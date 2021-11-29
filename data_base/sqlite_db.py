import sqlite3 as sq
from create_bot import bot
from parsing import stocks_parsing as sp
from keyboards import kb_client
from keyboards import kb_buy_stock
from keyboards import kb_portfolio


def sql_start():
    global base, cur
    base = sq.connect('tinkoff_prices.dp')
    cur = base.cursor()
    if base:
        print('Db connected!')
    base.execute('CREATE TABLE IF NOT EXISTS prices(name TEXT PRIMARY KEY, price TEXT, fibi TEXT, cn TEXT, low_name '
                 'TEXT, ticker TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS last_stock(usr TEXT PRIMARY KEY, stock TEXT)')
    base.commit()


async def sql_create_user_table(message):
    test = 'CREATE TABLE IF NOT EXISTS ' + str(message.from_user.username) + '(name TEXT PRIMARY KEY, count TEXT)'
    base.execute('CREATE TABLE IF NOT EXISTS ' + str(message.from_user.username)
                 + '(name TEXT PRIMARY KEY, count TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS top(name TEXT PRIMARY KEY, money TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS ids(name TEXT PRIMARY KEY, id TEXT)')
    base.commit()
    try:
        cur.execute('INSERT INTO top VALUES (?, ?)', (str(message.from_user.username), '0'))
    except:
        pass
    try:
        cur.execute('INSERT INTO ' + str(message.from_user.username) + ' VALUES (?, ?)', ('usd', '1000000'))
    except:
        pass
    try:
        cur.execute('INSERT INTO last_stock VALUES (?, ?)', (str(message.from_user.username), 'empty'))
    except:
        pass
    try:
        cur.execute('INSERT INTO ids VALUES (?, ?)', (str(message.from_user.username), str(message.from_user.id)))
    except:
        pass
    base.commit()


async def sql_print_user_table(message):
    await sql_create_user_table(message)
    res = "Ваш портфель\n\n"
    for ret in cur.execute('SELECT * FROM ' + str(message.from_user.username)).fetchall():
        cnt = 0
        if ret[0] != 'usd':
            cnt = '{:.0f}'.format(float(ret[1]))
        else:
            cnt = '{:.3f}'.format(float(ret[1]))
        if cnt == "0" and ret[0] != 'usd':
            continue
        res += ret[0] + '   ' + cnt
        if ret[0] != 'usd':
            res += ' акций'
        res += '\n'
    await bot.send_message(message.from_user.id, res, reply_markup=kb_portfolio)


async def sql_count_user_table(message):
    await sql_create_user_table(message)
    res = 0
    for ret in cur.execute('SELECT * FROM ' + str(message.from_user.username)).fetchall():
        if ret[0] == 'usd':
            res += float(ret[1])
            continue
        await sql_update(ret[0])
        r = cur.execute('SELECT price FROM prices WHERE name == ?', (ret[0],)).fetchone()[0]
        r = float(await convert(r, cur.execute('SELECT cn FROM prices WHERE name == ?', (ret[0],)).fetchone()[0]))
        r *= float(ret[1])
        res += r
    cur.execute('UPDATE top SET money == ? WHERE name == ?', (str(res), str(message.from_user.username)))
    await bot.send_message(message.from_user.id, 'Стоимость вашего портфеля равна ' + str(res) + ' usd',
                           reply_markup=kb_client)


async def sql_count_user_table_without_message(username):
    res = 0
    for ret in cur.execute('SELECT * FROM ' + username).fetchall():
        if ret[0] == 'usd':
            res += float(ret[1])
            continue
        await sql_update(ret[0])
        r = cur.execute('SELECT price FROM prices WHERE name == ?', (ret[0],)).fetchone()[0]
        r = float(await convert(r, cur.execute('SELECT cn FROM prices WHERE name == ?', (ret[0],)).fetchone()[0]))
        r *= float(ret[1])
        res += r
    test = str(res)
    cur.execute('UPDATE top SET money == ? WHERE name == ?', (str(res), username))


