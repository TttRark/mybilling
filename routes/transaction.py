from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from models import db, Transaction, Ledger
from forms.transaction import TransactionForm
from datetime import datetime
import csv
import io

transaction_bp = Blueprint('transaction', __name__)

@transaction_bp.route('/ledger/<int:ledger_id>/transactions')
@login_required
def index(ledger_id):
    ledger = Ledger.query.get_or_404(ledger_id)
    if ledger.user_id != current_user.id:
        flash('您没有权限查看此账本', 'error')
        return redirect(url_for('ledger.index'))
    
    # 获取查询参数
    page = request.args.get('page', 1, type=int)
    per_page = 10  # 每页显示10条记录
    transaction_type = request.args.get('type')
    start_date = request.args.get('start_date')
    end_date = request.args.get('end_date')
    
    # 构建查询
    query = Transaction.query.filter_by(ledger_id=ledger_id)
    
    # 应用过滤条件
    if transaction_type:
        query = query.filter_by(transaction_type=transaction_type)
    if start_date:
        query = query.filter(Transaction.date >= datetime.strptime(start_date, '%Y-%m-%d'))
    if end_date:
        query = query.filter(Transaction.date <= datetime.strptime(end_date, '%Y-%m-%d'))
    
    # 按日期降序排序并分页
    pagination = query.order_by(Transaction.date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    transactions = pagination.items
    
    return render_template('transaction/index.html', 
                         transactions=transactions, 
                         ledger=ledger,
                         pagination=pagination)

@transaction_bp.route('/ledger/<int:ledger_id>/transactions/create', methods=['GET', 'POST'])
@login_required
def create(ledger_id):
    ledger = Ledger.query.get_or_404(ledger_id)
    if ledger.user_id != current_user.id:
        flash('您没有权限在此账本中添加交易', 'error')
        return redirect(url_for('ledger.index'))
    
    form = TransactionForm()
    if form.validate_on_submit():
        transaction = Transaction(
            amount=form.amount.data,
            description=form.description.data,
            category=form.category.data,
            transaction_type=form.transaction_type.data,
            date=form.date.data,
            ledger_id=ledger_id
        )
        db.session.add(transaction)
        db.session.commit()
        flash('交易记录添加成功！', 'success')
        return redirect(url_for('transaction.index', ledger_id=ledger_id))
    return render_template('transaction/create.html', form=form, ledger=ledger)

@transaction_bp.route('/transaction/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit(id):
    transaction = Transaction.query.get_or_404(id)
    ledger = Ledger.query.get_or_404(transaction.ledger_id)
    if ledger.user_id != current_user.id:
        flash('您没有权限编辑此交易记录', 'error')
        return redirect(url_for('ledger.index'))
    
    form = TransactionForm(obj=transaction)
    if form.validate_on_submit():
        transaction.amount = form.amount.data
        transaction.description = form.description.data
        transaction.category = form.category.data
        transaction.transaction_type = form.transaction_type.data
        transaction.date = form.date.data
        db.session.commit()
        flash('交易记录更新成功！', 'success')
        return redirect(url_for('transaction.index', ledger_id=transaction.ledger_id))
    return render_template('transaction/edit.html', form=form, transaction=transaction, ledger=ledger)

@transaction_bp.route('/transaction/<int:id>/delete', methods=['POST'])
@login_required
def delete(id):
    transaction = Transaction.query.get_or_404(id)
    ledger = Ledger.query.get_or_404(transaction.ledger_id)
    if ledger.user_id != current_user.id:
        flash('您没有权限删除此交易记录', 'error')
        return redirect(url_for('ledger.index'))
    
    db.session.delete(transaction)
    db.session.commit()
    flash('交易记录已删除', 'success')
    return redirect(url_for('transaction.index', ledger_id=transaction.ledger_id))

@transaction_bp.route('/<int:ledger_id>/export')
@login_required
def export(ledger_id):
    ledger = Ledger.query.get_or_404(ledger_id)
    if ledger.user_id != current_user.id:
        flash('您没有权限访问此账本', 'danger')
        return redirect(url_for('ledger.index'))
    
    # 创建内存文件对象
    output = io.StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow(['日期', '类型', '金额', '分类', '描述'])
    
    # 写入数据
    for transaction in ledger.transactions:
        writer.writerow([
            transaction.date.strftime('%Y-%m-%d'),
            '收入' if transaction.transaction_type == 'income' else '支出',
            transaction.amount,
            transaction.category,
            transaction.description or ''
        ])
    
    # 准备下载
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode('utf-8-sig')),
        mimetype='text/csv',
        as_attachment=True,
        download_name=f'{ledger.name}_交易记录_{datetime.now().strftime("%Y%m%d")}.csv'
    )

@transaction_bp.route('/<int:ledger_id>/import', methods=['POST'])
@login_required
def import_transactions(ledger_id):
    ledger = Ledger.query.get_or_404(ledger_id)
    if ledger.user_id != current_user.id:
        flash('您没有权限访问此账本', 'danger')
        return redirect(url_for('ledger.index'))
    
    if 'file' not in request.files:
        flash('请选择要导入的文件', 'danger')
        return redirect(url_for('transaction.index', ledger_id=ledger_id))
    
    file = request.files['file']
    if file.filename == '':
        flash('未选择文件', 'danger')
        return redirect(url_for('transaction.index', ledger_id=ledger_id))
    
    if not file.filename.endswith('.csv'):
        flash('请上传CSV格式的文件', 'danger')
        return redirect(url_for('transaction.index', ledger_id=ledger_id))
    
    try:
        # 读取CSV文件
        content = file.read().decode('utf-8-sig')
        reader = csv.DictReader(content.splitlines())
        
        # 导入数据
        count = 0
        for row in reader:
            try:
                transaction = Transaction(
                    ledger_id=ledger_id,
                    date=datetime.strptime(row['日期'], '%Y-%m-%d'),
                    transaction_type='income' if row['类型'] == '收入' else 'expense',
                    amount=float(row['金额']),
                    category=row['分类'],
                    description=row['描述'] or None
                )
                db.session.add(transaction)
                count += 1
            except (ValueError, KeyError) as e:
                flash(f'导入第 {count + 1} 行数据时出错: {str(e)}', 'danger')
                continue
        
        db.session.commit()
        flash(f'成功导入 {count} 条交易记录', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'导入失败: {str(e)}', 'danger')
    
    return redirect(url_for('transaction.index', ledger_id=ledger_id))