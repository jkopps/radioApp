import functools

from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for


# from flaskRadio.db import get_db

bp = Blueprint('radio', __name__, url_prefix='/radio')

@bp.route('/', methods=('GET', 'POST'))
def radio():
    if request.method == 'POST':
        speaker = request.form['speaker']
        media = request.form['media']
        error = None

        ## Validate user input
        if media not in (
                'NPR All Things Considered',
                'NPR Morning Edition',
                ):
            error = 'Unrecognized media'
        
        if error is None:
            ## @todo Queue audio
            ## @todo Display now playing
            return 'Selected %s on %s' % (media, speaker)

        flash(error)

    return render_template('radio/radio.html')
