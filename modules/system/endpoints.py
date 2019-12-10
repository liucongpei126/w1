import yaml
from flask import Flask
from flask import json, url_for, Response
from flask_classy import FlaskView, route
from git import Repo, Git
from flask import render_template
import commands
from modules.ui.endpoints import react

from modules.app_config import cbpi

import pprint
import time


class SystemView(FlaskView):
    def doShutdown(self):
        time.sleep(5)
        from subprocess import call
        call("halt")

    @route('/shutdown', methods=['POST'])
    def shutdown(self):
        """
        Shutdown hook
        :return: HTTP 204
        """
        self.doShutdown()

        return ('', 204)

    def doReboot(self):
        time.sleep(5)
        from subprocess import call
        call("reboot")

    @route('/reboot', methods=['POST'])
    def reboot(self):
        """
        Reboot hook
        :return: HTTP 204
        """
        self.doReboot()

        return ('', 204)

    @route('/tags/<name>', methods=['GET'])
    def checkout_tag(self,name):
        repo = Repo('./')
        repo.git.reset('--hard')
        o = repo.remotes.origin
        o.fetch()
        g = Git('./')
        g.checkout(name)
        cbpi.notify("Checkout successful", "Please restart the system")
        return ('', 204)

    @route('/git/status', methods=['GET'])
    def git_status(self):
        repo = Repo('./')
        o = repo.remotes.origin
        o.fetch()
        # Tags
        tags = []
        for t in repo.tags:
            tags.append({"name": t.name, "commit": str(t.commit), "date": t.commit.committed_date,
                         "committer": t.commit.committer.name, "message": t.commit.message})
        try:
            branch_name = repo.active_branch.name
            # test1
        except:
            branch_name = None

        changes = []
        commits_behind = repo.iter_commits('master..origin/master')

        for c in list(commits_behind):
            changes.append({"committer": c.committer.name, "message": c.message})

        return json.dumps({"tags": tags, "headcommit": str(repo.head.commit), "branchname": branch_name,
                           "master": {"changes": changes}})

    @route('/check_update', methods=['GET'])
    def check_update(self):

        repo = Repo('./')
        o = repo.remotes.origin
        o.fetch()
        changes = []
        commits_behind = repo.iter_commits('master..origin/master')

        for c in list(commits_behind):
            changes.append({"committer": c.committer.name, "message": c.message})

        return json.dumps(changes)


    def get_mage(self):
	commands.getoutput("fswebcam -d /dev/video1 --no-banner -r 640x480 image4.jpg")
	f = None
	frame = None
	try:
	    f = open("image4.jpg",'r')
	    frame = f.read()
	    assert "f.read()"
	finally:
	    if f:
		f.close()
	return (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

    @route('/webcam/frame',methods=['GET'])
    def webcam_frame(self):
	assert "webcam frame"
	mframe = self.get_mage()
	return Response(mframe,mimetype='multipart/x-mixed-replace; boundary=frame')

    @route('/webcam', methods=['GET'])
    def webcam(self):
#        return '<h1> Hellow hahha 222</h1>'
#	return render_template('fswebcam.html')
	return react.send_static_file("fswebcam.html")

    @route('/git/pull', methods=['POST'])
    def update(self):
        repo = Repo('./')
        o = repo.remotes.origin
        info = o.pull()
        cbpi.notify("Pull successful", "The lasted updated was downloaded. Please restart the system")
        return ('', 204)

    @route('/dump', methods=['GET'])
    def dump(self):
        return json.dumps(cbpi.cache)

    @route('/endpoints', methods=['GET'])
    def endpoints(self):
        import urllib
        output = []
        vf = self.api.app.view_functions

        for f in self.api.app.view_functions:
            print  f
        endpoints = {}
        re =  {
            "swagger": "2.0",
            "host": "",
            "info": {
                "description":"",
                "version": "",
                "title": "CraftBeerPi"
            },
            "schemes": ["http"],
            "paths": endpoints}
        for rule in self.api.app.url_map.iter_rules():
            r = rule
            endpoints[rule.rule] = {}
            if "HEAD" in r.methods: r.methods.remove("HEAD")
            if "OPTIONS" in r.methods: r.methods.remove("OPTIONS")
            for m in rule.methods:
                endpoints[rule.rule][m] = dict(summary="", description="", consumes=["application/json"],produces=["application/json"])

        with open("config/version.yaml", 'r') as stream:

            y = yaml.load(stream)
        pprint.pprint(y)
        pprint.pprint(re)
        return Response(yaml.dump(re), mimetype='text/yaml')

    @route('/hello', methods=["GET"])
    def hello(self):
        return '<h1> Hellow Lcp 222</h1>'


@cbpi.initalizer()
def init(cbpi):

    SystemView.api = cbpi
    SystemView.register(cbpi.app, route_base='/api/system')
