import functools

from flask import Blueprint, flash, current_app, g, redirect, render_template, request, session, url_for

from . import media
from . import playback
# from flaskRadio.db import get_db

bp = Blueprint('radio', __name__, url_prefix='/radio')

@bp.route('/', methods=('GET', 'POST'))
def radio():
    if request.method == 'POST':
        speaker = request.form['speaker']
        program = request.form['media']
        error = None

        ## Validate user input
        if not media.isAvailable(program):
            error = 'Unrecognized media "%s"' % program
            
        if error is None:
            try:
                ## @todo Queue audio
                segments = media.getSegments(program)
                session['program']=media.getName(program)
                session['speaker'] = speaker
                g.segments = segments
                current_app.segments = segments
                current_app.logger.debug('Retrieved %d segments' % len(segments))
                playback.queueAudio(segments, True, True)
            except Exception as err:
                raise(err)
            else:
                return redirect(url_for("radio.playing"))

        flash(error)

    return render_template('radio/radio.html', resources=media.available())

@bp.route("/playing", methods=('GET',))
def playing():
    ## @todo Display actual state of play queue
    return render_template('radio/playing.html',
                           program=session.get('program', 'No program selected'),
                           segments=getattr(current_app, 'segments', [])
    )
