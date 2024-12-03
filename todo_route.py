import logging

from flask import Blueprint, render_template, session, request, redirect, url_for, flash

from log_config import setup_logging
from models import User, Todo, Session
from utils import session_token_required

setup_logging()
logger = logging.getLogger(__name__)

todo_router = Blueprint('todo', __name__)


# Add Todo Route
@todo_router.route("/add_todo", methods=["GET", "POST"])
@session_token_required
def add_todo():
    """
    Add a new Todo item.

    Input:
        - title (str): Todo title
        - description (str): Todo description

    Output:
        - Redirect to user dashboard on success
        - Render add_todo.html template on GET request
    """
    username = session['user_name']
    with Session() as session_db:
        user = session_db.query(User).filter_by(username=username).first()
        if request.method == "POST":
            title = request.form['title']
            description = request.form['description']
            logger.info(f"Adding todo for user {session.get('user_name')}: {title} - {description}")
            try:
                todo = Todo(title=title, description=description, user_id=user.id)
                session_db.add(todo)
                session_db.commit()
                logger.info(f"Todo added for user {user.fullname}: {title} - {description}")
                flash("Todo added successfully.", "Success")
            except Exception as e:
                logger.error(f"Error adding todo: {e}")
                flash("Error adding todo.", "Error")
            return redirect(url_for("user.dashboard"))
        return render_template("add_todo.html", user=user.fullname)


# Action Todo Route
@todo_router.route("/action_todo/<int:todo_id>")
@session_token_required
def action_todo(todo_id):
    """
    Perform an action on a Todo item.

    Input:
        - todo_id (int): Todo ID
        - action (str): Action to perform (close, open, delete)

    Output:
        - Redirect to user dashboard on success
        - Flash error message on failure
    """
    action = request.args.get('action')  # Get action from the URL
    username = session['user_name']

    with Session() as session_db:
        user = session_db.query(User).filter_by(username=username).first()
        todo = session_db.query(Todo).get(todo_id)

        if not todo:
            logger.error(f"Todo not found: {todo_id}")
            flash("Todo not found.", "Error")
            return redirect(url_for("user.dashboard"))

        if todo.user_id != user.id:
            logger.error(f"Permission denied for user {user.id} to perform action on todo {todo_id}")
            flash("You don't have permission to perform this action.", "Error")
            return redirect(url_for("user.dashboard"))

        # Perform the action based on the 'action' parameter
        if action == 'close':
            logger.info(f"Closing todo with id {todo_id} for user id {user.id}")
            try:
                todo.is_done = True
                session_db.add(todo)
                session_db.commit()
                logger.info(f"Todo closed successfully: {todo_id}")
                flash("Todo closed successfully.", "Success")
            except Exception as e:
                logger.error(f"Error closing todo: {e}")
                flash("Error closing todo.", "Error")

        elif action == 'open':
            logger.info(f"Opening todo with id {todo_id} for user id {user.id}")
            try:
                todo.is_done = False
                session_db.add(todo)
                session_db.commit()
                logger.info(f"Todo opened successfully: {todo_id}")
                flash("Todo opened successfully.", "Success")
            except Exception as e:
                logger.error(f"Error opening todo: {e}")
                flash("Error opening todo.", "Error")

        elif action == 'delete':
            logger.info(f"Deleting todo with id {todo_id} for user id {user.id}")
            try:
                todo.is_active = False
                session_db.add(todo)
                session_db.commit()
                logger.info(f"Todo deleted successfully: {todo_id}")
                flash("Todo deleted successfully.", "Success")
            except Exception as e:
                logger.error(f"Error deleting todo: {e}")
                flash("Error deleting todo.", "Error")

        else:
            logger.error(f"Invalid action specified: {action}")
            flash("Invalid action specified.", "Error")
            return redirect(url_for("user.dashboard"))

    return redirect(url_for("user.dashboard"))


# Update Todo Route
@todo_router.route("/update_todo/<int:todo_id>", methods=["GET", "POST"])
@session_token_required
def update_todo(todo_id):
    """
    Update a Todo item.

    Input:
        - todo_id (int): Todo ID
        - title (str): Todo title
        - description (str): Todo description

    Output:
        - Redirect to user dashboard on success
        - Render update_todo.html template on GET request
    """
    username = session['user_name']
    with Session() as session_db:
        user = session_db.query(User).filter_by(username=username).first()
        todo = session_db.query(Todo).get(todo_id)

        if not todo:
            logger.error(f"Todo not found: {todo_id}")
            flash("Todo not found.", "Error")
            return redirect(url_for("user.dashboard"))

        if todo.user_id != user.id:
            logger.error(f"Permission denied for user {user.id} to update todo {todo_id}")
            flash("You don't have permission to update this todo.", "Error")
            return redirect(url_for("user.dashboard"))

        if request.method == "POST":
            title = request.form.get("title")
            description = request.form.get("description")
            logger.info(f"Updating todo with id {todo_id} for user id {user.id}")
            try:
                todo.title = title
                todo.description = description
                session_db.add(todo)
                session_db.commit()
                logger.info(f"Todo updated successfully: {todo_id}")
                flash("Todo updated successfully.", "Success")
            except Exception as e:
                logger.error(f"Error updating todo: {e}")
                flash("Error updating todo.", "Error")
            return redirect(url_for("user.dashboard"))

        return render_template("update_todo.html", todo=todo)
