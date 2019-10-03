

indentation = '   '


def format_image(filepath, caption='', width=None, height=None, scale=None):
    content = '\n.. image:: {}'.format(filepath)
    if width:
        content += '\n{}:width: {}'.format(indentation, width)
    if height:
        content += '\n{}:height: {}'.format(indentation, height)
    if scale:
        content += '\n{}:scale: {}'.format(indentation, scale)
    if caption:
        content += '\n{}{}'.format(indentation, caption)

    return content+'\n'