async def sql_add_command(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO menu VALUES (?, ?)', tuple(data.values()))
        base.commit()


async def sql_read(message, ind):
    res = ''
    ind_0 = 0
    for ret in cur.execute('SELECT * FROM prices').fetchall():
        ss = ret[1]
        if ss == 'err':
            ss = ""
        else:
            ss = await convert(ss, ret[3])
            ss += ' usd'
        t = ret[0]
        res += ret[5] + max(3, 15 - len(ret[5])) * ' ' + t + max(3, (15 - len(t))) * ' ' + ss + '\n'
        if len(res) > 1000:
            if ind_0 == ind:
                await bot.send_message(message.from_user.id, res)
                return False
            res = ""
            ind_0 += 1


async def convert(price, cn):
    price = float(price)
    usd = float(sp.c.get_market_orderbook("BBG0013HGFT4", 1).payload.last_price)  # цена доллара из стакана, имхо
    eur = 85.5
    if cn == 'rub':
        price /= usd
    if cn == 'eur':
        price *= usd / eur
    price = float('{:.3f}'.format(price))
    return str(price)


async def sql_read_one(message, name):
    res = ''
    r = cur.execute('SELECT price FROM prices WHERE name == ?', (name,)).fetchone()
    rr = cur.execute('SELECT cn FROM prices WHERE name == ?', (name,)).fetchone()
    try:
        price = r[0]
        if rr[0] != 'usd':
            price = await convert(price, rr[0])
        res += name + (max(15 - len(name), 3)) * ' ' + price + ' ' + 'usd' + '\n'
        cnt = "0"
        try:
            cnt = cur.execute('SELECT count FROM ' + str(message.from_user.username) + ' WHERE name == ?',
                              (name,)).fetchone()[0]
        except:
            pass
        res += '\n'
        res += 'У вас ' + '{:.0f}'.format(float(cnt))
        await bot.send_message(message.from_user.id, res, reply_markup=kb_buy_stock)
        cur.execute('UPDATE last_stock SET stock == ? WHERE usr == ?', (name, str(message.from_user.username)))
        return True
    except:
        await bot.send_message(message.from_user.id, "Неправильное название", reply_markup=kb_client)
        return False


async def check_and_add(name, fibi='', cn='', ticker=''):
    for ret in cur.execute('SELECT * FROM prices').fetchall():
        if ret[0] == name:
            return
    cur.execute('INSERT INTO prices VALUES (?, ?, ?, ?, ?, ?)', (name, 'err', fibi, cn, name.lower(), ticker))
    base.commit()


async def sql_update(name):
    r = cur.execute('SELECT fibi FROM prices WHERE name == ?', (name,))
    try:
        price = float(sp.c.get_market_orderbook(r, 1).payload.last_price)
        cur.execute('UPDATE prices SET price == ? WHERE name == ?', (str(price), name))
    except:
        pass


async def sql_find_real_name(name):
    real_name = ""
    for ret in cur.execute('SELECT * FROM prices').fetchall():
        if name.lower() in ret[0].lower():
            real_name = ret[0]
    for ret in cur.execute('SELECT * FROM prices').fetchall():
        if name.lower() == ret[5].lower():
            real_name = ret[0]
    return real_name


async def sql_buy_stock(message):
    await sql_create_user_table(message)
    stock_name = \
        cur.execute('SELECT stock FROM last_stock WHERE usr == ?', (str(message.from_user.username),)).fetchone()[0]
    stock_price = cur.execute('SELECT price FROM prices WHERE name == ?', (stock_name,)).fetchone()[0]
    stock_price = float(await convert(stock_price,
                                      cur.execute('SELECT cn FROM prices WHERE name == ?', (stock_name,)).fetchone()[
                                          0]))
    count = float(message.text)
    delta = count * stock_price
    amount_of_money = float(cur.execute('SELECT count FROM ' + str(message.from_user.username) + ' WHERE name == ?',
                                        ('usd',)).fetchone()[0])
    mx = int(amount_of_money / stock_price)
    if count > mx:
        await bot.send_message(message.from_user.id, "У вас не хватает средств")
        return False
    amount_of_money -= delta
    cur.execute('UPDATE ' + str(message.from_user.username) + ' SET count == ? WHERE name == ?',
                (str(amount_of_money), 'usd'))
    try:
        cur.execute('INSERT INTO ' + str(message.from_user.username) + ' VALUES (?, ?)', (stock_name, str(count)))
    except:
        adding = float(cur.execute('SELECT count FROM ' + str(message.from_user.username) + ' WHERE name == ?',
                                   (stock_name,)).fetchone()[0])
        count += adding
        cur.execute('UPDATE ' + str(message.from_user.username) + ' SET count == ? WHERE name == ?',
                    (str(count), stock_name))
    await bot.send_message(message.from_user.id, "Сделка завершена", reply_markup=kb_client)
    return True


async def sql_sell_stock(message):
    await sql_create_user_table(message)
    stock_name = \
        cur.execute('SELECT stock FROM last_stock WHERE usr == ?', (str(message.from_user.username),)).fetchone()[0]
    stock_price = cur.execute('SELECT price FROM prices WHERE name == ?', (stock_name,)).fetchone()[0]
    stock_price = float(await convert(stock_price,
                                      cur.execute('SELECT cn FROM prices WHERE name == ?', (stock_name,)).fetchone()[
                                          0]))
    count = float(message.text)
    delta = count * stock_price
    amount_of_money = float(cur.execute('SELECT count FROM ' + str(message.from_user.username) + ' WHERE name == ?',
                                        ('usd',)).fetchone()[0])
    adding = 0
    try:
        adding = float(cur.execute('SELECT count FROM ' + str(message.from_user.username) + ' WHERE name == ?',
                                   (stock_name,)).fetchone()[0])
    except:
        pass
    if adding < count:
        await bot.send_message(message.from_user.id, "У вас нету такого количества акций")
        return False
    amount_of_money += delta
    cur.execute('UPDATE ' + str(message.from_user.username) + ' SET count == ? WHERE name == ?',
                (str(amount_of_money), 'usd'))

    count = adding - count
    cur.execute('UPDATE ' + str(message.from_user.username) + ' SET count == ? WHERE name == ?',
                (str(count), stock_name))

    await bot.send_message(message.from_user.id, "Сделка завершена", reply_markup=kb_client)
    return True


async def sql_mx_buy(message):
    await sql_create_user_table(message)
    stock_name = \
        cur.execute('SELECT stock FROM last_stock WHERE usr == ?', (str(message.from_user.username),)).fetchone()[0]
    stock_price = cur.execute('SELECT price FROM prices WHERE name == ?', (stock_name,)).fetchone()[0]
    stock_price = float(await convert(stock_price,
                                      cur.execute('SELECT cn FROM prices WHERE name == ?', (stock_name,)).fetchone()[
                                          0]))
    amount_of_money = float(cur.execute('SELECT count FROM ' + str(message.from_user.username) + ' WHERE name == ?',
                                        ('usd',)).fetchone()[0])
    mx = int(amount_of_money / stock_price)
    return mx


async def sql_update_top():
    users = []
    for ret in cur.execute('SELECT * FROM top').fetchall():
        users.append(ret[0])
    for us in users:
        await sql_count_user_table_without_message(us)


async def sql_top_traders(message):
    res = ""
    await sql_update_top()
    for ret in cur.execute('SELECT * FROM top').fetchall():
        res += ret[0] + ' ' + ret[1] + ' usd\n'
    await bot.send_message(message.from_user.id, res, reply_markup=kb_client)


async def sql_top_competitors(competitors):
    arr = []
    await sql_update_top()
    for cm in competitors:
        await sql_count_user_table_without_message(cm)
        money = cur.execute('SELECT money FROM top WHERE name == ?', (cm,)).fetchone()[0]
        arr.append([money, cm])
    arr = sorted(arr)
    arr = reversed(arr)
    res = ''
    for el in arr:
        res += el[1] + '   ' + el[0] + '\n'
    return res


async def sql_users():
    users = []
    for ret in cur.execute('SELECT * FROM last_stock').fetchall():
        users.append(ret[0])
    return users


async def sql_users_info():
    ids = []
    for ret in cur.execute('SELECT * FROM ids').fetchall():
        ids.append(ret)
    return ids


async def sql_user_prepare_competition(user):
    cur.execute('DELETE FROM ' + user)
    cur.execute('INSERT INTO ' + user + ' VALUES (?, ?)', ('usd', '1000000'))


async def sql_create_user_table_0(username, user_id):
    test = 'CREATE TABLE IF NOT EXISTS ' + username + '(name TEXT PRIMARY KEY, count TEXT)'
    base.execute('CREATE TABLE IF NOT EXISTS ' + username
                 + '(name TEXT PRIMARY KEY, count TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS top(name TEXT PRIMARY KEY, money TEXT)')
    base.execute('CREATE TABLE IF NOT EXISTS ids(name TEXT PRIMARY KEY, id TEXT)')
    base.commit()
    try:
        cur.execute('INSERT INTO top VALUES (?, ?)', (username, '0'))
    except:
        pass
    try:
        cur.execute('INSERT INTO ' + username + ' VALUES (?, ?)', ('usd', '1000000'))
    except:
        pass
    try:
        cur.execute('INSERT INTO last_stock VALUES (?, ?)', (username, 'empty'))
    except:
        pass
    try:
        cur.execute('INSERT INTO ids VALUES (?, ?)', (username, user_id))
    except:
        pass
    base.commit()
