import shutil
import sys
from pathlib import Path
from langchain_mcp_adapters.client import MultiServerMCPClient

# sales.db mutlak dosya yolu
DB_PATH = str(Path(__file__).resolve().parent.parent / "data" / "sales.db")

# Sanal ortamdaki mcp-server-sqlite calistirilabilir dosyasini bul
def get_mcp_server_command():
    # Once venv icindeki Scripts klasorune bak (Windows icin)
    venv_scripts = Path(sys.prefix) / "Scripts" / "mcp-server-sqlite.exe"
    if venv_scripts.exists():
        return str(venv_scripts)
    
    # Yoksa PATH uzerinden ara
    cmd = shutil.which("mcp-server-sqlite")
    if cmd:
        return cmd
        
    # En son care python modul olarak dene
    return sys.executable

async def get_sqlite_mcp_tools():
    """
    SQLite MCP sunucusunu baslatir ve LangChain uyumlu araclari dondurur.
    """
    cmd = get_mcp_server_command()
    
    # Eger dogrudan exe bulunduysa sadece parametreleri ver
    if cmd.endswith("mcp-server-sqlite.exe") or cmd.endswith("mcp-server-sqlite"):
        server_config = {
            "sqlite": {
                "command": cmd,
                "args": ["--db-path", DB_PATH],
                "transport": "stdio",
            }
        }
    else:
        # Fallback python -m
        server_config = {
            "sqlite": {
                "command": sys.executable,
                "args": ["-m", "mcp_server_sqlite.server", "--db-path", DB_PATH],
                "transport": "stdio",
            }
        }

    client = MultiServerMCPClient(server_config)
    tools = await client.get_tools()
    return tools

if __name__ == "__main__":
    import asyncio

    async def main():
        print(f"Baglanilacak Veritabani: {DB_PATH}")
        tools = await get_sqlite_mcp_tools()
        print(f"\nToplam {len(tools)} adet MCP araci yuklendi:")
        for t in tools:
            print(f" - {t.name}: {t.description}")

    asyncio.run(main())