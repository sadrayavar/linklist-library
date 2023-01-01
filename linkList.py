import random
import string


class LibraryBackEnd:
    database = None
    first = None
    last = None
    emptyRows = []

    def __init__(self, databaseName, newFile=False):
        if newFile is False:
            # read database
            rows = open(databaseName, 'r').readlines()

            # search for first and last
            for i in range(len(rows)):

                # convert string to list
                rows[i] = self.stringToList(
                    rows[i])
                if rows[i][0] == 'None':  # set first
                    self.first = i
                if rows[i][1] == 'None':  # set last
                    self.last = i

            if (self.first == None):
                print('Database does not have a first book')
            if (self.last == None):
                print('Database does not have a last book')
            if not (self.first == None or self.last == None):
                self.database = databaseName
        else:
            try:  # create database
                open(databaseName, 'x')
            except:  # delete current database contents
                open(databaseName, 'w').write('')
            self.database = databaseName
            self.first = 1

    def add(self, ISBN, title, author, publisher, pubDate, category, supply, people):
        '''
        data:
        last book place
        next empty row = last book place (after add)

        functions:
        1- get next empty row
        2- edit last book to point to the next empty row
        3- insert book to the next empty row
        4- update last book place
        '''
        lastBookPlace = self.last
        nextEmptyRow = None

        # get next empty row
        if (len(self.emptyRows) == 0):
            if (self.last == None):
                nextEmptyRow = 1
            else:
                tempLines = open(self.database, 'r').readlines()
                nextEmptyRow = len(tempLines)+1
        else:
            nextEmptyRow = self.emptyRows.pop()

        # edit last book to point to the next empty row
        if (lastBookPlace != None):
            lastBook = self.readFromDatabase(lastBookPlace)
            lastBook[1] = nextEmptyRow
            self.writeToDatabase(lastBook, lastBookPlace)

        # insert book to the next empty row
        book = self.paramToString(
            lastBookPlace, None, ISBN, title, author, publisher, pubDate, category, supply, people)
        self.writeToDatabase(book, nextEmptyRow)

        # update last book place
        self.last = nextEmptyRow

    def remove(self, rowList):
        def temp(where):
            # define book and bookplace
            place = self.search('ISBN', where)[0]
            this = self.readFromDatabase(place)

            # define former book
            former = self.readFromDatabase(this[0])
            former[1] = this[1]
            self.writeToDatabase(former, this[0])

            # define next book
            next = self.readFromDatabase(this[1])
            next[0] = this[0]
            self.writeToDatabase(next, this[1])

            # edit book
            self.writeToDatabase('\n', place)

            # add empty row to emptyRows list
            self.emptyRows.append(place)

        if isinstance(rowList, list):
            for row in rowList:
                temp(row)
        else:
            temp(rowList)

    def search(self, searchParam, value):
        if (searchParam == 'ISBN'):
            key = 2
        elif (searchParam == 'title'):
            key = 3
        elif (searchParam == 'author'):
            key = 4
        elif (searchParam == 'publisher'):
            key = 5
        elif (searchParam == 'pubDate'):
            key = 6
        elif (searchParam == 'category'):
            key = 7
        elif (searchParam == 'supply'):
            key = 8
        elif (searchParam == 'people'):
            key = 9
        else:
            print('search parameter must be one of the values below:\ntitle\nauthor\npublisher\npubDate\ncategory\nsupply\npeople')
            exit()

        output = []
        where = self.first
        canBreak = False

        def turnBookItemsToList(book):
            for i in range(len(book)):  # turn not list keys to list
                if (not (isinstance(book[i], list))):
                    temp = []
                    temp.append(book[i])
                    book[i] = temp

        while (where != 'None'):
            book = self.readFromDatabase(where)
            if (book == None):  # returns None if database is empty
                return False

            turnBookItemsToList(book)

            for item in book[key]:
                if (value == item):  # add to output list
                    output.append(where)
                    where = book[1][0]
                    break
                elif (book[1][0] == 'None'):
                    canBreak = True
                    break
            where = book[1][0]
            if (canBreak):
                break

        if (len(output) == 0):
            return False
        else:
            return output

    def sort(self):
        pass

    def edit(self):
        pass

    # helper methods

    def readFromDatabase(self, where):
        where -= 1
        try:
            rows = open(self.database, 'r').readlines()
            return self.stringToList(rows[where])
        except:
            return None

    def writeToDatabase(self, what, where):
        where -= 1
        if (not (isinstance(what, str))):
            what = self.paramToString(
                what[0], what[1], what[2], what[3], what[4], what[5], what[6], what[7], what[8], what[9])

        rows = open(self.database, 'r').readlines()

        if (len(rows) <= where):
            rows.append(what)
        else:
            rows[where] = what

        file = open(self.database, 'w')
        file.writelines(rows)
        file.close()

    def stringToList(self, book):
        book = book.split(',')
        book[-1] = book[-1].split(':')
        book[-3] = book[-3].split(':')
        for i in range(len(book[-1])):
            try:
                book[-1][i] = int(book[-1][i])
            except:
                pass
        for i in range(len(book)-1):
            try:
                book[i] = int(book[i])
            except:
                pass
        return book

    def paramToString(self, former, next, ISBN, title, author, publisher, pubDate, category, supply, people):
        def temp(list):
            return ':'.join(str(item) for item in list)
        return f'{former},{next},{ISBN},{title},{author},{publisher},{pubDate},{temp(category)},{supply},{temp(people)}\n'


