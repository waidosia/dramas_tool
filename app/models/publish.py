from app.extension import db

class Publish(db.Model):
    __tablename__ = 'publish_history'
    # 列
    id = db.Column(db.Integer, primary_key=True)
    cn_name = db.Column(db.String(100), nullable=False)
    en_name = db.Column(db.String(100), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    season =db.Column(db.Integer, nullable=False)
    film_source = db.Column(db.String(100), nullable=False)
    source = db.Column(db.String(100), nullable=False)
    team =db.Column(db.String(100), nullable=False)
    cover = db.Column(db.String(100), nullable=False)
    pt_gen = db.Column(db.String(100), nullable=False)
    introduction = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    main_title = db.Column(db.String(100), nullable=False)
    sub_title = db.Column(db.String(100), nullable=False)
    torrent_path = db.Column(db.String(100), nullable=False)
    torrent = db.Column(db.LargeBinary, nullable=False)
    screenshot1_link =db.Column(db.String(100), nullable=False)
    screenshot2_link =db.Column(db.String(100), nullable=False)
    screenshot3_link =db.Column(db.String(100), nullable=False)
    screenshot4_link =db.Column(db.String(100), nullable=False)
    screenshot5_link =db.Column(db.String(100), nullable=False)
    video_screenshot_link =db.Column(db.String(100), nullable=False)
    publish_info =db.Column(db.String(100), nullable=False)
    mediaInfo =db.Column(db.String(100), nullable=False)
    first_file_name = db.Column(db.String(100), nullable=False)
    resolution = db.Column(db.String(100), nullable=False)
    video_codec = db.Column(db.String(100), nullable=False)
    audio_codec = db.Column(db.String(100), nullable=False)
    sites = db.relationship("PublishForSite", backref="publish", lazy="joined")
    downloaders = db.relationship("PublishForDownloader", backref="publish", lazy="joined")


    def to_dict(self):
        return {
        'id': self.id,
        'cnName': self.cn_name,
        'enName': self.en_name,
        'year': self.year,
        'season': self.season,
        'filmSource':  self.film_source,
        'source':  self.source,
        'team':  self.team,
        'cover': self.cover,
        'ptGen':  self.pt_gen,
        'introduction':  self.introduction,
        'category':  self.category,
        'mainTitle': self.main_title,
        'subTitle': self.sub_title,
        'torrentPath': self.torrent_path,
        'screenshot1_link': self.screenshot1_link,
        'screenshot2_link': self.screenshot2_link,
        'screenshot3_link': self.screenshot3_link,
        'screenshot4_link': self.screenshot4_link,
        'screenshot5_link': self.screenshot5_link,
        'videoScreenshotLink': self.video_screenshot_link,
        'publishInfo': self.publish_info,
        'mediaInfo':  self.mediaInfo,
        'firstFileName': self.first_file_name,
        'sites': [site.to_dict() for site in self.sites],
        'downloaders': [downloader.to_dict() for downloader in self.downloaders]
        }



class PublishForSite(db.Model):
    __tablename__ = 'publish_by_site'
    id = db.Column(db.Integer, primary_key=True)
    publish_id = db.Column(db.Integer, db.ForeignKey('publish_history.id'), nullable=False)
    site_type = db.Column(db.Integer,nullable=False)
    status = db.Column(db.Integer,nullable=False)
    error_msg= db.Column(db.String(100), nullable=False)
    torrent_id=db.Column(db.Integer,nullable=False)


    def to_dict(self):
        return {
            'id': self.id,
            'publish_id': self.publish_id,
            'site_type': self.site_type,
            'status': self.status,
            'error_msg': self.error_msg,
            'torrent_id': self.torrent_id,
        }



class PublishForDownloader(db.Model):
    __tablename__ = 'publish_by_downloader'
    id = db.Column(db.Integer, primary_key=True)
    publish_id = db.Column(db.Integer, db.ForeignKey('publish_history.id'), nullable=False)
    site_type = db.Column(db.Integer, nullable=False)
    status = db.Column(db.Integer, nullable=False)
    error_msg = db.Column(db.String(100), nullable=False)
    downloader_id = db.Column(db.Integer,nullable=False)
    torrent_hash=db.Column(db.String(100),nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'publish_id': self.publish_id,
            'site_type': self.site_type,
            'status': self.status,
            'error_msg': self.error_msg,
            'downloader_type': self.downloader_id,
            'torrent_hash': self.torrent_hash,
        }