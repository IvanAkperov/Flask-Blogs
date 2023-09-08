from flask import Blueprint, request, render_template, flash, redirect, url_for, abort
from flask_login import login_required, current_user

from flaskblog import db
from flaskblog.models import Post, Comment, User
from flaskblog.posts.forms import PostForm

posts = Blueprint("posts", __name__)


@posts.route("/post")
def post():
    page = request.args.get("page", 1, type=int)
    all_posts = Post.query.paginate(page=page, per_page=5)
    return render_template("posts.html", title="Posts", posts=all_posts)


@posts.route("/post/new", methods=["POST", "GET"])
@login_required
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        post_to_add = Post(title=form.title.data.capitalize(), content=form.content.data, author=current_user)
        db.session.add(post_to_add)
        db.session.commit()
        flash("Your post has been added!", "success")
        return redirect(url_for("posts.post"))
    return render_template("create.html", title="Create a new post", form=form, legend="New post")


@posts.route("/post/<int:post_id>")
def get_post(post_id):
    get_post_id = Post.query.get_or_404(post_id)
    return render_template("get_post.html", title=get_post_id.title, post=get_post_id)


@posts.route("/post/<int:post_id>/update", methods=["POST", "GET"])
@login_required
def update_post(post_id):
    get_post_id = Post.query.get_or_404(post_id)
    if get_post_id.author != current_user:
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        get_post_id.title = form.title.data
        get_post_id.content = form.content.data
        db.session.commit()
        flash("You post has been updated!", "success")
        return redirect(url_for("posts.get_post", post_id=post_id))
    elif request.method == "GET":
        form.title.data = get_post_id.title
        form.content.data = get_post_id.content
    return render_template("create.html", title="Update post", form=form, legend="Update post")


@posts.route("/post/<int:post_id>/delete", methods=["POST", "GET"])
def delete_post(post_id):
    get_post_id = Post.query.get_or_404(post_id)

    if get_post_id.author != current_user:
        abort(403)
    db.session.delete(get_post_id)
    db.session.commit()
    flash("Post has been deleted!", "success")
    return redirect(url_for("posts.post", post_id=post_id))


@posts.route("/search")
def search_post():
    query = request.args.get("query")
    if query:
        message = Post.query.filter(Post.title.ilike(f"%{query}%")).all()
    else:
        message = []
    return render_template("search_posts.html", message=message, query=query, title="Results")


@posts.route('/posts/<int:post_id>/comments', methods=['POST'])
@login_required
def submit_comment(post_id):
    post = Post.query.get_or_404(post_id)
    content = request.form.get('content')
    if content:
        comment = Comment(content=content, post_id=post.id, author_id=current_user.id)
        db.session.add(comment)
        db.session.commit()
        flash('Comment submitted successfully.', 'success')
    return redirect(url_for('posts.post', post_id=post.id, author=current_user.user))
