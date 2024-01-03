import sqlite3, datetime
import discord

def Connect(db_path = r'db/DiscordDB.db') -> sqlite3.Connection:
    return sqlite3.connect(db_path, isolation_level = None)

def GetUserByAuthor(author):
    con = Connect()
    cur = con.cursor()

    cur.execute("SELECT * FROM User WHERE id = ? AND guild_id = ?", (author.id, author.guild.id,))
    _user = cur.fetchone()

    con.close()

    return _user

def SaveUserDB(author):
    con = Connect()
    cur = con.cursor()
    if not GetUserByAuthor(author):
        cur.execute("INSERT INTO User VALUES (?, ?, ?)", (author.id, author.guild.id, author.display_name))
        con.close()
        return True
    else:
        cur.execute("UPDATE User SET username=? WHERE id=? AND guild_id=?", (author.display_name, author.id, author.guild.id))
        con.close()
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

def GetStatByAuthor(author):
    con = Connect()
    cur = con.cursor()

    cur.execute("SELECT * FROM Stat WHERE id = ? AND guild_id = ?", (author.id, author.guild.id,))
    _user = cur.fetchone()

    con.close()

    return _user

def SaveStatDB(author, level=1, exp=0):
    con = Connect()
    cur = con.cursor()
    author_id = (author.id, author.guild.id,)
    if not GetStatByAuthor(author):
        cur.execute("INSERT INTO Stat VALUES (?, ?, ?, ?)", (*author_id, level, exp))
        con.close()
        return True
    else:
        cur.execute("UPDATE Stat SET level=?, exp=? WHERE id=? AND guild_id=?", (level, exp, *author_id))
        con.close()
        return False

def DeleteStatByAuthor(author):
    if GetUserByAuthor(author):
        con = Connect()
        cur = con.cursor()
        author_id = (author.id, author.guild.id,)
        cur.execute("DELETE FROM Stat WHERE id = ? AND guild_id = ?", author_id)
        con.close()
        return True
    return False

def GetChatByAuthor(author):
    con = Connect()
    cur = con.cursor()

    cur.execute("SELECT * FROM Chat WHERE id = ? AND guild_id = ?", (author.id, author.guild.id,))
    _user = cur.fetchone()

    con.close()

    return _user

def GetChat():
    con = Connect()
    cur = con.cursor()

    cur.execute("SELECT * FROM Chat")
    _user = cur.fetchall()

    con.close()

    return _user

def SaveChatDB(author, history, database):
    con = Connect()
    cur = con.cursor()
    author_id = (author.id, author.guild.id,)
    if not GetChatByAuthor(author):
        cur.execute("INSERT INTO Chat VALUES (?, ?, ?, ?)", (*author_id, history, database))
        con.close()
        return True
    else:
        cur.execute("UPDATE Chat SET history=?, data=? WHERE id=? AND guild_id=? ", (history, database, *author_id))
        con.close()
        return False

def DeleteChatByAuthor(author):
    if GetChatByAuthor(author):
        con = Connect()
        cur = con.cursor()
        author_id = (author.id, author.guild.id,)
        cur.execute("DELETE FROM Chat WHERE id = ? AND guild_id = ?", author_id)
        con.close()
        return True
    return False

def GetMusicByGuild(guild):
    con = Connect()
    cur = con.cursor()

    cur.execute("SELECT * FROM Music WHERE guild_id = ?", (guild.id, ))
    _music = cur.fetchone()

    con.close()

    return _music

def GetMusic():
    con = Connect()
    cur = con.cursor()

    cur.execute("SELECT * FROM Music")
    _music = cur.fetchall()

    con.close()

    return _music

def SaveMusicDB(guild, is_playing):
    con = Connect()
    cur = con.cursor()
    if not GetMusicByGuild(guild):
        cur.execute("INSERT INTO Music VALUES (?, ?)", (guild.id, is_playing))
        con.close()
        return True
    else:
        cur.execute("UPDATE Music SET playing=? WHERE guild_id=? ", (is_playing, guild.id))
        con.close()
        return False

def GetMusicByGuild(guild):
    con = Connect()
    cur = con.cursor()

    cur.execute("SELECT * FROM Music WHERE guild_id=?", (guild.id, ))
    _music = cur.fetchone()

    con.close()

    return _music