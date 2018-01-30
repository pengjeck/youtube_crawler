# coding:utf-8


class User:
    """
    obj
    """

    def __init__(self, user_id):
        self.user_id = user_id
        self.followers = -1
        self.nickname = ''
        self.avatar_path = ''
        self.avatar_url = ''
        self.des = ''

    def dump(self):
        """from insert a User object to database"""
        return (self.user_id, self.followers,
                self.nickname, self.avatar_path,
                self.avatar_url, self.des)
