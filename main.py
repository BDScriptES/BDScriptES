from cliente import BotClient



bot = BotClient("!")


bot.nuevo_comando(nombre="etc",
                  tipo="$enviar",
                  codigo="""
rol agregado
$roleGrant[+1343946570739220531;487430318500872203]

                  """)


bot.run("token")