class LibraryFrontEnd:
    back = None
    border = '\n##########################\n'
    ranValue = False

    def __init__(self):
        self.back = self.configDatabase()
        self.talkToMe()

    def configDatabase(self):
        file = None
        inp = None
        print('\n\nWelcome!')
        while not (inp == '1' or inp == '2'):
            print(
                f'\n{self.border}\nSelect start method:\n1- Create a new database\n2- Import database')
            inp = input()
            if (inp == '1'):
                print(
                    '\nYour Database is created with the name of: library-database.csv')
                file = LibraryBackEnd('library-database.csv', True)
            elif (inp == '2'):
                while file == None:
                    print('Enter your database name:')
                    fileName = input()
                    fileNameIsCorrect = True
                    if (fileNameIsCorrect):
                        print('Your Database is connecting to app...\n')
                        file = LibraryBackEnd(fileName)
                        if (file.database == None):
                            print(f'\nStandard database format:\nformer,next,ISBN,title,author,publisher,pubDate,category1:...,supply,personID1:...\nand also should have exactly one first and one last\nexample:\nNone,2,...\n1,None,...')
                            file = None
                    else:
                        print(
                            f'\nYour database name is incorrect\n{self.border}')
        print(f'\nNow lets manage this library\n{self.border}')
        return file

    def talkToMe(self):
        while True:
            print(
                'Select one of the options below:\n1- add\n2- remove\n3- search\n4- display')
            inp = input()

            if (inp == '1'):
                self.addBook()
            elif (inp == '2'):
                self.removeBook()
            elif (inp == '3'):
                self.searchBook()
            elif (inp == '4'):
                self.displayBooks()
            else:
                print('Please pay attension here')

            break
        print(self.border)
        self.talkToMe()

    def addBook(self):

        def inputString(what, rang):
            key = None
            while key == None:
                if self.ranValue == False:
                    print(f'Enter {what}:')
                    key = input()
                if key == 'r' or self.ranValue == True:
                    self.ranValue = True
                    method = string.ascii_letters
                    length = random.randint(rang[0], rang[1]+1)
                    return ''.join(random.choice(method) for i in range(length))
                else:
                    if (len(key) < rang[0] or len(key) > rang[1]):
                        key = None
                        print(
                            f'\n{what} length should be {rang[0]}-{rang[1]}')
                    else:
                        return key

        def inputnumber(what, ran):
            key = None
            while key == None:
                if self.ranValue == False:
                    print(f'Enter {what}:')
                    key = input()
                if key == 'r' or self.ranValue == True:
                    self.ranValue = True
                    if isinstance(ran, int):
                        stop = 1
                        for i in range(ran):
                            stop *= 10
                        temp = random.randint(0, stop)
                        while len(str(temp)) < 13:
                            temp = '0'+str(temp)
                        return temp
                    else:
                        return random.randint(ran[0], ran[1]+1)
                else:
                    try:
                        int(key)
                    except:
                        key = None
                        print(f'\n{what} should be an integer number')
                        continue
                    if isinstance(ran, int):
                        if not len(str(key)) == ran:
                            key = None
                            print(f'\n{what} length should be {ran}')
                            continue
                    else:
                        if int(key) < ran[0] or int(key) > ran[1]:
                            key = None
                            print(
                                f'\n{what} should be {ran[0]}-{range[1]}')
                            continue
                    return int(key)

        print('Enter "r" to add a random book')

        # input ISBN
        ISBN = inputnumber('ISBN', 13)
        doesExist = self.back.search('ISBN', ISBN)
        if (doesExist):
            print(f'{ISBN} is already in the database: {doesExist}')
            return

        # input title
        title = inputString('Title', [5, 30])

        # input author
        firstName = inputString('Author First Name', [5, 15])
        lastName = inputString('Author Last Name', [5, 25])
        author = firstName+' '+lastName

        # input publisher
        publisher = inputString('Publisher', [5, 30])

        # input publishDate
        pubYear = inputnumber('Publish year', 4)
        pubMonth = inputnumber('Publish month', [1, 12])
        pubDay = inputnumber('Publish day', [1, 31])
        pubDate = int(str(pubYear)+str(pubMonth)+str(pubDay))

        # input category
        if not self.ranValue:
            print('How many category do you want to add')
        howMany = inputnumber('Category Number', [0, 11])
        category = []
        for i in range(howMany):
            category.append(inputString('Category', [4, 10]))

        # input supply
        supply = inputnumber('Supply', [0, 100])

        # input people
        if not self.ranValue:
            print('How many people do you want to add')
        howMany = inputnumber('People Number', [0, supply+1])
        people = []
        for i in range(howMany):
            people.append(inputnumber('People ID', 10))

        self.back.add(ISBN, title, author, publisher,
                      pubDate, category, supply, people)
        print(f'Your record added to row:\t{self.back.last}')
        self.ranValue = False

    def removeBook(self):
        pass

    def searchBook(self):
        pass

    def displayBooks(self):
        pass


# tests
'''
b = LibraryBackEnd('database.csv', True)
b.add(5, '', '', '', 0, [
      'ali', 'hasan', 'qolam'], 0,  [1, 2, 3, 4])
b.add(2, '', '', '', 0, ['ali', 'hasan'], 0,  [1, 2, 3])
b.add(4, '', '', '', 0, ['ali', ''], 0,  [1, 2])
# b.remove(2915972317011)
b.add(3, '', '', '', 0, [
      'ali', 'hasan', 'qolam'], 0,  [1, 2, 3, 4])
b.add(1, '', '', '', 0, ['ali', ''], 0,  [1, 2])
print(b.search('category', 'hasan'))
print(b.search('category', 'qolam'))
print(b.search('category', 'ali'))
b.sort('ISBN')
'''
LibraryFrontEnd()
