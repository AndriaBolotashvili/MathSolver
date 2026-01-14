from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, login_required, logout_user, current_user
from fractions import Fraction
from math import sqrt, pi

from .forms import (
    RegisterForm, LoginForm, PostForm, CommentForm,
    TriangleForm, QuadraticForm, CircleForm, TrapezoidForm
)
from .models import User, Post, PostLike, Comment, ProblemHistory
from . import db

main = Blueprint('main', __name__)

@main.before_request
def check_if_banned():
    if current_user.is_authenticated and current_user.is_banned:
        allowed_routes = [
            'main.logout',
            'main.banned'
        ]

        if request.endpoint not in allowed_routes:
            return redirect(url_for('main.banned'))



def pretty_number(x):
    if x is None:
        return None

    if abs(x - round(x)) < 1e-9:
        return str(int(round(x)))

    frac = Fraction(x).limit_denominator(20)
    if abs(float(frac) - x) < 1e-9:
        return f"{frac.numerator}/{frac.denominator}"

    return f"{x:.2f}"


def pretty_pi(value):
    approx = f"{value:.2f}"
    frac = Fraction(value / pi).limit_denominator(20)

    if frac.denominator == 1:
        exact = f"{frac.numerator}π"
    else:
        exact = f"{frac.numerator}/{frac.denominator}π"

    return f"{exact} ≈ {approx}"


def save_history():
    if current_user.is_authenticated:
        db.session.add(ProblemHistory(user_id=current_user.id))
        db.session.commit()



@main.route('/')
def index():
    return render_template('index.html')

@main.route("/banned")
@login_required
def banned():
    return render_template("banned.html")


@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("Username უკვე გამოყენებულია")
            return redirect(url_for('main.register'))

        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        return redirect(url_for('main.profile'))

    return render_template('register.html', form=form)

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('main.profile'))
        flash("არასწორი მონაცემები")
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))

@main.route('/profile')
@login_required
def profile():
    solved_count = ProblemHistory.query.filter_by(user_id=current_user.id).count()
    return render_template(
        'profile.html',
        user=current_user,
        solved_count=solved_count
    )

@main.route('/problems')
def problems():
    return render_template('problems.html')

@main.route('/forum')
def forum():
    posts = Post.query.order_by(Post.id.desc()).all()
    return render_template('forum.html', posts=posts)


@main.route('/forum/create', methods=['GET', 'POST'])
@login_required
def create_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id
        )
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('main.forum'))

    return render_template('create_post.html', form=form)


@main.route('/forum/post/<int:post_id>', methods=['GET', 'POST'])
def view_post(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()

    if form.validate_on_submit() and current_user.is_authenticated:
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            post_id=post.id
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('main.view_post', post_id=post.id))

    return render_template('view_post.html', post=post, form=form)


@main.route('/forum/post/<int:post_id>/like')
@login_required
def like_post(post_id):
    if not PostLike.query.filter_by(user_id=current_user.id, post_id=post_id).first():
        db.session.add(PostLike(user_id=current_user.id, post_id=post_id))
        db.session.commit()
    return redirect(url_for('main.view_post', post_id=post_id))


@main.route('/forum/post/<int:post_id>/delete')
@login_required
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)
    if current_user.username == "Vayton3":
        db.session.delete(post)
        db.session.commit()
    else:
        flash("მხოლოდ ადმინს შეუძლია")
    return redirect(url_for('main.forum'))



@main.route('/solve/triangle', methods=['GET', 'POST'])
def solve_triangle():
    form = TriangleForm()
    area = None

    if form.validate_on_submit():
        a, b, c = form.a.data, form.b.data, form.c.data


        if a + b <= c or a + c <= b or b + c <= a:
            area = "სამკუთხედი არ არსებობს"
        else:
            s = (a + b + c) / 2
            area = pretty_number(sqrt(s * (s - a) * (s - b) * (s - c)))
            save_history()

    return render_template('solve/triangle.html', form=form, area=area)



