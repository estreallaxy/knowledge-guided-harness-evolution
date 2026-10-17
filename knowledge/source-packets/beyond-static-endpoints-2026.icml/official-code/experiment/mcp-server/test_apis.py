#!/usr/bin/env python3
"""
API测试脚本
支持测试Directus、Memos和MinIO的API功能
"""
import asyncio
import sys
import json
from pathlib import Path
from typing import Dict, Any, List

# 添加当前目录到Python路径
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from tools import (
    initialize_tools,
    directus_get_draft_articles,
    directus_update_articles_author,
    memos_get_memos,
    memos_update_visibility,
    minio_upload_object,
    minio_get_object
)


class APITester:
    """API测试类"""
    
    def __init__(self):
        self.test_results = {}
    
    def print_separator(self, title: str = ""):
        """打印分隔线"""
        print("=" * 60)
        if title:
            print(f" {title} ")
            print("=" * 60)
    
    def print_result(self, test_name: str, result: Dict[str, Any]):
        """打印测试结果"""
        print(f"\n📋 {test_name} 测试结果:")
        print("-" * 40)
        
        if result.get("success"):
            print("✅ 测试成功")
            if "data" in result:
                # 检查是否是MinIO下载的数据（字符串类型）
                if isinstance(result["data"], str):
                    print(f"📄 文件内容长度: {len(result['data'])} 字符")
                    if "object_name" in result:
                        print(f"📁 对象名称: {result['object_name']}")
                else:
                    # 处理其他类型的数据（如列表）
                    print(f"📊 数据条数: {result.get('count', 0)}")
                    if result.get('count', 0) > 0:
                        print("📄 数据预览:")
                        data = result["data"]
                        if isinstance(data, list) and len(data) > 0:
                            # 只显示前3条数据
                            for i, item in enumerate(data[:3]):
                                print(f"  {i+1}. {json.dumps(item, ensure_ascii=False, indent=2)}")
                            if len(data) > 3:
                                print(f"  ... 还有 {len(data) - 3} 条数据")
                        else:
                            print(f"  {json.dumps(data, ensure_ascii=False, indent=2)}")
            elif "message" in result:
                print(f"💬 {result['message']}")
            elif "token" in result:
                print(f"🔑 Token: {result['token'][:20]}...")
        else:
            print("❌ 测试失败")
            print(f"🚨 错误信息: {result.get('error', '未知错误')}")
        
        self.test_results[test_name] = result
    
    async def test_directus(self):
        """测试Directus API"""
        self.print_separator("Directus API 测试")
        
        print("📄 步骤1: 获取草稿文章列表...")
        articles_result = await directus_get_draft_articles()
        self.print_result("Directus草稿文章", articles_result)
        
        if not articles_result.get("success"):
            print("❌ 获取草稿文章失败，无法继续测试")
            return
        
        articles = articles_result.get("data", [])
        if not articles:
            print("⚠️ 没有找到草稿文章，跳过更新测试")
            return
        
        print(f"\n🔄 步骤2: 更新文章作者为ID=1...")
        article_ids = [article.get("id") for article in articles if article.get("id")]
        if article_ids:
            update_result = await directus_update_articles_author(article_ids, 1)
            self.print_result("Directus更新作者", update_result)
        else:
            print("⚠️ 没有有效的文章ID，跳过更新测试")
    
    async def test_memos(self):
        """测试Memos API"""
        self.print_separator("Memos API 测试")
        
        print("📝 步骤1: 获取备忘录列表...")
        memos_result = await memos_get_memos()
        self.print_result("Memos备忘录列表", memos_result)
        
        if not memos_result.get("success"):
            print("❌ 获取备忘录列表失败，无法继续测试")
            return
        
        memos = memos_result.get("data", [])
        if not memos:
            print("⚠️ 没有找到备忘录，跳过更新测试")
            return
        
        print(f"\n🔄 步骤2: 更新备忘录可见性为PUBLIC...")
        updated_count = 0
        failed_count = 0
        
        for i, memo in enumerate(memos):
            memo_name = memo.get("name", "")
            if not memo_name:
                print(f"⚠️ 备忘录 {i+1} 没有名称，跳过")
                continue
            
            print(f"  正在更新备忘录: {memo_name}")
            update_result = await memos_update_visibility(memo_name, "PUBLIC")
            
            if update_result.get("success"):
                updated_count += 1
                print(f"  ✅ {memo_name} 更新成功")
            else:
                failed_count += 1
                print(f"  ❌ {memo_name} 更新失败: {update_result.get('error', '未知错误')}")
        
        print(f"\n📊 更新结果统计:")
        print(f"  ✅ 成功: {updated_count} 个")
        print(f"  ❌ 失败: {failed_count} 个")
        print(f"  📝 总计: {len(memos)} 个")
    
    def test_minio(self):
        """测试MinIO API"""
        self.print_separator("MinIO API 测试")
        
        test_content = "Hello MinIO from MCP Server Test!"
        object_name = "hello.txt"
        
        print(f"📤 步骤1: 上传文件 {object_name}...")
        upload_result = minio_upload_object(object_name, test_content)
        self.print_result("MinIO文件上传", upload_result)
        
        if not upload_result.get("success"):
            print("❌ 文件上传失败，无法继续测试")
            return
        
        print(f"\n📥 步骤2: 下载文件 {object_name}...")
        download_result = minio_get_object(object_name)
        self.print_result("MinIO文件下载", download_result)
        
        if download_result.get("success"):
            downloaded_content = download_result.get("data", "")
            print(f"💬 文件 {object_name} 下载成功")
            print(f"📄 文件大小: {len(downloaded_content)} 字节")
            if downloaded_content == test_content:
                print("✅ 文件内容验证成功")
            else:
                print("⚠️ 文件内容验证失败")
                print(f"期望: {test_content}")
                print(f"实际: {downloaded_content}")
    
    def print_menu(self):
        """打印菜单"""
        self.print_separator("API 测试工具")
        print("请选择要测试的API:")
        print("1. Directus API (草稿文章列表 + 更新作者)")
        print("2. Memos API (备忘录列表 + 更新可见性)")
        print("3. MinIO API (文件上传 + 下载)")
        print("4. 测试所有API")
        print("0. 退出")
        print("-" * 60)
    
    def print_summary(self):
        """打印测试总结"""
        self.print_separator("测试总结")
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result.get("success"))
        failed_tests = total_tests - successful_tests
        
        print(f"📊 测试统计:")
        print(f"  总测试数: {total_tests}")
        print(f"  成功: {successful_tests}")
        print(f"  失败: {failed_tests}")
        print(f"  成功率: {(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "  成功率: 0%")
        
        if failed_tests > 0:
            print(f"\n❌ 失败的测试:")
            for test_name, result in self.test_results.items():
                if not result.get("success"):
                    print(f"  - {test_name}: {result.get('error', '未知错误')}")
    
    async def run_test(self, choice: str):
        """运行指定的测试"""
        if choice == "1":
            await self.test_directus()
        elif choice == "2":
            await self.test_memos()
        elif choice == "3":
            self.test_minio()
        elif choice == "4":
            await self.test_directus()
            await self.test_memos()
            self.test_minio()
        else:
            print("❌ 无效的选择")
    
    async def run(self):
        """运行测试工具"""
        try:
            print("🚀 正在初始化API工具...")
            initialize_tools()
            print("✅ 初始化完成")
            
            while True:
                self.print_menu()
                choice = input("请输入选择 (0-4): ").strip()
                
                if choice == "0":
                    print("👋 再见!")
                    break
                elif choice in ["1", "2", "3", "4"]:
                    await self.run_test(choice)
                    self.print_summary()
                    
                    if choice != "4":  # 如果不是测试所有API，询问是否继续
                        continue_choice = input("\n是否继续测试? (y/n): ").strip().lower()
                        if continue_choice not in ['y', 'yes', '是']:
                            print("👋 再见!")
                            break
                else:
                    print("❌ 无效的选择，请重新输入")
                
                print("\n" + "="*60)
        
        except KeyboardInterrupt:
            print("\n\n👋 用户中断，再见!")
        except Exception as e:
            print(f"\n❌ 程序运行出错: {e}")
            sys.exit(1)


async def main():
    """主函数"""
    tester = APITester()
    await tester.run()


if __name__ == "__main__":
    asyncio.run(main())
