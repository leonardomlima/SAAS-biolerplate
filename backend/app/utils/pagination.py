def paginate(items: list, page: int = 1, per_page: int = 20):
    start = (page - 1) * per_page
    return items[start : start + per_page]
