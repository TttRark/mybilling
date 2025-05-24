from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from models import db, Transaction, Ledger
import pandas as pd
from datetime import datetime
import os
from werkzeug.utils import secure_filename

export_bp = Blueprint('export', __name__)

@export_bp.route('/ledger/<int:ledger_id>/export')
@login_required
def export_excel(ledger_id):
    ledger = Ledger.query.get_or_404(ledger_id)
    if ledger.user_id != current_user.id:
        flash('您没有权限导出此账本', 'error')
        return redirect(url_for('ledger.index'))
    
    transactions = Transaction.query.filter_by(ledger_id=ledger_id).all()
    
    # 创建DataFrame
    data = []
    for t in transactions:
        data.append({
            '日期': t.date.strftime('%Y-%m-%d'),
            '金额': t.amount,
            '类型': t.transaction_type,
            '分类': t.category,
            '描述': t.description
        })
    
    df = pd.DataFrame(data)
    
    # 创建Excel文件
    filename = f'ledger_{ledger_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx'
    filepath = os.path.join('temp', filename)
    os.makedirs('temp', exist_ok=True)
    
    df.to_excel(filepath, index=False)
    
    return send_file(filepath, as_attachment=True, download_name=filename)

@export_bp.route('/ledger/<int:ledger_id>/import', methods=['GET', 'POST'])
@login_required
def import_excel(ledger_id):
    ledger = Ledger.query.get_or_404(ledger_id)
    if ledger.user_id != current_user.id:
        flash('您没有权限导入数据到此账本', 'error')
        return redirect(url_for('ledger.index'))
    
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('没有选择文件', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            flash('没有选择文件', 'error')
            return redirect(request.url)
        
        if file and file.filename.endswith('.xlsx'):
            filename = secure_filename(file.filename)
            filepath = os.path.join('temp', filename)
            os.makedirs('temp', exist_ok=True)
            file.save(filepath)
            
            try:
                df = pd.read_excel(filepath)
                for _, row in df.iterrows():
                    transaction = Transaction(
                        amount=float(row['金额']),
                        description=row['描述'],
                        category=row['分类'],
                        transaction_type=row['类型'],
                        date=datetime.strptime(row['日期'], '%Y-%m-%d'),
                        ledger_id=ledger_id
                    )
                    db.session.add(transaction)
                
                db.session.commit()
                flash('数据导入成功！', 'success')
            except Exception as e:
                flash(f'导入失败：{str(e)}', 'error')
            finally:
                os.remove(filepath)
            
            return redirect(url_for('transaction.index', ledger_id=ledger_id))
        
        flash('请上传Excel文件(.xlsx)', 'error')
        return redirect(request.url)
    
    return render_template('export/import.html', ledger=ledger) 