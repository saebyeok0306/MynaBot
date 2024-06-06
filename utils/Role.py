def get_role_server_by_author(author):
    for role in author.guild.roles:
        if role.name == str(author.id):
            return role
    return False


async def delete_role_server_by_author(author, reason="회원탈퇴"):
    for role in author.guild.roles:
        if role.name == str(author.id):
            await role.delete(reason=f'역할 삭제 사유 : {reason}')
            return True
    return False


def get_role_author(author):
    for role in author.roles:
        if role.name == str(author.id):
            return role
    return False


async def create_role_author(author):
    default_color = 0x99aab5
    server_roles = [role for role in author.guild.roles]
    new_role = await author.guild.create_role(name=author.id, color=default_color, hoist=False)

    posIdx = len(server_roles) - 3 if len(server_roles) > 3 else len(server_roles)
    server_roles.insert(posIdx, new_role)
    position = {role: pos for pos, role in enumerate(server_roles)}
    await author.guild.edit_role_positions(positions=position)
    await author.add_roles(new_role)
    return new_role
