import curses

# to be initialized by init_render
attributes = {}

ADD = 0
REMOVE = 1
REFRESH = 2
DELETE_WALLET = 3
EXIT = 4
MAIN_OPTIONS = ["Add", "Remove", "Refresh", "Delete wallet", "Exit"]
ENTER = 10
ESCAPE = 27

HEADER_START = (2, 5)
SUB_MENU_START = (4, 2)


def main_header(stdscr):
    stdscr.erase()
    stdscr.border()
    stdscr.addstr(HEADER_START[0], HEADER_START[1],
                  "CryptoWatch - Multi Cryptocurrency watch-only wallet", curses.A_UNDERLINE)


def init_render(stdscr):
    curses.curs_set(0)  # hide the cursor

    curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
    attributes['normal'] = curses.color_pair(1)

    curses.init_pair(2, curses.COLOR_BLACK, curses.COLOR_GREEN)
    attributes['highlighted'] = curses.color_pair(2)

    # set foreground and background colors to normal
    stdscr.bkgd(' ', attributes['normal'])


def display_options_bar(stdscr, y, x, options, highlight=-1, layout='vertical'):
    """
    Display options bar in row y starting from cell x

    :param options list of strings - the options to display
    :param highlight index of an option to highlight.
    :param y base row number
    :param x base column number
    :param layout how the options should be display. should be 'vertical' or 'horizontal'.
                  in vertical mode, each row starts with a number (sequentially)

    """
    if layout == 'vertical':
        for i in range(len(options)):
            if i == highlight:
                attr = attributes['highlighted']
            else:
                attr = attributes['normal']
            stdscr.addstr(y, x, str(i + 1) + '. ')
            stdscr.addstr(options[i], attr)
            y += 1

    elif layout == 'horizontal':
        for i in range(len(options)):
            if i == highlight:
                attr = attributes['highlighted']
            else:
                attr = attributes['normal']
            stdscr.addstr(y, x, options[i], attr)
            x += len(options[i]) + 2


COLUMNS_SPACE = 12


def display_coins_table(stdscr, y, x, coins):
    """
    Display the coins table starting from row y and column x.

    :param coins List of lists. each inner list is [coin_id, amount, value_usd, value_btc]

    number of lines written to screen is len(coins)+3
    """
    stdscr.addstr(y, x, "Coin        Amount      USD-value   BTC-value",
                  attributes['highlighted'])
    if len(coins) == 0:
        stdscr.addstr(y + 1, x, "Your wallet is empty. Choose 'Add' to add new coin")
        return

    for i, coin in enumerate(coins):
        for j in range(4):
            stdscr.addstr(y + 1 + i, x + (j * COLUMNS_SPACE), str(coin[j]))

    total_usd = 0
    total_btc = 0
    for i in range(len(coins)):
        if coins[i][2] is not None and coins[i][3] is not None:
            # actually it is guaranteed that both will be None, or both won't
            total_usd += coins[i][2]
            total_btc += coins[i][3]

    # truncate digits after point
    total_usd = float('%.3f' % total_usd)
    total_btc = float('%.8f' % total_btc)

    stdscr.addstr(y + len(coins) + 2, x, "Total Balance: ")
    stdscr.addstr("{0} USD, {1} BTC".format(total_usd, total_btc))


def display_main_scr(stdscr, coins, option=0):
    """
    Display the main screen - a table with all coins and amounts, and list of options

    :param coins: list of lists. Each inner list correspond to a single coin
                  and looks like this: [coin_code, amount, value_in_usd, value_in_btc]
    :param option the option to be initially chosen
    :return: the option chosen by the user
    """

    c = 0  # last character read
    should_render = True  # for the first time drawing

    while c != ENTER:
        if should_render:
            main_header(stdscr)
            display_coins_table(stdscr, SUB_MENU_START[0], SUB_MENU_START[1], coins)
            display_options_bar(stdscr, SUB_MENU_START[0] + len(coins) + 5, SUB_MENU_START[1],
                                MAIN_OPTIONS, highlight=option, layout='horizontal')
            stdscr.refresh()
            should_render = False

        c = stdscr.getch()

        # todo add support to number pressing. if user click 3, option 3 will be marked
        if c == curses.KEY_LEFT and option > 0:
            option -= 1
            should_render = True
        elif c == curses.KEY_RIGHT and option < len(MAIN_OPTIONS) - 1:
            option += 1
            should_render = True
        elif c == curses.KEY_RESIZE:
            should_render = True

    return option


def add_menu_header(stdscr):
    """
    Displays the header for the add coin menu
    """
    main_header(stdscr)
    stdscr.addstr(SUB_MENU_START[0], SUB_MENU_START[1], "Add coin:")
    stdscr.refresh()


def display_add_scr(stdscr, wallet):
    """
    Display the 'add coin' screen to the user and handles adding new coin

    :param wallet: Wallet object to which coins should be added
    :param y_base the first row to draw from
    :param x_base the first column to draw from
    """
    c = 0  # last character read
    option = 0

    while c != ESCAPE and c != ENTER:
        add_menu_header(stdscr)
        display_options_bar(stdscr, SUB_MENU_START[0], SUB_MENU_START[1],
                            ["Add addresses to watch", "Add balance manually"], option, 'vertical')

        c = stdscr.getch()

        # todo add support to number pressing
        if c == curses.KEY_UP and option > 0:
            option -= 1
        elif c == curses.KEY_DOWN and option < 1:
            option += 1

    if c == ESCAPE:
        return

    last_line = SUB_MENU_START[0]  # the last line we wrote to
    try:
        curses.echo()  # so the user sees what he types
        curses.curs_set(1)

        add_menu_header(stdscr)
        stdscr.addstr(last_line + 2, SUB_MENU_START[1],
                      "Enter coin code/symbol (e.g. BTC): ")
        last_line += 2
        coin_code = stdscr.getstr().decode("utf-8")

        if option == 0:
            stdscr.addstr(last_line + 2, SUB_MENU_START[1],
                          "Enter addresses to watch (comma separated, e.g. addr1,addr2,addr3):")
            last_line += 2
            stdscr.move(last_line + 1, SUB_MENU_START[1])
            last_line += 1
            addresses = stdscr.getstr().decode("utf-8")
            addresses = "".join(addresses.split())  # remove any whitespaces
            addresses = addresses.split(',')
            wallet.add_watch_address(coin_code, addresses)
        else:
            # manually add balance
            stdscr.addstr(last_line + 2, SUB_MENU_START[1], "Enter amount to add: ")
            last_line += 2
            amount = float(stdscr.getstr().decode("utf-8"))
            wallet.add_manual_balance(coin_code, amount)

        curses.curs_set(0)
        curses.noecho()
    except Exception:
        curses.curs_set(0)
        curses.noecho()
        return None
