from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models import db, Ledger
from forms.ledger import LedgerForm

ledger_bp = Blueprint('ledger', __name__)

@ledger_bp.route('/')
@login_required
def index():
    ledgers = Ledger.query.filter_by(user_id=current_user.id).all()
    return render_template('ledger/index.html', ledgers=ledgers)

@ledger_bp.route('/create', methods=['GET', 'POST'])
@login_required
def create():
    form = LedgerForm()
    if form.validate_on_submit():
        ledger = Ledger(
            name=form.name.data,
            description=form.description.data,
            user_id=current_user.id
        )
        db.session.add(ledger)
        db.session.commit()
        flash('账本创建成功！', 'success')
        return redirect(url_for('ledger.index'))
    return render_template('ledger/create.html', form=form)

@ledger_bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    ledger = Ledger.query.get_or_404(id)
    if ledger.user_id != current_user.id:
        flash('您没有权限编辑此账本', 'error')
        return redirect(url_for('ledger.index'))
    
    form = LedgerForm(obj=ledger)
    if form.validate_on_submit():
        ledger.name = form.name.data
        ledger.description = form.description.data
        db.session.commit()
        flash('账本更新成功！', 'success')
        return redirect(url_for('ledger.index'))
    return render_template('ledger/edit.html', form=form, ledger=ledger)

@ledger_bp.route('/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    ledger = Ledger.query.get_or_404(id)
    if ledger.user_id != current_user.id:
        flash('您没有权限删除此账本', 'error')
        return redirect(url_for('ledger.index'))
    
    db.session.delete(ledger)
    db.session.commit()
    flash('账本已删除', 'success')
    return redirect(url_for('ledger.index')) 