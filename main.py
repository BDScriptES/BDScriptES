from cliente import BotClient



bot = BotClient("!")


bot.nuevo_comando(nombre="etc",
                  tipo="$enviar",
               codigo="""
$var[o;1]
$var[n;$var[o]]
$if[$var[n]==1]
true
$endif

                  """)


bot.run("")