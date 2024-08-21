from app import db, login_manager


class Admin(db.Model):
    username = db.Column(db.String(20), unique=True, primary_key=True,  nullable=False)
    password = db.Column(db.String(60), nullable=False)
    def __repr__(self):
        return f"Admin('{self.username}', '{self.password}')"

class Influencer(db.Model):
    
    email = db.Column(db.String(500), unique=True, nullable=False)
    name = db.Column(db.String(500), nullable=False)
    username = db.Column(db.String(20), unique=True, primary_key=True,  nullable=False)
    password = db.Column(db.String(60), nullable=False)
    niche = db.Column(db.String(500), nullable=False)
    reach = db.Column(db.Integer, nullable=False)
    image_url = db.Column(db.String(500), nullable=False)
    total_earning = db.Column(db.Integer, nullable=False, default=0)
    private_profile = db.Column(db.Boolean, default=False, nullable=False)

    def __repr__(self):
        return f"Influencer('{self.email}', '{self.name}', '{self.username}', '{self.password}', '{self.niche}', '{self.reach}', '{self.image_url}', '{self.private_profile}', '{self.total_earning}')"

class Sponsor(db.Model):

    email = db.Column(db.String(500),unique=True, nullable=False)
    company_name = db.Column(db.String(500), unique=True, nullable=False)
    username = db.Column(db.String(20),unique=True, primary_key=True,  nullable=False)
    password = db.Column(db.String(60), nullable=False)
    industry = db.Column(db.String(300), nullable=False)
    image_url = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"Sponsor('{self.email}', '{self.company_name}', '{self.username}', '{self.password}', '{self.industry}', '{self.image_url}')"
    

class Sponsor_campaigns(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_username = db.Column(db.String(20), db.ForeignKey('sponsor.username'), nullable=False)
    campaign_title = db.Column(db.String(500), nullable=False)
    campaign_description = db.Column(db.String(500), nullable=False)
    campaign_start_date = db.Column(db.String(100), nullable=False)
    campaign_end_date = db.Column(db.String(100), nullable=False)
    campaign_budget = db.Column(db.Integer, nullable=False)
    campaign_status = db.Column(db.String(500), nullable=False)
    campaign_niche = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f"Sponsor_campaigns('{self.id}', '{self.sponsor_username}', '{self.campaign_title}', '{self.campaign_description}', '{self.campaign_start_date}', '{self.campaign_end_date}', '{self.campaign_budget}', '{self.campaign_status}', '{self.campaign_niche}')"

class Ad_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_campaign_id = db.Column(db.Integer, db.ForeignKey('sponsor_campaigns.id'), nullable=False)
    sponsor_username = db.Column(db.String(20), db.ForeignKey('sponsor.username'), nullable=False)
    influencer_username = db.Column(db.String(20), db.ForeignKey('influencer.username'), nullable=False)
    ad_tile = db.Column(db.String(500), nullable=False)
    ad_description = db.Column(db.String(500), nullable=False)
    ad_niche = db.Column(db.String(500), nullable=False)
    ad_requirements = db.Column(db.String(500), nullable=False)
    ad_budget = db.Column(db.Integer, nullable=False)
    ad_negotiated_budget = db.Column(db.Integer, nullable=False, default=0)
    ad_status = db.Column(db.String(500), nullable=False, default="sent")

    def __repr__(self):
        return f"Ad_data('{self.id}', '{self.sponsor_campaign_id}', '{self.sponsor_username}', '{self.influencer_username}', '{self.ad_tile}', '{self.ad_description}', '{self.ad_niche}', '{self.ad_requirements}', '{self.ad_budget}', '{self.ad_status}', '{self.ad_negotiated_budget}')"