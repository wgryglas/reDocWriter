

def generate_variables(templateDest):
    from os.path import basename
    from datetime import datetime
    return {
        'now': datetime.today().strftime('%Y-%m-%d %H:%M'),
        'fileBaseName': basename(templateDest).split('.')[0],
        'filePath': templateDest,
        'fileName': basename(templateDest)
    }


def emptyFileTemplate():
    return """
    -------------------
    Main Title
    -------------------
    :date: {now}
    :modified: {now}
    :tags: some, tags, for, your, text
    :category: nice
    :slug: {fileName}
    :authors: Your Name
    :summary: Short version for index and feeds
    """