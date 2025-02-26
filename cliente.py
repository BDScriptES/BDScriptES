import discord
from discord.ext import commands
import os
import importlib
from utils.handler_error import handle_error  # Manejador de errores
from stine.conditions import execute as execute_conditions  # Motor de condiciones


class BotClient(commands.Bot):
    def __init__(self, command_prefix):
        super().__init__(command_prefix=command_prefix if isinstance(command_prefix, list) else [command_prefix], intents=discord.Intents().all())
        self.commands_registry = {}
        self.function_handlers = {}
        self.load_functions()

    def load_functions(self):
        folder = "stine"
        for filename in os.listdir(folder):
            if filename.endswith(".py"):
                module_name = f"{folder}.{filename[:-3]}"
                module = importlib.import_module(module_name)
                self.function_handlers[filename[:-3]] = module

    def nuevo_comando(self, nombre, tipo, codigo, alias=None):
        self.commands_registry[nombre] = {"tipo": tipo, "codigo": codigo, "alias": alias or []}

        async def command_function(ctx, *args):
            try:
                await self.ejecutar_comando(ctx, nombre, *args)
            except Exception as e:
                await handle_error(ctx, e)

        command_function = commands.Command(command_function, name=nombre, aliases=alias or [])
        self.add_command(command_function)

    async def ejecutar_comando(self, ctx, nombre, *args):
        print("Arg:", args)
        try:
            if nombre in self.commands_registry:
                comando = self.commands_registry[nombre]
                codigo = comando["codigo"]

                print(f"Procesando código: {codigo}")  # Debug

                # 🔹 **Ejecutar condiciones primero**
                codigo = execute_conditions(codigo, ctx)

                if comando["tipo"] == "$enviar":
                    embeds = {}

                    # 🔹 **Procesar `$loop` primero**
                    if "loop" in self.function_handlers:
                        loop_module = self.function_handlers["loop"]
                        if hasattr(loop_module, "execute"):
                            prev_codigo = None
                            contador = 0  # Seguridad para evitar bucle infinito

                            while "$loop[" in codigo and prev_codigo != codigo:
                                prev_codigo = codigo
                                codigo = loop_module.execute(codigo)

                                contador += 1
                                print(f"Iteración {contador} - Resultado de loop: {codigo}")  # Debug

                                if contador > 100:
                                    print("⚠️ Se alcanzó el límite de iteraciones del loop.")
                                    break

                    # 🔹 **Procesar otras funciones después**
                    for func_name, module in self.function_handlers.items():
                        if func_name in ["loop", "conditions"]:  # Ya se procesó
                            continue

                        if hasattr(module, "execute"):
                            prev_codigo = None

                            # 🔹 **Procesar funciones sin `[` (como `$guildID`)**
                            while f"${func_name}" in codigo and f"${func_name}[" not in codigo:
                                resultado = module.execute(codigo, ctx, args)
                                if resultado:
                                    codigo = resultado  # Reemplazamos directamente


                            # 🔹 **Procesar funciones con `[` primero**
                            while f"${func_name}[" in codigo and prev_codigo != codigo:
                                prev_codigo = codigo
                                resultado = module.execute(codigo, ctx, args)

                                if resultado:
                                    if isinstance(resultado, str):
                                        codigo = resultado  # Reemplazamos el código
                                    else:
                                        for res in resultado:
                                            text, index = res if isinstance(res, tuple) else (res, 1)
                                            index = int(index) if index else 1
                                            if index not in embeds:
                                                embeds[index] = discord.Embed()

                                            # Procesamiento de embeds
                                            if func_name == "title":
                                                embeds[index].title = text
                                            elif func_name == "description":
                                                embeds[index].description = text
                                            elif func_name == "addField":
                                                name, value, inline, idx = text.split(';')
                                                inline = inline.lower() == 'true'
                                                idx = int(idx) if idx else 1
                                                embeds[idx].add_field(name=name, value=value, inline=inline)
                                            elif func_name == "thumbnail":
                                                embeds[index].set_thumbnail(url=text)
                                            elif func_name == "footer":
                                                embeds[index].set_footer(text=text)
                                            elif func_name == "footerIcon":
                                                embeds[index].set_footer(icon_url=text)
                                            elif func_name == "image":
                                                embeds[index].set_image(url=text)
                                            elif func_name == "author":
                                                name, icon_url, url = text.split(';')
                                                embeds[index].set_author(name=name, icon_url=icon_url, url=url)
                                            elif func_name == "color":
                                                embeds[index].color = discord.Color(int(text.lstrip('#'), 16))


                    # 🔹 **Enviar los embeds generados**
                    if embeds:
                        for index in sorted(embeds.keys()):
                            embed = embeds[index]
                            await ctx.send(embed=embed)

                    # 🔹 **Enviar texto fuera de embeds**
                    if codigo.strip() and not any(f"${func_name}[" in codigo for func_name in self.function_handlers):
                        await ctx.send(codigo)

        except Exception as e:
            await handle_error(ctx, e)  # Captura cualquier error y lo maneja

    async def on_ready(self):
        print(f"✅ Bot conectado como {self.user}")
