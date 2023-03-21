from flask import blueprints, jsonify, request
from . import db_session
from .jobs import Jobs
import werkzeug

blueprint = blueprints.Blueprint('get_jobs', __name__)


@blueprint.route('/get/jobs', methods=['GET'])
def get_jobs():
    sess = db_session.create_session()
    jobs = sess.query(Jobs).all()
    print(1)
    if jobs:
        print(2)
        return jsonify(
            {
                'jobs': [
                    item.to_dict(only=('team_leader', 'job', 'work_size', 'collaborators', 'start_date', 'end_date',
                                       'is_finished')) for item in jobs]
            }
        )
    return jsonify({'error': 'empty'})


@blueprint.route('/get/jobs/<int:job_id>', methods=['GET'])
def get_job(job_id):
    sess = db_session.create_session()
    job = sess.query(Jobs).get(job_id)
    if not job:
        return jsonify({'error': 'Not found'})
    return jsonify(job.to_dict(only=('team_leader', 'job', 'work_size', 'collaborators', 'start_date', 'end_date',
                                     'is_finished')))


@blueprint.route('/api/jobs', methods=['POST'])
def add_job():
    sess = db_session.create_session()
    job = Jobs()
    job.team_leader = request.json['team_leader']
    job.job = request.json['job']
    sess.add(job)
    sess.commit()
    # добавляем в сессию, коммитим сессию
