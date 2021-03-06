from random import choice, randint
from string import printable
import re

class RegexStr(object):
    def __init__(self, value):
        self.value = value

    def invalid_data(self):
        data = filter(lambda ind: \
        not ind in self.value, printable)

        return ''.join(choice(data) 
        for ind in xrange(len(self.value)))

    def valid_data(self):
        return self.value

    def __str__(self):
        return re.escape(self.value)

class RegexOperator(object):
    # It may be interesting to have a base class Pattern
    # that implements common methods with Group and Include, Exclude.
    # Because these accept multiple arguments.

    def __init__(self):
        pass

    def invalid_data(self):
        pass

    def valid_data(self):
        pass

    def encargs(self, args):
        return [RegexStr(ind) if isinstance(ind, str) else ind
        for ind in args]

    def encstr(self, regex):
        regex = RegexStr(regex) if isinstance(
        regex, str) else regex
        return regex

    def test(self):
        regex = str(self)
        data  = self.valid_data()

        # It has to be search in order to work with ConsumeNext.
        strc  = re.search(regex, data)
        print 'Regex;', regex
        print 'Input:', data
        print 'Group dict:', strc.groupdict()
        print 'Group 0:', strc.group(0)
        print 'Groups:', strc.groups()

    def join(self):
        return ''.join(map(lambda ind: str(ind), self.args))

    def __str__(self):
        pass

class NamedGroup(RegexOperator):
    """
    Named groups.

    (?P<name>...)
    """

    def __init__(self, name, *args):
        self.args = self.encargs(args)
        self.name  = name

    def invalid_data(self):
        return ''.join(map(lambda ind: \
        ind.invalid_data(), self.args))

    def valid_data(self):
        return ''.join(map(lambda ind: \
        ind.valid_data(), self.args))

    def __str__(self):
        return '(?P<%s>%s)' % (self.name, self.join())

class Group(RegexOperator):
    """
    A normal group.

    (abc).
    """

    def __init__(self, *args):
        self.args = self.encargs(args)

    def invalid_data(self):
        return ''.join(map(lambda ind: \
        ind.invalid_data(), self.args))

    def valid_data(self):
        return ''.join(map(lambda ind: \
        ind.valid_data(), self.args))

    def __str__(self):
        return '(%s)' % self.join()

class Times(RegexOperator):
    """
    Match n, m times.

    a{1, 3}

    Note: The * and + are emulated by
    Times(regex, 0) or Times(regex, 1)

    """

    TEST_MAX = 10

    def __init__(self, regex, min=0, max=''):
        self.regex = self.encstr(regex)

        self.min   = min
        self.max   = max

    def invalid_data(self):
        pass

    def valid_data(self):
        count = randint(self.min, self.max 
        if self.max else self.TEST_MAX)

        data = ''.join((self.regex.valid_data() 
        for ind in xrange(count)))

        return data 

    def __str__(self):
        return '%s{%s,%s}' % (self.regex, 
        self.min, self.max)

class ConsumeNext(RegexOperator):
    """
    Lookbehind assertion.
    
    (?<=...) or (?<...) based on neg argument.
    """

    def __init__(self, regex0, regex1, neg=False):
        self.regex0 = self.encstr(regex0)
        self.regex1 = self.encstr(regex1)
        self.neg    = neg

    def invalid_data(self):
        pass

    def valid_data(self):
        return '%s%s' % ((self.regex0.valid_data(), 
        self.regex1.valid_data()) if not self.neg else (self.regex0.invalid_data(), 
        self.regex1.valid_data()))

    def __str__(self):
        return ('(?<=%s)%s' if not self.neg else \
        '(?<!%s)%s') % (self.regex0, self.regex1)

class ConsumeBack(RegexOperator):
    """
    Lookahead assertion.

    (?=...)
    """

    def __init__(self, regex0, regex1, neg=False):
        self.regex0 = self.encstr(regex0)
        self.regex1 = self.encstr(regex1)
        self.neg    = neg

    def invalid_data(self):
        pass

    def valid_data(self):
        return '%s%s' % ((self.regex0.valid_data(), 
        self.regex1.valid_data()) if not self.neg else (self.regex0.valid_data(), 
        self.regex1.invalid_data()))

    def __str__(self):
        return ('%s(?=%s)' if not self.neg else\
        '%s(?!%s)') % (self.regex0, self.regex1)

class Seq(RegexOperator):
    def __init__(self, start, end):
        self.start = start
        self.end   = end
        self.seq   = [chr(ind) for ind in xrange(
        ord(self.start), ord(self.end))]

    def invalid_data(self):
        return ''.join(filter(lambda ind: \
        not ind in self.seq, printable))

    def valid_data(self):
        return ''.join(self.seq)

    def __str__(self):
        return '%s-%s' % (self.start, self.end)

class Include(RegexOperator):
    """
    Sets.

    [abc]
    """

    def __init__(self, *args):
        self.args = self.encargs(args)

    def invalid_data(self):
        chars = ''.join(map(lambda ind: \
        ind.valid_data(), self.args))

        data = filter(lambda ind: \
        not ind in chars, printable)

        return choice(data)

    def valid_data(self):
        chars = ''.join(map(lambda ind: \
        ind.valid_data(), self.args))

        char = choice(chars)
        return char

    def __str__(self):
        return '[%s]' % self.join()

class Exclude(RegexOperator):
    """
    Excluding.

    [^abc]
    """

    def __init__(self, *args):
        self.args = self.encargs(args)

    def invalid_data(self):
        chars = ''.join(map(lambda ind: \
        ind.valid_data(), self.args))

        char = choice(chars)
        return char

    def valid_data(self):
        chars = ''.join(map(lambda ind: \
        ind.valid_data(), self.args))

        data = filter(lambda ind: \
        not ind in chars, printable)

        return choice(data)

    def __str__(self):
        return '[^%s]' % self.join()

class X(RegexOperator):
    """
    The dot.

    .
    """

    TOKEN = '.'

    def __init__(self):
        pass

    def invalid_data(self):
        return ''

    def valid_data(self):
        char = choice(printable)
        return char

    def __str__(self):
        return self.TOKEN

class Pattern(RegexOperator):
    """
    Setup a pattern.
    """

    def __init__(self, *args):
        self.args = self.encargs(args)

    def invalid_data(self):
        return ''.join(map(lambda ind: \
        ind.invalid_data(), self.args))

    def valid_data(self):
        return ''.join(map(lambda ind: \
        ind.valid_data(), self.args))

    def __str__(self):
        return self.join()
    