@main.route('/solve/quadratic', methods=['GET', 'POST'])
def solve_quadratic():
    form = QuadraticForm()
    result = None

    if form.validate_on_submit():
        a, b, c = form.a.data, form.b.data, form.c.data
        d = b**2 - 4*a*c

        if d < 0:
            result = "რეალური პასუხი არ არსებობს"
        else:
            sqrt_d = sqrt(d)

            def as_fraction(x):
                frac = Fraction(x).limit_denominator(1000)
                if frac.denominator == 1:
                    return str(frac.numerator)
                return f"{frac.numerator}/{frac.denominator}"


            x1 = (-b + sqrt_d) / (2*a)
            x2 = (-b - sqrt_d) / (2*a)


            x1 = as_fraction(x1)
            x2 = as_fraction(x2)

            result = (x1, x2)
        save_history()
    return render_template('solve/quadratic.html', form=form, result=result)


@main.route('/solve/circle', methods=['GET', 'POST'])
def solve_circle():
    form = CircleForm()
    area = circumference = None

    if form.validate_on_submit():
        r = form.r.data
        area = pretty_pi(pi * r * r)
        circumference = pretty_pi(2 * pi * r)
        save_history()

    return render_template(
        'solve/circle.html',
        form=form,
        area=area,
        circumference=circumference
    )

@main.route('/solve/trapezoid', methods=['GET', 'POST'])
def solve_trapezoid():
    form = TrapezoidForm()
    area = None

    if form.validate_on_submit():
        area = pretty_number(
            (form.a.data + form.b.data) / 2 * form.h.data
        )
        save_history()

    return render_template('solve/trapezoid.html', form=form, area=area)

@main.route('/theory')
def theory():
    return render_template('theory.html')

@main.route('/admin/users')
@login_required
def admin_users():
    if current_user.username != "Vayton3":
        flash("წვდომა აკრძალულია")
        return redirect(url_for('main.index'))

    users = User.query.all()
    return render_template('admin/users.html', users=users)


@main.route('/admin/user/<int:user_id>')
@login_required
def admin_view_user(user_id):
    if current_user.username != "Vayton3":
        flash("წვდომა აკრძალულია")
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)
    solved_count = ProblemHistory.query.filter_by(user_id=user.id).count()

    return render_template(
        'admin/user_profile.html',
        user=user,
        solved_count=solved_count
    )


@main.route('/admin/user/<int:user_id>/ban')
@login_required
def admin_ban_user(user_id):
    if current_user.username != "Vayton3":
        flash("წვდომა აკრძალულია")
        return redirect(url_for('main.index'))

    user = User.query.get_or_404(user_id)

    if user.username == "Vayton3":
        flash("საკუთარი თავის დაბანვა არ შეიძლება")
        return redirect(url_for('main.admin_users'))

    user.is_banned = True
    db.session.commit()

    flash("მომხმარებელი დაბანილია")
    return redirect(url_for('main.admin_users'))

@main.route("/admin/unban/<int:user_id>")
@login_required
def unban_user(user_id):
    if current_user.username != "Vayton3":
        flash("წვდომა აკრძალულია")
        return redirect(url_for("main.index"))

    user = User.query.get_or_404(user_id)
    user.is_banned = False
    db.session.commit()

    flash(f"მომხმარებელი {user.username} განბლოკილია")
    return redirect(url_for("main.admin_users"))

@main.route('/forum/comment/<int:comment_id>/delete')
@login_required
def delete_comment(comment_id):
    if current_user.username != "Vayton3":
        flash("წვდომა აკრძალულია")
        return redirect(url_for('main.index'))

    comment = Comment.query.get_or_404(comment_id)
    post_id = comment.post_id

    db.session.delete(comment)
    db.session.commit()

    flash("კომენტარი წაიშალა")
    return redirect(url_for('main.view_post', post_id=post_id))

