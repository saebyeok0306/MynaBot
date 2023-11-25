import sqlite3, datetime
import discord

def Connect(db_path = r'data/DiscordDB.db') -> sqlite3.Connection:
    return sqlite3.connect(db_path, isolation_level = None)

def GetUserByAuthor(author):
    con = Connect()
    cur = con.cursor()

    cur.execute("SELECT * FROM User WHERE id = ? AND guild_id = ?", (author.id, author.guild.id,))
    _user = cur.fetchone()

    con.close()

    return _user

def SaveUserDB(author):
    if not GetUserByAuthor(author):
        con = Connect()
        cur = con.cursor()
        cur.execute("INSERT INTO User VALUES (?, ?, ?)", (author.id, author.guild.id, author.display_name))
        con.close()
        return True
    return False

def DeleteUserByAuthor(author):
    if GetUserByAuthor(author):
        con = Connect()
        cur = con.cursor()
        author_id = (author.id, author.guild.id,)
        cur.execute("DELETE FROM User WHERE id = ? AND guild_id = ?", author_id)
        con.close()
        return True
    return False

def SaveUserDBAtGuild(guild):
    """Save all users in guilds to database"""
    for author in guild.members:
        # if guild.id != 966942556078354502: continue
        if author.bot: continue
        SaveUserDB(author)

def GetRoleServerByAuthor(author):
    for role in author.guild.roles:
        if role.name == str(author.id):
            return role
    return False

async def DeleteRoleServerByAuthor(author, reason="회원탈퇴"):
    for role in author.guild.roles:
        if role.name == str(author.id):
            await role.delete(reason=f'역할 삭제 사유 : {reason}')
            return True
    return False


def GetRoleAuthor(author):
    for role in author.roles:
        if role.name == str(author.id):
            return role
    return False

async def CreateRoleServer(author):
    default_color = 0x99aab5
    server_roles = [ role for role in author.guild.roles ]
    new_role = await author.guild.create_role(name=author.id, color=default_color, hoist=False)

    posIdx = len(server_roles)-3 if len(server_roles) > 3 else len(server_roles)
    server_roles.insert(posIdx, new_role)
    position = {role : pos for pos, role in enumerate(server_roles)}
    await author.guild.edit_role_positions(positions=position)
    await author.add_roles(new_role)
    return new_role