from flask import Flask, render_template, request, flash, redirect, url_for, session, make_response
import os
from app import create_app, db
from models import Sponsor, Influencer, Sponsor_campaigns, Ad_data, Admin
from functools import wraps
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
import warnings

app = create_app()

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            flash('Please log in to access this page', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.after_request
def add_header(response):
    
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/register")
def register():
    return render_template("register.html", title="Sign Up")

@app.route("/influencer_register")
def influencer_register():
    return render_template("influencer_register.html", title="Influencer Sign Up")

@app.route("/admin")
def admin():
    return render_template("admin_home.html", title="Admin Home")
    
@app.route("/admin_register", methods=["POST", "GET"])
def admin_register():
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']
        query_data = Admin(username=username, password=password)
        db.session.add(query_data)
        db.session.commit()
        print(Sponsor.query.all())
        flash('Register', 'success')
        return redirect(url_for('admin_login'))
    flash('Not Register', 'danger')
    return render_template("admin_register.html", title="Admin Register")

@app.route("/admin_login", methods=["POST", "GET"])
def admin_login():
    if request.method=="POST":
        username = request.form['username']
        password = request.form['password']
        
        # Check in Influencer table
        admin = Admin.query.filter_by(username=username).first()
        if admin and admin.password == password:
            session['username'] = username
            session['role'] = 'admin'
            return redirect(url_for('admin_dashboard', username=username))
    flash("Not Correct", 'danger')
    return render_template("admin_login.html", title="Login")

@app.route("/admin_dashboard/<username>", methods=["POST", "GET"])
def admin_dashboard(username):
    influencer_data = Influencer.query.all()
    sponsor_data = Sponsor.query.all()
    return render_template("admin_dashboard.html", title="Admin Dashboard", username=username, influencer_data=influencer_data, sponsor_data=sponsor_data)

@app.route("/admin_influencer_stats/<username>", methods=["POST", "GET"])
def admin_influencer_stats(username):
    data = Influencer.query.filter_by(username=username).first()
    ad_data = Ad_data.query.filter_by(influencer_username=username).all()
    completed_ad = 0
    total_ad = len(ad_data)
    for ads in ad_data:
        if ads.ad_status == 'Completed':
            completed_ad += 1
    remaining_ad = total_ad - completed_ad
    categories = ['Completed Ads', 'Remaining Ads']
    ad_counts = [completed_ad, remaining_ad]
    plt.bar(categories, ad_counts, color=['green', 'yellow'])
    plt.ylabel('Number of Ads')
    plt.ylim(0, total_ad + 1)
    plt.yticks(range(0, total_ad+1, 1))
    plt.xlabel('Ad Status')
    plt.title('Completed vs Remaining Ads')
    graph_path = f"graphs/stats_{username}"
    plt.savefig(os.path.join(app.static_folder, graph_path))
    plt.clf()
    # plt.savefig("/static/graphs/stats_{username}.png")
    return render_template("admin_influencer_stats.html", title="Influencer Stats", data=data, username=username, ad_data=ad_data, completed_ad=completed_ad, total_ad=total_ad, remaining_ad=remaining_ad)

@app.route("/admin_sposnor_stats/<username>", methods=["POST", "GET"])
def admin_sponsor_stats(username):
    data = Sponsor.query.filter_by(username=username).first()
    campaign_data = Sponsor_campaigns.query.filter_by(sponsor_username=username).all()
    total_campaign = len(campaign_data)
    ad_data = Ad_data.query.filter_by(sponsor_username=username).all()
    completed_ad = 0
    total_ad = len(ad_data)
    for ads in ad_data:
        if ads.ad_status == 'Completed':
            completed_ad += 1
    remaining_ad = total_ad - completed_ad
    categories = ['Completed Ads', 'Remaining Ads']
    ad_counts = [completed_ad, remaining_ad]
    plt.bar(categories, ad_counts, color=['green', 'yellow'])
    plt.ylabel('Number of Ads')
    plt.ylim(0, total_ad + 1)
    plt.yticks(range(0, total_ad+1, 1))
    plt.xlabel('Ad Status')
    plt.title('Completed vs Remaining Ads')
    graph_path = f"graphs/stats_{username}"
    plt.savefig(os.path.join(app.static_folder, graph_path))
    plt.clf()
    return render_template("admin_sponsor_stats.html", title="Sponsor Stats", username=username, total_campaign=total_campaign, total_ad=total_ad, completed_ad = completed_ad, remaining_ad=remaining_ad, data=data, ad_data=ad_data)

@app.route("/admin_delete_influencer/<username>", methods=["POST", "GET"])
def delete_influencer(username):
    influencer = Influencer.query.filter_by(username=username).first()
    if influencer:
        db.session.delete(influencer)
        db.session.commit()
        flash('Influencer deleted successfully', 'success')
        return redirect(url_for('admin_dashboard', username=username))
    flash('Influencer not found', 'danger')
    return redirect(url_for('admin_dashboard', username=username))
    
@app.route("/admin_delete_sponsor/<username>", methods=["POST", "GET"])
def delete_sponsor(username):
    sponsor = Sponsor.query.filter_by(username=username).first()
    if sponsor:
        db.session.delete(sponsor)
        db.session.commit()
        flash('sponosr deleted successfully', 'success')
        return redirect(url_for('admin_dashboard', username=username))
    flash('sponsor not found', 'danger')
    return redirect(url_for('admin_dashboard', username=username))

@app.route("/admin_logout")
def admin_logout():
    session.clear()  # Clear all session data
    return redirect(url_for('admin'))

@app.route("/sponsor_register")
def sponsor_register():
    return render_template("sponsor_register.html", title="Sponsor Sign Up")

@app.route("/influencer_dashboard/<username>", methods=['POST', 'GET'])
@login_required
def influencer_dashboard(username):
    influencer = Influencer.query.filter_by(username=username).first()
    if influencer:
        niches = influencer.niche.strip('[]').replace("'", "").split(', ')
        print(niches)
        data = {
            'email': influencer.email,
            'name': influencer.name,
            'username': influencer.username,
            'password': influencer.password,
            'niche': influencer.niche,
            'reach': influencer.reach,
            'photo_url': influencer.image_url,
            'total_earning': influencer.total_earning,
        }
        data['private_profile']=False
        if request.method == 'POST':
            if 'private' in request.form:
                influencer.private_profile = True
                db.session.commit()
                print(Influencer.query.all())
                data['private_profile']=True
            if 'public' in request.form:
                influencer.private_profile = False
                db.session.commit()
                print(Influencer.query.all())
                data['private_profile']=False
        ad_data_list = Ad_data.query.filter_by(influencer_username=username).all()
        return render_template("influencer_dashboard.html", title="Influencer Dashboard", data=data, public=True, ad_data_list = ad_data_list, username=username)
    flash('Influencer not found', 'danger')
    return redirect(url_for('login'))

@app.route("/influencer_view_ad/<username>/<int:ad_id>")
def influencer_view_ad(username, ad_id):
    data = Influencer.query.filter_by(username=username).first()
    ad_data = Ad_data.query.filter_by(id=ad_id).first()
    return render_template("influencer_view_ad.html", title="View Ad", ad_data=ad_data, data=data, username=username)

@app.route("/influencer_view_accepted_ad/<username>/<int:ad_id>", methods=["POST", "GET"])
def influencer_view_accepted_ad(username, ad_id):
    ad_data = Ad_data.query.filter_by(id=ad_id).first()
    data = Influencer.query.filter_by(username=username).first()
    return render_template("influencer_view_accepted_ad.html", title = "View Accepted Ad", ad_data=ad_data, data=data, username=username)

@app.route("/influencer_view_ad/decision_ad/<username>/<int:ad_id>", methods=["POST", "GET"])
def influencer_decision_ad(username, ad_id):
    ad_data = Ad_data.query.filter_by(id=ad_id).first()
    print(request.form.keys())
    if request.method=="POST":
        if 'negotiated_budget' in request.form.keys():
            negotiated_budget = request.form['negotiated_budget']
            ad_data.ad_negotiated_budget = negotiated_budget
            ad_data.ad_status = 'Negotiation'
            db.session.commit()
            flash('Negotiation started', 'success')
        if 'change_status' in request.form.keys():
            if request.form['change_status'] == 'Accepted':
                ad_data.ad_status = 'Accepted'
                db.session.commit()
                flash('Request Acepted', 'success')
        if 'change_status' in request.form.keys():
            if request.form['change_status'] == 'Rejected':
                ad_data.ad_status = 'Rejected'
                db.session.commit()
                flash('Request Rejected', 'danger')
        if 'change_status' in request.form.keys():
            if request.form['change_status'] == 'Completed':
                ad_data.ad_status = 'Completed'
                influencer_username = Ad_data.query.filter_by(id=ad_id).first().influencer_username
                influencer = Influencer.query.filter_by(username=influencer_username).first()
                if ad_data.ad_negotiated_budget != 0:
                    influencer.total_earning += ad_data.ad_negotiated_budget
                else:
                    influencer.total_earning += ad_data.ad_budget
                db.session.commit()
                flash('Request Completed', 'success')
        if 'change_status' in request.form.keys():
            if request.form['change_status'] == 'Requested':
                ad_data.ad_status = 'Requested'
                ad_data.influencer_username = username
                db.session.commit()
                flash('Request Sent', 'success')
    return redirect(url_for('influencer_dashboard', username=username))

@app.route("/influencer_view_completed_ad/<username>/<int:ad_id>", methods=["POST", "GET"])
def influencer_view_completed_ad(username, ad_id):
    ad_data = Ad_data.query.filter_by(id=ad_id).first()
    data = Influencer.query.filter_by(username=username).first()
    return render_template("influencer_view_completed_ad.html", title = "View Accepted Ad", ad_data=ad_data, data=data)

@app.route("/influencer_find/<username>", methods = ["POST", "GET"])
def influencer_find(username):
    data = Influencer.query.filter_by(username=username).first()
    subquery = db.session.query(Ad_data.sponsor_campaign_id).filter_by(influencer_username=username).subquery()
    assigned_campaigns = Sponsor_campaigns.query.filter(Sponsor_campaigns.id.in_(subquery)).all()
    other_subquery = db.session.query(Ad_data.sponsor_campaign_id).filter_by(influencer_username="").subquery()
    other_campaigns = Sponsor_campaigns.query.filter(Sponsor_campaigns.id.in_(other_subquery)).all()
    print(assigned_campaigns)
    print(1)
    print(other_campaigns)
    return render_template("influencer_find.html", title="Find Campaigns", assigned_campaigns=assigned_campaigns, other_campaigns=other_campaigns, username=username, data=data)

@app.route("/influencer_find/<username>/search/", methods=["POST", "GET"])
def influencer_search(username):
    data = Influencer.query.filter_by(username=username).first()
    if request.method=="POST":
            if request.form['search_username'] and request.form['search_campaign'] == "":
                sponsor_data = Sponsor_campaigns.query.filter(Sponsor_campaigns.sponsor_username==request.form['search_username'], Sponsor_campaigns.campaign_status=='public').all()
                print(sponsor_data)
                if sponsor_data == None:
                    flash('Please enter a valid search query', 'danger')  
                    return redirect(url_for('influencer_find', username=username))
            elif request.form['search_username'] == "" and request.form['search_campaign']:
                sponsor_data = Sponsor_campaigns.query.filter(Sponsor_campaigns.campaign_title==request.form['search_campaign'], Sponsor_campaigns.campaign_status=='public').all()
                print(sponsor_data)
                if sponsor_data == None:
                    flash('Please enter a valid search query', 'danger')  
                    return redirect(url_for('influencer_find', username=username))
            elif request.form['search_username'] != "" and request.form['search_campaign']:
                sponsor_data = Sponsor_campaigns.query.filter(Sponsor_campaigns.sponsor_username==request.form['search_username'], Sponsor_campaigns.campaign_title==request.form['search_campaign'], Sponsor_campaigns.campaign_status=='public').all()
                if sponsor_data == None:
                    flash('Please enter a valid search query', 'danger')  
                    return redirect(url_for('influencer_find', username=username))
            else:
                flash('Please enter a valid search query', 'danger')  
                return redirect(url_for('influencer_find', username=username))
            return render_template("influencer_search_result.html", title="Search Result", data=data, sponsor_data=sponsor_data)

@app.route("/influencer_view_campaign/<username>/<int:campaign_id>/", methods = ["POST", "GET"])
def influencer_view_campaign(username, campaign_id):
    data = Influencer.query.filter_by(username=username).first()
    campaign_data = Sponsor_campaigns.query.filter_by(id=campaign_id).first()
    ad_data_list = Ad_data.query.filter_by(sponsor_campaign_id=campaign_id).all()
    return render_template("influencer_view_campaign.html", title="View Campaign", username=username, data=data, campaign_data=campaign_data, ad_data_list=ad_data_list)

@app.route("/influencer_stats/<username>", methods=["POST", "GET"])
def influencer_stats(username):
    data = Influencer.query.filter_by(username=username).first()
    ad_data = Ad_data.query.filter_by(influencer_username=username).all()
    completed_ad = 0
    total_ad = len(ad_data)
    for ads in ad_data:
        if ads.ad_status == 'Completed':
            completed_ad += 1
    remaining_ad = total_ad - completed_ad
    categories = ['Completed Ads', 'Remaining Ads']
    ad_counts = [completed_ad, remaining_ad]
    plt.bar(categories, ad_counts, color=['green', 'yellow'])
    plt.ylabel('Number of Ads')
    plt.ylim(0, total_ad + 1)
    plt.yticks(range(0, total_ad+1, 1))
    plt.xlabel('Ad Status')
    plt.title('Completed vs Remaining Ads')
    graph_path = f"graphs/stats_{username}"
    plt.savefig(os.path.join(app.static_folder, graph_path))
    plt.clf()
    # plt.savefig("/static/graphs/stats_{username}.png")
    return render_template("influencer_stats.html", title="Influencer Stats", data=data, username=username, ad_data=ad_data, completed_ad=completed_ad, total_ad=total_ad, remaining_ad=remaining_ad)

@app.route("/sponsor_dashboard/<username>")
@login_required
def sponsor_dashboard(username):
    sponsor = Sponsor.query.filter_by(username=username).first()
    if sponsor:
        data = {
            'email': sponsor.email,
            'companyName': sponsor.company_name,
            'username': sponsor.username,
            'password': sponsor.password,
            'industry': sponsor.industry,
            'photo_url': sponsor.image_url
        }
        return render_template("sponsor_dashboard.html", title="Sponsor Dashboard", data=data, username=username)
    flash('Sponsor not found', 'danger')
    return redirect(url_for('login'))
    
@app.route("/sposnor_campaigns/<username>")
@login_required
def sponsor_campaigns(username):
    sponsor = Sponsor.query.filter_by(username=username).first()
    if sponsor:
        data = {
            'email': sponsor.email,
            'companyName': sponsor.company_name,
            'username': sponsor.username,
            'password': sponsor.password,
            'industry': sponsor.industry,
            'photo_url': sponsor.image_url
        }
        campaign_list = []
        campaigns_query=Sponsor_campaigns.query.all()
        for campaign in campaigns_query:
            campaign_dict = {
                'sponsor_username': campaign.sponsor_username,
                'campaign_id': campaign.id,
                'campaign_title': campaign.campaign_title,
                'campaign_description': campaign.campaign_description,
                'campaign_start_date': campaign.campaign_start_date,
                'campaign_end_date': campaign.campaign_end_date,
                'campaign_budget': campaign.campaign_budget,
                'campaign_status': campaign.campaign_status,
                'campaign_niche': campaign.campaign_niche,
            }
            campaign_list.append(campaign_dict)

        return render_template("sponsor_campaigns.html", title="Sponsor Campaigns", data=data, campaign_list=campaign_list, username=username)
    flash('Sponsor not found', 'danger')
    return redirect(url_for('login'))

@app.route("/add_campaigns/<username>", methods=["POST", "GET"])
def add_campaigns(username):
    return render_template("add_campaigns.html", title="Add Campaigns", username=username)

@app.route("/campaigns_data/<username>", methods=['POST', 'GET'])
def campaigns_data(username):
    if request.method=='POST':
        sponsor_username = username
        campaign_title = request.form['title']
        campaign_description = request.form['description']
        campaign_start_date = request.form['start_date']
        campaign_end_date = request.form['end_date']
        campaign_budget = int(request.form['budget'])
        campaign_status = request.form['visibility']
        niche_all = request.form['niche']
        niche = list(niche_all.split(','))
        campaign_niche = ' '.join([str(elem).lower() for elem in niche])
        query_data = Sponsor_campaigns(sponsor_username=sponsor_username, campaign_title=campaign_title, campaign_description=campaign_description, campaign_start_date=campaign_start_date, campaign_end_date=campaign_end_date, campaign_budget=campaign_budget, campaign_status=campaign_status, campaign_niche=campaign_niche)
        db.session.add(query_data)
        db.session.commit()
        print(Sponsor_campaigns.query.all())
        
        flash('Campaign added successfully', 'success')
    return redirect(url_for('sponsor_campaigns', username=username))

@app.route("/view_campaign/<username>/<int:campaign_id>", methods=['POST', 'GET'])
def view_campaign(username, campaign_id=None):
    if request.method=="POST":
        campaign_id = request.form['campaign_id']
        campaign = Sponsor_campaigns.query.filter_by(id=campaign_id).first()
        if campaign:
            data = {
                'campaign_id': campaign.id,
                'sponsor_username': campaign.sponsor_username,
                'campaign_title': campaign.campaign_title,
                'campaign_description': campaign.campaign_description,
                'campaign_start_date': campaign.campaign_start_date,
                'campaign_end_date': campaign.campaign_end_date,
                'campaign_budget': campaign.campaign_budget,
                'campaign_status': campaign.campaign_status,
                'campaign_niche': campaign.campaign_niche,
            }
        ad_data_list = Ad_data.query.filter_by(sponsor_campaign_id=campaign_id).all()
        return render_template("view_campaign.html", title="View Campaign", data=data, ad_data_list=ad_data_list, username=username)
    campaign = Sponsor_campaigns.query.filter_by(id=campaign_id).first()
    if campaign:
        data = {
            'campaign_id': campaign.id,
            'sponsor_username': campaign.sponsor_username,
            'campaign_title': campaign.campaign_title,
            'campaign_description': campaign.campaign_description,
            'campaign_start_date': campaign.campaign_start_date,
            'campaign_end_date': campaign.campaign_end_date,
            'campaign_budget': campaign.campaign_budget,
            'campaign_status': campaign.campaign_status,
            'campaign_niche': campaign.campaign_niche,
        }
        ad_data_list = Ad_data.query.filter_by(sponsor_campaign_id=campaign_id).all()
        return render_template("view_campaign.html", title="View Campaign", data=data, ad_data_list=ad_data_list, username=username)
        # flash('Campaign not found', 'danger')
        # return redirect(url_for('sponsor_campaigns'))
    return render_template("view_campaign.html", title="View Campaign", username=username)

@app.route("/delete_camapign/<username>", methods=["POST", "GET"])
def delete_campaign(username):
    if request.method=="POST":
        campaign_id = request.form['delete']
        campaign = Sponsor_campaigns.query.filter_by(id=campaign_id).first()
        if campaign:
            ad_data = Ad_data.query.filter_by(sponsor_campaign_id=campaign_id).all()
            for ad in ad_data:
                db.session.delete(ad)
            db.session.delete(campaign)
            db.session.commit()
            flash('Campaign deleted successfully', 'success')
            return redirect(url_for('sponsor_campaigns', username=username))
        flash('Campaign not found', 'danger')
        return redirect(url_for('sponsor_campaigns', username=username))

@app.route("/edit_campaign/<username>", methods=["POST", "GET"])
def edit_campaign(username):
    if request.method=="POST":
        campaign_id = request.form['edit']
        campaign = Sponsor_campaigns.query.filter_by(id=campaign_id).first()
        if campaign:
            data = {
                'campaign_id': campaign.id,
                'sponsor_username': campaign.sponsor_username,
                'campaign_title': campaign.campaign_title,
                'campaign_description': campaign.campaign_description,
                'campaign_start_date': campaign.campaign_start_date,
                'campaign_end_date': campaign.campaign_end_date,
                'campaign_budget': campaign.campaign_budget,
                'campaign_status': campaign.campaign_status,
                'campaign_niche': campaign.campaign_niche,
            }
            return render_template("edit_campaign.html", title="Edit Campaign", data=data, username=username)
        flash('Campaign not found', 'danger')
        return redirect(url_for('sponsor_campaigns', username=username))

@app.route("/edit_campaign_data/<username>", methods=["POST", "GET"])
def edit_campaign_data(username):
    print(username)
    if request.method=="POST":
        campaign = Sponsor_campaigns.query.filter_by(id=request.form['campaign_id']).first()
        if campaign:
            print(campaign)
            campaign.campaign_title = request.form['title']
            campaign.campaign_description = request.form['description']
            campaign.campaign_start_date = request.form['start_date']
            campaign.campaign_end_date = request.form['end_date']
            campaign.campaign_budget = int(request.form['budget'])
            campaign.campaign_status = request.form['visibility']
            niche_all = request.form['niche']
            niche = list(niche_all.split(','))
            campaign.campaign_niche = ' '.join([str(elem).lower() for elem in niche])
            db.session.commit()
            flash('Campaign updated successfully', 'success')
            print(campaign)
            return redirect(url_for('sponsor_campaigns', username=username))
    return redirect(url_for('sponsor_campaigns', username=username))


@app.route("/add_ad_request/<username>", methods=["POST", "GET"])
def add_ad_request(username):
    if request.method=="POST":
        campaign_id=request.form['campaign_id']
        print(campaign_id)
    flash('Advertisement request sent sucessfully', 'success')
    return render_template("add_ad_request.html", title="Add Ad Request", username=username, campaign_id=campaign_id)

@app.route("/ad_request_data/<username>", methods=["POST", "GET"])
def ad_request_data(username):
    sponsor_username = username
    if request.method=="POST":
        sponsor_campaign_id = request.form['campaign_id']
        influencer_username = request.form['influencer_username']
        ad_title = request.form['title']
        ad_description = request.form['description']
        ad_niche_all = request.form['niche']
        niche = list(ad_niche_all.split(','))
        ad_niche = ' '.join([str(elem).lower() for elem in niche])
        ad_requirements = request.form['requirements']
        ad_budget = int(request.form['budget'])
        query_data = Ad_data(sponsor_campaign_id=sponsor_campaign_id, sponsor_username=sponsor_username, influencer_username=influencer_username, ad_tile=ad_title, ad_description=ad_description, ad_niche=ad_niche, ad_requirements=ad_requirements, ad_budget=ad_budget)
        db.session.add(query_data)
        db.session.commit()
        print(Ad_data.query.all())
    return redirect(url_for('view_campaign', campaign_id=sponsor_campaign_id, username=username))

@app.route("/view_ad/<username>/<int:ad_id>", methods=["POST", "GET"])
def view_ad(username, ad_id):
    if request.method=="POST":
        print(1)
        campaign_id = request.form['campaign_id']
        campaign = Sponsor_campaigns.query.filter_by(id=campaign_id).first()
        if campaign:
            data = {
                'campaign_id': campaign.id,
                'sponsor_username': campaign.sponsor_username,
                'campaign_title': campaign.campaign_title,
                'campaign_description': campaign.campaign_description,
                'campaign_start_date': campaign.campaign_start_date,
                'campaign_end_date': campaign.campaign_end_date,
                'campaign_budget': campaign.campaign_budget,
                'campaign_status': campaign.campaign_status,
                'campaign_niche': campaign.campaign_niche,
            }
    if request.method=="GET":
        campaign_id = Ad_data.query.filter_by(id=ad_id).first().sponsor_campaign_id
        campaign = Sponsor_campaigns.query.filter_by(id=campaign_id).first()
        if campaign:
            data = {
                'campaign_id': campaign.id,
                'sponsor_username': campaign.sponsor_username,
                'campaign_title': campaign.campaign_title,
                'campaign_description': campaign.campaign_description,
                'campaign_start_date': campaign.campaign_start_date,
                'campaign_end_date': campaign.campaign_end_date,
                'campaign_budget': campaign.campaign_budget,
                'campaign_status': campaign.campaign_status,
                'campaign_niche': campaign.campaign_niche,
            }
    ad_data_list = Ad_data.query.filter_by(id=ad_id).first()
    if ad_data_list:
        ad_data = {
            'camapign_id': ad_data_list.sponsor_campaign_id,
            'ad_id': ad_data_list.id,
            'ad_sponsor_username': ad_data_list.sponsor_username,
            'ad_infleuncer_username': ad_data_list.influencer_username,
            'ad_title': ad_data_list.ad_tile,
            'ad_description': ad_data_list.ad_description,
            'ad_niche': ad_data_list.ad_niche,
            'ad_requirements': ad_data_list.ad_requirements,
            'ad_budget': ad_data_list.ad_budget,
            'ad_status': ad_data_list.ad_status,
            'ad_negotiated_budget': ad_data_list.ad_negotiated_budget
        }
        print(ad_data)
    return render_template("view_ad.html", title="View Ad", data=data, ad_data=ad_data, username=username)

@app.route("/delete_ad/<username>/<int:ad_id>", methods=["POST", "GET"])
def delete_ad(username, ad_id):
    ad = Ad_data.query.filter_by(id=ad_id).first()
    campaign_id = ad.sponsor_campaign_id
    if ad:
        db.session.delete(ad)
        db.session.commit()
        flash('Ad deleted successfully', 'success')
    return redirect(url_for('view_campaign', campaign_id=campaign_id, username=username))

@app.route("/edit_ad/<username>/<int:ad_id>")
def edit_ad(username, ad_id):
    ad_data_list = Ad_data.query.filter_by(id=ad_id).first()
    if ad_data_list:
        ad_data = {
                    'camapign_id': ad_data_list.sponsor_campaign_id,
                    'ad_id': ad_data_list.id,
                    'ad_sponsor_username': ad_data_list.sponsor_username,
                    'ad_infleuncer_username': ad_data_list.influencer_username,
                    'ad_title': ad_data_list.ad_tile,
                    'ad_description': ad_data_list.ad_description,
                    'ad_niche': ad_data_list.ad_niche,
                    'ad_requirements': ad_data_list.ad_requirements,
                    'ad_budget': ad_data_list.ad_budget,
                    'ad_status': ad_data_list.ad_status,
                }
    campaign_id = ad_data_list.sponsor_campaign_id
    campaign = Sponsor_campaigns.query.filter_by(id=campaign_id).first()
    if campaign:
        data = {
                'campaign_id': campaign.id,
                'sponsor_username': campaign.sponsor_username,
                'campaign_title': campaign.campaign_title,
                'campaign_description': campaign.campaign_description,
                'campaign_start_date': campaign.campaign_start_date,
                'campaign_end_date': campaign.campaign_end_date,
                'campaign_budget': campaign.campaign_budget,
                'campaign_status': campaign.campaign_status,
                'campaign_niche': campaign.campaign_niche,
            }
    return render_template("edit_ad.html", title="Edit Ad", data=data, ad_data=ad_data, username=username)

@app.route("/edit_ad_data/<username>", methods=["POST", "GET"])
def edit_ad_data(username):
    if request.method=="POST":
        ad = Ad_data.query.filter_by(id=request.form['ad_id']).first()
        if ad:
            ad.ad_tile = request.form['title']
            ad.ad_description = request.form['description']
            ad_niche_all = request.form['niche']
            niche = list(ad_niche_all.split(','))
            ad.ad_niche = ' '.join([str(elem).lower() for elem in niche])
            ad.ad_requirements = request.form['requirements']
            ad.ad_budget = int(request.form['budget'])
            db.session.commit()
            flash('Ad updated successfully', 'success')
            return redirect(url_for('view_ad', ad_id=ad.id, username=username))
    return redirect(url_for('sponsor_campaigns', username=username))

@app.route("/sponsor_view_accepted_ad/<username>/<int:ad_id>", methods=["POST", "GET"])
def sponsor_view_accepted_ad(username, ad_id):
    if request.method=="POST":
        print(1)
        campaign_id = request.form['campaign_id']
        campaign = Sponsor_campaigns.query.filter_by(id=campaign_id).first()
        if campaign:
            data = {
                'campaign_id': campaign.id,
                'sponsor_username': campaign.sponsor_username,
                'campaign_title': campaign.campaign_title,
                'campaign_description': campaign.campaign_description,
                'campaign_start_date': campaign.campaign_start_date,
                'campaign_end_date': campaign.campaign_end_date,
                'campaign_budget': campaign.campaign_budget,
                'campaign_status': campaign.campaign_status,
                'campaign_niche': campaign.campaign_niche,
            }
    ad_data_list = Ad_data.query.filter_by(id=ad_id).first()
    if ad_data_list:
        ad_data = {
            'camapign_id': ad_data_list.sponsor_campaign_id,
            'ad_id': ad_data_list.id,
            'ad_sponsor_username': ad_data_list.sponsor_username,
            'ad_infleuncer_username': ad_data_list.influencer_username,
            'ad_title': ad_data_list.ad_tile,
            'ad_description': ad_data_list.ad_description,
            'ad_niche': ad_data_list.ad_niche,
            'ad_requirements': ad_data_list.ad_requirements,
            'ad_budget': ad_data_list.ad_budget,
            'ad_status': ad_data_list.ad_status,
            'ad_negotiated_budget': ad_data_list.ad_negotiated_budget
        }
    return render_template("sponsor_view_accepted_ad.html", title='View Accepted Ad', ad_data=ad_data, data=data, username=username)
    
@app.route("/sponsor_view_completed_ad/<username>/<int:ad_id>", methods=["POST", "GET"])
def sponsor_view_completed_ad(username, ad_id):
    if request.method=="POST":
        print(1)
        campaign_id = request.form['campaign_id']
        campaign = Sponsor_campaigns.query.filter_by(id=campaign_id).first()
        if campaign:
            data = {
                'campaign_id': campaign.id,
                'sponsor_username': campaign.sponsor_username,
                'campaign_title': campaign.campaign_title,
                'campaign_description': campaign.campaign_description,
                'campaign_start_date': campaign.campaign_start_date,
                'campaign_end_date': campaign.campaign_end_date,
                'campaign_budget': campaign.campaign_budget,
                'campaign_status': campaign.campaign_status,
                'campaign_niche': campaign.campaign_niche,
            }
    ad_data_list = Ad_data.query.filter_by(id=ad_id).first()
    if ad_data_list:
        ad_data = {
            'camapign_id': ad_data_list.sponsor_campaign_id,
            'ad_id': ad_data_list.id,
            'ad_sponsor_username': ad_data_list.sponsor_username,
            'ad_infleuncer_username': ad_data_list.influencer_username,
            'ad_title': ad_data_list.ad_tile,
            'ad_description': ad_data_list.ad_description,
            'ad_niche': ad_data_list.ad_niche,
            'ad_requirements': ad_data_list.ad_requirements,
            'ad_budget': ad_data_list.ad_budget,
            'ad_status': ad_data_list.ad_status,
            'ad_negotiated_budget': ad_data_list.ad_negotiated_budget
        }
    return render_template("sponsor_view_completed_ad.html", title='View Accepted Ad', ad_data=ad_data, data=data, username=username)

@app.route("/view_ad/decision_ad/<username>/<int:ad_id>", methods=["POST", "GET"])
def sponsor_decision_ad(username, ad_id):
    ad_data = Ad_data.query.filter_by(id=ad_id).first()
    if request.method=="POST":
        if 'negotiated_budget' in request.form.keys():
            negotiated_budget = request.form['negotiated_budget']
            ad_data.ad_negotiated_budget = negotiated_budget
            ad_data.ad_status = 'Negotiation'
            db.session.commit()
            flash('Negotiation started', 'success')
        if 'change_status' in request.form.keys():
            if request.form['change_status'] == 'Completed':
                ad_data.ad_status = 'Completed'
                influencer_username = Ad_data.query.filter_by(id=ad_id).first().influencer_username
                influencer = Influencer.query.filter_by(username=influencer_username).first()
                if ad_data.ad_negotiated_budget != 0:
                    influencer.total_earning += ad_data.ad_negotiated_budget
                else:
                    influencer.total_earning += ad_data.ad_budget
                db.session.commit()
                flash('Request Completed', 'success')
            if request.form['change_status'] == 'Negotiation':
                ad_data.ad_status = 'Negotiation'
                db.session.commit()
                flash('Request Negotiated', 'success')
            if request.form['change_status'] == 'Accepted':
                ad_data.ad_status = 'Accepted'
                db.session.commit()
                flash('Request Accepted', 'success')
            if request.form['change_status'] == 'Rejected':
                ad_data.ad_status = 'Sent'
                ad_data.influencer_username = ""
                db.session.commit()
                flash('Request Declined', 'danger')
    return redirect(url_for('view_campaign', campaign_id=ad_data.sponsor_campaign_id, username=username))

@app.route("/sposnor_find/<username>/", methods=["POST", "GET"])
def sponsor_find(username):
    sponsor = Sponsor.query.filter_by(username=username).first()
    if sponsor:
        data = {
            'email': sponsor.email,
            'companyName': sponsor.company_name,
            'username': sponsor.username,
            'password': sponsor.password,
            'industry': sponsor.industry,
            'photo_url': sponsor.image_url
        }
    influencer_list = Influencer.query.all()
    influencer_list_public = Influencer.query.filter_by(private_profile=False).all()
    private_influencer_list = []
    for influencer in influencer_list:
        if any(x in influencer.niche for x in data['industry']):
            private_influencer_list.append(influencer)
    return render_template("sposnor_find.html", title="Find Influencer", data=data, influencer_list=influencer_list_public, private_influencer_list=private_influencer_list, username=username)

@app.route("/sposnor_find/<username>/search/", methods=["POST", "GET"])
def sponsor_search(username):
    sponsor = Sponsor.query.filter_by(username=username).first()
    if sponsor:
        data = {
            'email': sponsor.email,
            'companyName': sponsor.company_name,
            'username': sponsor.username,
            'password': sponsor.password,
            'industry': sponsor.industry,
            'photo_url': sponsor.image_url
        }
    if request.method=="POST":
        if request.form['search_username'] and request.form['reach'] == 'Select Reach':
            influencer_data = Influencer.query.filter(
                Influencer.username == request.form['search_username'],
                Influencer.private_profile == False
            ).all()
            if influencer_data == None:
                flash('Please enter a valid search query', 'danger')  
                return redirect(url_for('sponsor_find', username=username))
            print(influencer_data)
        elif request.form['reach'] != 'Select Reach' and request.form['search_username']== '':
            reach_value = int(request.form['reach'][:-1])
            influencer_data = Influencer.query.filter(Influencer.reach >= reach_value, Influencer.private_profile == False).all()
            if influencer_data == None:
                flash('Please enter a valid search query', 'danger')  
                return redirect(url_for('sponsor_find', username=username))
            print(influencer_data)
        elif request.form['search_username'] and request.form['reach'] != 'Select Reach':
            reach_value = int(request.form['reach'][:-1])
            influencer_data = Influencer.query.filter(Influencer.reach >= reach_value, Influencer.username==request.form['search_username'], Influencer.private_profile == False).all()
            if influencer_data == None:
                flash('Please enter a valid search query', 'danger')  
                return redirect(url_for('sponsor_find', username=username))
            print(1)
            print(list(influencer_data))
        else:
            flash('Please enter a valid search query', 'danger')  
            return redirect(url_for('sponsor_find', username=username))

        return render_template("sponsor_search_result.html", title="Search Result", data=data, influencer_data=influencer_data, username=username)
    

@app.route("/influencer_profile/<username>", methods=["POST", "GET"])
def influencer_profile(username):
    sponsor = Sponsor.query.filter_by(username=username).first()
    if sponsor:
        data = {
            'email': sponsor.email,
            'companyName': sponsor.company_name,
            'username': sponsor.username,
            'password': sponsor.password,
            'industry': sponsor.industry,
            'photo_url': sponsor.image_url
        }
    if request.method=="POST":
        influencer_username = request.form["influencer_username"]
        influencer_data = Influencer.query.filter_by(username=influencer_username).first()
        ad_data = Ad_data.query.filter_by(influencer_username=influencer_username).all()
        completed_ad = 0
        total_ad = len(ad_data)
        for ads in ad_data:
            if ads.ad_status == 'Completed':
                completed_ad += 1
        remaining_ad = total_ad - completed_ad
        categories = ['Completed Ads', 'Remaining Ads']
        ad_counts = [completed_ad, remaining_ad]
        plt.bar(categories, ad_counts, color=['green', 'yellow'])
        plt.ylabel('Number of Ads')
        plt.ylim(0, total_ad + 1)
        plt.yticks(range(0, total_ad+1, 1))
        plt.xlabel('Ad Status')
        plt.title('Completed vs Remaining Ads')
        graph_path = f"graphs/stats_{influencer_username}"
        plt.savefig(os.path.join(app.static_folder, graph_path))
        plt.clf()
        return render_template("influencer_profile.html", title = "Influencer Profile", data=data, influencer_data = influencer_data, username=username, total_ad=total_ad, completed_ad=completed_ad, remaining_ad=remaining_ad, influencer_username=influencer_username)

@app.route("/sposnor_stats/<username>", methods=["POST", "GET"])
def sponsor_stats(username):
    data = Sponsor.query.filter_by(username=username).first()
    campaign_data = Sponsor_campaigns.query.filter_by(sponsor_username=username).all()
    total_campaign = len(campaign_data)
    ad_data = Ad_data.query.filter_by(sponsor_username=username).all()
    completed_ad = 0
    total_ad = len(ad_data)
    for ads in ad_data:
        if ads.ad_status == 'Completed':
            completed_ad += 1
    remaining_ad = total_ad - completed_ad
    categories = ['Completed Ads', 'Remaining Ads']
    ad_counts = [completed_ad, remaining_ad]
    plt.bar(categories, ad_counts, color=['green', 'yellow'])
    plt.ylabel('Number of Ads')
    plt.ylim(0, total_ad + 1)
    plt.yticks(range(0, total_ad+1, 1))
    plt.xlabel('Ad Status')
    plt.title('Completed vs Remaining Ads')
    graph_path = f"graphs/stats_{username}"
    plt.savefig(os.path.join(app.static_folder, graph_path))
    plt.clf()
    return render_template("sponsor_stats.html", title="Sponsor Stats", username=username, total_campaign=total_campaign, total_ad=total_ad, completed_ad = completed_ad, remaining_ad=remaining_ad, data=data, ad_data=ad_data)

@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check in Influencer table
        influencer = Influencer.query.filter_by(username=username).first()
        if influencer and influencer.password == password:
            session['username'] = username
            session['role'] = 'influencer'
            return redirect(url_for('influencer_dashboard', username=username))
        
        # Check in Sponsor table
        sponsor = Sponsor.query.filter_by(username=username).first()
        if sponsor and sponsor.password == password:
            session['username'] = username
            session['role'] = 'sponsor'
            return redirect(url_for('sponsor_dashboard', username=username))
        
        flash('Invalid username or password', 'danger')
        return redirect(url_for('login'))
    
    return render_template("login.html", title="Login")

@app.route("/logout")
def logout():
    session.clear()  # Clear all session data
    flash('You have been logged out', 'success')
    return redirect(url_for('home'))

@app.route("/influencer_dashboard/", methods=['POST', 'GET'])
def influencer_register_submit():
    if request.method == 'POST':
        email = request.form['email']
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        niche_all = request.form['niche']
        niche = list(niche_all.split(','))
        niche = ' '.join([str(elem).lower() for elem in niche])
        reach = int(request.form['reach'])
        photo_upload = request.files['photo']
        photo_url = f"uploads/{username}_profile_photo.png"
        photo_upload.save(os.path.join(app.static_folder, photo_url))
        print(f"Photo saved at: {os.path.join(app.static_folder, photo_url)}")
        private_profile = False
        if Influencer.query.filter_by(email=email).first():
            flash('Email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('influencer_register'))
        if Influencer.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('influencer_register'))
        query_data = Influencer(email=email, name=name, username=username, password=password, niche=niche, reach=reach, image_url=photo_url, private_profile=False)
        if 'private' in request.form:
            query_data.private_profile = True
            print(Influencer.query.all())
        if 'public' in request.form:
            query_data.private_profile = False
            print(Influencer.query.all())
        db.session.add(query_data)
        db.session.commit()
        print(Influencer.query.all())
        data = {'email': email, 'name': name, 'username': username, 'password': password, 'niche': niche, 'reach': reach, 'photo_url': photo_url, 'private_profile': False}
        return render_template("influencer_dashboard.html", title="Influencer Dashboard", data=data, username=username)
    return render_template("influencer_register.html")

@app.route("/sponsor_dashboard/", methods=['POST', 'GET'])
def sponsor_register_submit():
    if request.method == 'POST':
        email = request.form['email']
        companyName = request.form['companyName']
        username = request.form['username']
        password = request.form['password']
        industry_all = request.form['industry']
        industry = list(industry_all.split(','))
        industry = ''.join([str(elem).lower() for elem in industry])
        photo_upload = request.files['photo']
        photo_url = f"uploads/{username}_profile_photo.png"
        photo_upload.save(os.path.join(app.static_folder, photo_url))
        print(f"Photo saved at: {os.path.join(app.static_folder, photo_url)}")
        if Sponsor.query.filter_by(email=email).first():
            flash('Email already exists. Please choose a different one.', 'danger')
            return redirect(url_for('sponsor_register'))
        if Sponsor.query.filter_by(company_name=companyName).first():
            flash('Company Name already exists. Please choose a different one.', 'danger')
            return redirect(url_for('sponsor_register'))
        if Sponsor.query.filter_by(username=username).first():
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('sponsor_register'))
        query_data = Sponsor(email=email, company_name=companyName, username=username, password=password, industry=industry, image_url=photo_url)
        db.session.add(query_data)
        db.session.commit()
        print(Sponsor.query.all())
        data = {'email': email, 'companyName': companyName, 'username': username, 'password': password, 'industry': industry, 'photo_url': photo_url}
        return render_template("sponsor_dashboard.html", title="Sponsor Dashboard", data=data, username=username)
    return render_template("sponsor_register.html")

if __name__ == '__main__':
        app.run(debug=True, host='localhost', port=8001)