from app.extension import db


class ImageHost(db.Model):
    # 表名
    __tablename__ = 'image_host'
    # 列
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    key_or_cookie = db.Column(db.String(255))
    is_available = db.Column(db.Boolean, default=True)
    is_proxy = db.Column(db.Boolean, default=False)
    def __repr__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'key_or_cookie': self.key_or_cookie,
            'is_available': self.is_available,
            'is_proxy': self.is_proxy,
        }

class Downloader(db.Model):
    __tablename__ = 'downloader'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    url = db.Column(db.String(255), nullable=False)
    user = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    seeding_path = db.Column(db.String(255))

    def __repr__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'url': self.url,
            'user': self.user,
            'password': self.password,
            'seeding_path': self.seeding_path
        }

class Site(db.Model):
    __tablename__ = 'site'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.Integer, nullable=False,unique= True )
    cookie = db.Column(db.String(255), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    def __repr__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'cookie': self.cookie,
            'is_available': self.is_available
        }


class Screenshot(db.Model):
    __tablename__ = 'screenshot'
    id = db.Column(db.Integer, primary_key=True)
    dir = db.Column(db.String(255), nullable=False)
    num = db.Column(db.Integer, nullable=False)
    complexity = db.Column(db.Float, nullable=False)
    is_thumbnail = db.Column(db.Boolean, nullable=False)
    thumbnail_horizontal = db.Column(db.Integer, nullable=False)
    thumbnail_vertical = db.Column(db.Integer, nullable=False)
    starting_point = db.Column(db.Float, nullable=False)
    end_point = db.Column(db.Float, nullable=False)
    auto_upload = db.Column(db.Boolean, nullable=False)
    del_local_img = db.Column(db.Boolean, nullable=False)
    def __repr__(self):
        return self.dir

    def to_dict(self):
        return {
            'id': self.id,
            'dir': self.dir,
            'num': self.num,
            'complexity': self.complexity,
            'is_thumbnail': self.is_thumbnail,
            'thumbnail_horizontal': self.thumbnail_horizontal,
            'thumbnail_vertical': self.thumbnail_vertical,
            'starting_point': self.starting_point,
            'end_point': self.end_point,
            'auto_upload': self.auto_upload,
            'del_local_img': self.del_local_img
        }


class PtGen(db.Model):
    __tablename__ = 'pt_gen'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    is_available = db.Column(db.Boolean, default=True)
    def __repr__(self):
        return self.name

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'url': self.url,
            'is_available': self.is_available
        }


class Config(db.Model):
    __tablename__ = 'configuration'
    id = db.Column(db.Integer, primary_key=True)
    image_host_id = db.Column(db.Integer, db.ForeignKey('image_host.id'), nullable=False)
    pt_gen_id = db.Column(db.Integer, db.ForeignKey('pt_gen.id'), nullable=False)
    screenshot_id = db.Column(db.Integer, db.ForeignKey('screenshot.id'), nullable=False)
    downloader_id = db.Column(db.Integer, db.ForeignKey('downloader.id'), nullable=False)
    is_transfer = db.Column(db.Boolean, nullable=False)
    transfer_dir = db.Column(db.String(255), nullable=False)
    proxy_url = db.Column(db.String(255), nullable=False)
    torrent_path = db.Column(db.String(255), nullable=False)
    def __repr__(self):
        return self.id

    def to_dict(self):
        return {
            'id': self.id,
            'image_host_id': self.image_host_id,
            'pt_gen_id': self.pt_gen_id,
            'screenshot_id': self.screenshot_id,
            'downloader_id': self.downloader_id,
            'is_transfer': self.is_transfer,
            'transfer_dir': self.transfer_dir,
            'proxy_url': self.proxy_url,
            'torrent_path': self.torrent_path
        }
