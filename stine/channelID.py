def execute(code, ctx, args):
    """
    Reemplaza $channelID con el ID del canal donde se ejecuta el comando.
    """
    return code.replace("$channelID", str(ctx.channel.id))