"""
数据库迁移脚本：添加member_type字段
"""
from sqlalchemy import text  # 导入text用于执行原生SQL
from app.core.database import engine  # 导入数据库引擎

def migrate_database():
    """执行数据库迁移，添加member_type字段"""
    with engine.connect() as conn:
        # 检查member_type列是否已存在
        result = conn.execute(text("SHOW COLUMNS FROM users LIKE 'member_type'"))
        exists = result.fetchone()
        
        if not exists:
            print("添加 member_type 列...")
            # 添加member_type列（使用VARCHAR而不是ENUM，以便更好地兼容）
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN member_type VARCHAR(10) NOT NULL DEFAULT 'normal'
            """))
            
            # 更新所有现有用户的member_type为normal
            conn.execute(text("""
                UPDATE users 
                SET member_type = 'normal' 
                WHERE member_type IS NULL OR member_type = ''
            """))
            
            print("[OK] member_type 列已添加并设置为 'normal'")
        else:
            print("[OK] member_type 列已存在")
        
        # 提交事务
        conn.commit()
        print("\n迁移完成！")

if __name__ == "__main__":
    print("=" * 50)
    print("开始数据库迁移...")
    print("=" * 50)
    try:
        migrate_database()
        print("\n" + "=" * 50)
        print("迁移成功！")
        print("=" * 50)
    except Exception as e:
        print(f"\n迁移失败：{e}")
        import traceback
        traceback.print_exc()

