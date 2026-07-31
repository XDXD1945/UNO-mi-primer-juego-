const mineflayer = require('mineflayer');
const { pathfinder, Movements, goals } = require('mineflayer-pathfinder');
const collectBlock = require('mineflayer-collectblock').plugin;
const { OpenAI } = require('openai');

// Configuración de la IA - Optimizada para velocidad
const openai = new OpenAI({
  apiKey: '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',
  baseURL: 'https://integrate.api.nvidia.com/v1',
  timeout: 15000,
});

const bot = mineflayer.createBot({
  host: 'waryfish.aternos.host',
  port: 57744,
  username: 'Mika',
  version: '1.21.11',
  checkTimeoutInterval: 60 * 1000
});

bot.loadPlugin(pathfinder);
bot.loadPlugin(collectBlock);

let listoParaHablar = false;
let memoriaComprimida = "Sin historia previa.";
let historialCorto = []; // Máximo 4 interacciones para no saturar tokens

bot.once('spawn', () => {
  console.log('⚡ Mika V4 Iniciada - Arquitectura Function Calling');
  try {
    const mcData = require('minecraft-data')(bot.version);
    bot.pathfinder.setMovements(new Movements(bot, mcData));
  } catch (e) {}
  setTimeout(() => { listoParaHablar = true; console.log('⚡ Lista para operar.'); }, 3000);
});

// Auto-equipamiento mejorado (Incluye Elytras)
bot.on('playerCollect', async (collector) => {
  if (collector.username !== bot.username) return;
  setTimeout(async () => {
    for (const item of bot.inventory.items()) {
      try {
        if (item.name.includes('helmet')) await bot.equip(item, 'head');
        if (item.name.includes('chestplate') || item.name.includes('elytra')) await bot.equip(item, 'torso');
        if (item.name.includes('leggings')) await bot.equip(item, 'legs');
        if (item.name.includes('boots')) await bot.equip(item, 'feet');
        if (item.name.includes('sword')) await bot.equip(item, 'hand');
      } catch (err) {}
    }
  }, 500);
});

// Estado Ultra-Comprimido
function getState() {
  const p = bot.entity.position;
  const target = bot.nearestEntity(e => e.type === 'player');
  const bed = bot.findBlock({ matching: b => b.name.includes('bed'), maxDistance: 4 });
  
  let s = `HP:${Math.round(bot.health)} FD:${Math.round(bot.food)} POS:${Math.round(p.x)},${Math.round(p.y)},${Math.round(p.z)}`;
  if (target) s += ` NEAR:${target.username}`;
  if (bed) s += ` BED:YES`;
  return s;
}

// Compresión de memoria en segundo plano
async function compressMemory() {
  if (historialCorto.length < 5) return;
  console.log('-> Comprimiendo memoria...');
  try {
    const prompt = `Resume en 1 oración la memoria clave (acuerdos, intenciones, lugares):
Memoria vieja: ${memoriaComprimida}
Nuevos mensajes:\n${historialCorto.map(m => `${m.role}: ${m.content}`).join('\n')}`;

    const res = await openai.chat.completions.create({
      model: "meta/llama-3.1-8b-instruct",
      messages: [{ role: "user", content: prompt }],
      max_tokens: 50,
    });
    memoriaComprimida = res.choices[0].message.content;
    historialCorto = []; 
  } catch (err) {}
}

// Menú de Habilidades (Tools) para la IA
const herramientas = [
  {
    type: "function",
    function: {
      name: "hablar",
      description: "Envía un mensaje de chat al jugador.",
      parameters: { type: "object", properties: { texto: { type: "string", description: "Lo que Mika dirá" } }, required: ["texto"] }
    }
  },
  {
    type: "function",
    function: {
      name: "seguir",
      description: "Camina hacia un jugador específico.",
      parameters: { type: "object", properties: { objetivo: { type: "string" } }, required: ["objetivo"] }
    }
  },
  {
    type: "function",
    function: { name: "parar_movimiento", description: "Detiene cualquier movimiento actual de Mika.", parameters: { type: "object", properties: {} } }
  },
  {
    type: "function",
    function: { name: "dormir", description: "Se acuesta en una cama cercana si hay una disponible.", parameters: { type: "object", properties: {} } }
  },
  {
    type: "function",
    function: {
      name: "enviar_comando",
      description: "Ejecuta un comando en el servidor (ej. /tpa Ursscccp)",
      parameters: { type: "object", properties: { comando: { type: "string" } }, required: ["comando"] }
    }
  }
];

// Procesador de Decisiones
async function pensar(usuario, mensaje) {
  historialCorto.push({ role: "user", content: `${usuario}:${mensaje}` });

  const sysPrompt = `Eres Mika, jugadora de Minecraft. Usa las herramientas (tools) para actuar y hablar.
ESTADO: ${getState()}
MEMORIA: ${memoriaComprimida}`;

  try {
    const res = await openai.chat.completions.create({
      model: "meta/llama-3.1-8b-instruct",
      messages: [ { role: "system", content: sysPrompt }, ...historialCorto ],
      tools: herramientas,
      tool_choice: "auto", // Permite a la IA decidir qué función usar
      temperature: 0.2,
      max_tokens: 150,
    });

    const msgIA = res.choices[0].message;
    
    // Si la IA decidió usar herramientas (Functions)
    if (msgIA.tool_calls) {
      for (const call of msgIA.tool_calls) {
        const args = JSON.parse(call.function.arguments);
        const fnName = call.function.name;

        if (fnName === "hablar") {
          bot.chat(args.texto);
          historialCorto.push({ role: "assistant", content: args.texto });
        }
        if (fnName === "seguir") {
          const target = bot.players[args.objetivo]?.entity;
          if (target) bot.pathfinder.setGoal(new goals.GoalFollow(target, 2), true);
        }
        if (fnName === "parar_movimiento") bot.pathfinder.setGoal(null);
        if (fnName === "dormir") {
          const bed = bot.findBlock({ matching: b => b.name.includes('bed'), maxDistance: 4 });
          if (bed) bot.sleep(bed).catch(()=>{});
        }
        if (fnName === "enviar_comando") bot.chat(args.comando);
      }
    } else if (msgIA.content) {
      // Si la IA respondió solo con texto por alguna razón
      bot.chat(msgIA.content);
      historialCorto.push({ role: "assistant", content: msgIA.content });
    }

    compressMemory(); // Verifica si debe comprimir
  } catch (err) {
    console.log("Error de IA:", err.message);
  }
}

bot.on('chat', (username, message) => {
  if (!listoParaHablar || username === bot.username) return;
  const msgL = message.toLowerCase();
  if (msgL.includes('mika') || username === 'Ursscccp') {
    pensar(username, message);
  }
});

bot.on('error', err => console.log('Err:', err.message));
bot.on('end', () => console.log('Desconectada.'));
