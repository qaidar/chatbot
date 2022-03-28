"""
Chat views.
"""
from flask import Blueprint, render_template, request, session, current_app, abort
from wtforms import Form, StringField, validators

from chatbot.auth import login_required

# Create a blueprint for authentication
bp = Blueprint('chat', __name__, url_prefix='/chat')


@bp.route('/', methods=('GET',))
@login_required
def overview():
    """ Route for the chat overview
    """
    return render_template('chat/overview.html', prompts=current_app.prompts)


@bp.route('/<chat_scenario>', methods=('GET', 'POST'))
@login_required
def chat(chat_scenario):
    """ Route for chat with variable scenarios
    """
    form = ChatForm(request.form)

    # Return 404 if chat scenario not found
    promptExists = chat_scenario in current_app.prompts.keys()
    if not promptExists:
        abort(404)
        # return render_template('404.html'), 404

    # If the users opens the chat from somewhere else, clear chat history
    userOpensChatFirstTime = request.url != request.referrer
    if userOpensChatFirstTime:
        clear_chat_history()

    # request.referrer.split('/')[-1]

    prompt = current_app.prompts[chat_scenario]
    prompt_text = prompt['text']
    # if chat_scenario 
    # prompt = current_app.prompts

    # Get chat history
    chat_history = session.get('chat_history')
    # Create if not exists
    if not chat_history:
        chat_history = []

    # On text form submission
    if request.method == 'POST':
        if request.form['submit_button'] == 'Clear chat':
            # Clear chat history
            clear_chat_history()
        elif request.form['submit_button'] == 'Send text' and form.validate():
            # Add text to chat history
            chat_history.append(
                {
                    'sender': 'user',
                    'text': form.text_input.data
                }
            )

            # Clear form
            form.text_input.data = ""
            # Get response from bot
            chat_history = get_bot_response(chat_history, prompt_text)
            # Update chat history
            session['chat_history'] = chat_history


    return render_template('chat/chat.html', 
                            # chat_scenario=chat_scenario,
                            prompt=prompt,
                            form=form,
                            loc = userOpensChatFirstTime
                            )


# @bp.route('/general', methods=('GET', 'POST'))
# @login_required
# def general():
#     """ Route for general simple chat.
#     """
#     form = ChatForm(request.form)

#     # Get chat history
#     chat_history = session.get('chat_history')
#     # Create if not exists
#     if not chat_history:
#         chat_history = []

#     # On text form submission
#     if request.method == 'POST':
#         if request.form['submit_button'] == 'Clear chat':
#             # Clear chat history
#             clear_chat_history()
#         elif request.form['submit_button'] == 'Send text' and form.validate():
#             # Add text to chat history
#             chat_history.append(
#                 {
#                     'sender': 'user',
#                     'text': form.text_input.data
#                 }
#             )

#             # Clear form
#             form.text_input.data = ""
#             # Get response from bot
#             chat_history = get_bot_response(chat_history)
#             # Update chat history
#             session['chat_history'] = chat_history
        
#     return render_template('chat/general_chat.html', form=form)


def get_bot_response(chat_history, prompt_text):
    """ Get response from the bot """
    # Here we have to get the response from the bot
    # chat_history should be sent to the model class
    # Something like:
    # response = model.predict(chat_history)
    # chat_history_new = chat_history.append(response)
    # Dummy response for now
    # chat_history.append(
    #     {
    #         'sender': 'bot',
    #         'text': 'This is an automated dummy reply.'
    #     }
    # )
    if current_app.config['LOAD_GRAMMAR_MODEL']:
        chat_history = current_app.grammar_correction.add_correction_to_chat_history(chat_history)
    chat_history = current_app.language_model.add_response_to_chat_history(chat_history, prompt_text)

    return chat_history

def clear_chat_history():
    """ Clear the chat history """
    if session.get('chat_history'):
        session.pop('chat_history')

class ChatForm(Form):
    text_input = StringField('Input',
                            [validators.Length(min=4, max=300)],
                            render_kw={'class': 'form-control chat_text_input_field'}
                            )
