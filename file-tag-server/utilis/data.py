from utilis import system


def handle_return_data(msg="", data=None):
    if data:
        if data.get("code") == system.SUCCESS:
            return {"code": system.SUCCESS, "msg": f"{msg}{data.get('msg', '')}", "data": data.get("data", None)}
        else:  # 返回数据库异常
            return {"code": system.ERROR, "msg": f"{msg}{data.get('msg', '')}", "data": None}
    else:  # 处理其他类型的错误
        return {"code": system.ERROR, "msg": msg, "data": None}


def handle_query_data(code: int, msg: str, data=None):
    return {"code": code, "msg": msg, "data": data}


def get_datetime_formater(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")


mime_to_simple_type = {
    # 文档类型
    'application/pdf': '文档',
    'application/msword': '文档',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': '文档',
    'application/vnd.ms-excel': '文档',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': '文档',
    'application/vnd.ms-powerpoint': '文档',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': '文档',
    'application/rtf': '文档',
    'application/vnd.oasis.opendocument.text': '文档',
    'application/vnd.oasis.opendocument.spreadsheet': '文档',
    'application/vnd.oasis.opendocument.presentation': '文档',

    # 图片类型
    'image/jpeg': '图片',
    'image/png': '图片',
    'image/gif': '图片',
    'image/bmp': '图片',
    'image/tiff': '图片',
    'image/webp': '图片',
    'image/svg+xml': '图片',

    # 音频类型
    'audio/mpeg': '音频',
    'audio/wav': '音频',
    'audio/ogg': '音频',
    'audio/flac': '音频',
    'audio/aac': '音频',
    'audio/webm': '音频',

    # 视频类型
    'video/mp4': '视频',
    'video/x-msvideo': '视频',
    'video/x-matroska': '视频',
    'video/webm': '视频',
    'video/quicktime': '视频',
    'video/mpeg': '视频',

    # 文本类型
    'text/plain': '文本',
    'text/html': '文本',
    'text/css': '文本',
    'text/csv': '文本',
    'text/javascript': '文本',
    'application/json': '文本',
    'application/xml': '文本',

    # 压缩文件类型
    'application/zip': '压缩文件',
    'application/x-rar-compressed': '压缩文件',
    'application/x-7z-compressed': '压缩文件',
    'application/x-tar': '压缩文件',
    'application/gzip': '压缩文件',

    # 其他类型
    'application/octet-stream': '二进制文件',
    'application/x-shockwave-flash': 'Flash文件',
    'application/x-msdownload': '可执行文件',

    # 默认类型
    'default': '未知类型'
}