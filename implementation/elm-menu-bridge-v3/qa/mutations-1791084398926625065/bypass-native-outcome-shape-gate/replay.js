(function(scope){
'use strict';

function F(arity, fun, wrapper) {
  wrapper.a = arity;
  wrapper.f = fun;
  return wrapper;
}

function F2(fun) {
  return F(2, fun, function(a) { return function(b) { return fun(a,b); }; })
}
function F3(fun) {
  return F(3, fun, function(a) {
    return function(b) { return function(c) { return fun(a, b, c); }; };
  });
}
function F4(fun) {
  return F(4, fun, function(a) { return function(b) { return function(c) {
    return function(d) { return fun(a, b, c, d); }; }; };
  });
}
function F5(fun) {
  return F(5, fun, function(a) { return function(b) { return function(c) {
    return function(d) { return function(e) { return fun(a, b, c, d, e); }; }; }; };
  });
}
function F6(fun) {
  return F(6, fun, function(a) { return function(b) { return function(c) {
    return function(d) { return function(e) { return function(f) {
    return fun(a, b, c, d, e, f); }; }; }; }; };
  });
}
function F7(fun) {
  return F(7, fun, function(a) { return function(b) { return function(c) {
    return function(d) { return function(e) { return function(f) {
    return function(g) { return fun(a, b, c, d, e, f, g); }; }; }; }; }; };
  });
}
function F8(fun) {
  return F(8, fun, function(a) { return function(b) { return function(c) {
    return function(d) { return function(e) { return function(f) {
    return function(g) { return function(h) {
    return fun(a, b, c, d, e, f, g, h); }; }; }; }; }; }; };
  });
}
function F9(fun) {
  return F(9, fun, function(a) { return function(b) { return function(c) {
    return function(d) { return function(e) { return function(f) {
    return function(g) { return function(h) { return function(i) {
    return fun(a, b, c, d, e, f, g, h, i); }; }; }; }; }; }; }; };
  });
}

function A2(fun, a, b) {
  return fun.a === 2 ? fun.f(a, b) : fun(a)(b);
}
function A3(fun, a, b, c) {
  return fun.a === 3 ? fun.f(a, b, c) : fun(a)(b)(c);
}
function A4(fun, a, b, c, d) {
  return fun.a === 4 ? fun.f(a, b, c, d) : fun(a)(b)(c)(d);
}
function A5(fun, a, b, c, d, e) {
  return fun.a === 5 ? fun.f(a, b, c, d, e) : fun(a)(b)(c)(d)(e);
}
function A6(fun, a, b, c, d, e, f) {
  return fun.a === 6 ? fun.f(a, b, c, d, e, f) : fun(a)(b)(c)(d)(e)(f);
}
function A7(fun, a, b, c, d, e, f, g) {
  return fun.a === 7 ? fun.f(a, b, c, d, e, f, g) : fun(a)(b)(c)(d)(e)(f)(g);
}
function A8(fun, a, b, c, d, e, f, g, h) {
  return fun.a === 8 ? fun.f(a, b, c, d, e, f, g, h) : fun(a)(b)(c)(d)(e)(f)(g)(h);
}
function A9(fun, a, b, c, d, e, f, g, h, i) {
  return fun.a === 9 ? fun.f(a, b, c, d, e, f, g, h, i) : fun(a)(b)(c)(d)(e)(f)(g)(h)(i);
}

console.warn('Compiled in DEV mode. Follow the advice at https://elm-lang.org/0.19.2/optimize for better performance and smaller assets.');


var _List_Nil_UNUSED = { $: 0 };
var _List_Nil = { $: '[]' };

function _List_Cons_UNUSED(hd, tl) { return { $: 1, a: hd, b: tl }; }
function _List_Cons(hd, tl) { return { $: '::', a: hd, b: tl }; }


var _List_cons = F2(_List_Cons);

function _List_fromArray(arr)
{
	var out = _List_Nil;
	for (var i = arr.length; i--; )
	{
		out = _List_Cons(arr[i], out);
	}
	return out;
}

function _List_toArray(xs)
{
	for (var out = []; xs.b; xs = xs.b) // WHILE_CONS
	{
		out.push(xs.a);
	}
	return out;
}

var _List_map2 = F3(function(f, xs, ys)
{
	for (var arr = []; xs.b && ys.b; xs = xs.b, ys = ys.b) // WHILE_CONSES
	{
		arr.push(A2(f, xs.a, ys.a));
	}
	return _List_fromArray(arr);
});

var _List_map3 = F4(function(f, xs, ys, zs)
{
	for (var arr = []; xs.b && ys.b && zs.b; xs = xs.b, ys = ys.b, zs = zs.b) // WHILE_CONSES
	{
		arr.push(A3(f, xs.a, ys.a, zs.a));
	}
	return _List_fromArray(arr);
});

var _List_map4 = F5(function(f, ws, xs, ys, zs)
{
	for (var arr = []; ws.b && xs.b && ys.b && zs.b; ws = ws.b, xs = xs.b, ys = ys.b, zs = zs.b) // WHILE_CONSES
	{
		arr.push(A4(f, ws.a, xs.a, ys.a, zs.a));
	}
	return _List_fromArray(arr);
});

var _List_map5 = F6(function(f, vs, ws, xs, ys, zs)
{
	for (var arr = []; vs.b && ws.b && xs.b && ys.b && zs.b; vs = vs.b, ws = ws.b, xs = xs.b, ys = ys.b, zs = zs.b) // WHILE_CONSES
	{
		arr.push(A5(f, vs.a, ws.a, xs.a, ys.a, zs.a));
	}
	return _List_fromArray(arr);
});

var _List_sortBy = F2(function(f, xs)
{
	return _List_fromArray(_List_toArray(xs).sort(function(a, b) {
		return _Utils_cmp(f(a), f(b));
	}));
});

var _List_sortWith = F2(function(f, xs)
{
	return _List_fromArray(_List_toArray(xs).sort(function(a, b) {
		var ord = A2(f, a, b);
		return ord === $elm$core$Basics$EQ ? 0 : ord === $elm$core$Basics$LT ? -1 : 1;
	}));
});



var _JsArray_empty = [];

function _JsArray_singleton(value)
{
    return [value];
}

function _JsArray_length(array)
{
    return array.length;
}

var _JsArray_initialize = F3(function(size, offset, func)
{
    var result = new Array(size);

    for (var i = 0; i < size; i++)
    {
        result[i] = func(offset + i);
    }

    return result;
});

var _JsArray_initializeFromList = F2(function (max, ls)
{
    var result = new Array(max);

    for (var i = 0; i < max && ls.b; i++)
    {
        result[i] = ls.a;
        ls = ls.b;
    }

    result.length = i;
    return _Utils_Tuple2(result, ls);
});

var _JsArray_unsafeGet = F2(function(index, array)
{
    return array[index];
});

var _JsArray_unsafeSet = F3(function(index, value, array)
{
    var length = array.length;
    var result = new Array(length);

    for (var i = 0; i < length; i++)
    {
        result[i] = array[i];
    }

    result[index] = value;
    return result;
});

var _JsArray_push = F2(function(value, array)
{
    var length = array.length;
    var result = new Array(length + 1);

    for (var i = 0; i < length; i++)
    {
        result[i] = array[i];
    }

    result[length] = value;
    return result;
});

var _JsArray_foldl = F3(function(func, acc, array)
{
    var length = array.length;

    for (var i = 0; i < length; i++)
    {
        acc = A2(func, array[i], acc);
    }

    return acc;
});

var _JsArray_foldr = F3(function(func, acc, array)
{
    for (var i = array.length - 1; i >= 0; i--)
    {
        acc = A2(func, array[i], acc);
    }

    return acc;
});

var _JsArray_map = F2(function(func, array)
{
    var length = array.length;
    var result = new Array(length);

    for (var i = 0; i < length; i++)
    {
        result[i] = func(array[i]);
    }

    return result;
});

var _JsArray_indexedMap = F3(function(func, offset, array)
{
    var length = array.length;
    var result = new Array(length);

    for (var i = 0; i < length; i++)
    {
        result[i] = A2(func, offset + i, array[i]);
    }

    return result;
});

var _JsArray_slice = F3(function(from, to, array)
{
    return array.slice(from, to);
});

var _JsArray_appendN = F3(function(n, dest, source)
{
    var destLen = dest.length;
    var itemsToCopy = n - destLen;

    if (itemsToCopy > source.length)
    {
        itemsToCopy = source.length;
    }

    var size = destLen + itemsToCopy;
    var result = new Array(size);

    for (var i = 0; i < destLen; i++)
    {
        result[i] = dest[i];
    }

    for (var i = 0; i < itemsToCopy; i++)
    {
        result[i + destLen] = source[i];
    }

    return result;
});



// LOG

var _Debug_log_UNUSED = F2(function(tag, value)
{
	return value;
});

var _Debug_log = F2(function(tag, value)
{
	console.log(tag + ': ' + _Debug_toString(value));
	return value;
});


// TODOS

function _Debug_todo(moduleName, region)
{
	return function(message) {
		_Debug_crash(8, moduleName, region, message);
	};
}

function _Debug_todoCase(moduleName, region, value)
{
	return function(message) {
		_Debug_crash(9, moduleName, region, value, message);
	};
}


// TO STRING

function _Debug_toString_UNUSED(value)
{
	return '<internals>';
}

function _Debug_toString(value)
{
	return _Debug_toAnsiString(false, value);
}

function _Debug_toAnsiString(ansi, value)
{
	if (typeof value === 'function')
	{
		return _Debug_internalColor(ansi, '<function>');
	}

	if (typeof value === 'boolean')
	{
		return _Debug_ctorColor(ansi, value ? 'True' : 'False');
	}

	if (typeof value === 'number')
	{
		return _Debug_numberColor(ansi, value + '');
	}

	if (value instanceof String)
	{
		return _Debug_charColor(ansi, "'" + _Debug_addSlashes(value, true) + "'");
	}

	if (typeof value === 'string')
	{
		return _Debug_stringColor(ansi, '"' + _Debug_addSlashes(value, false) + '"');
	}

	if (typeof value === 'object' && '$' in value)
	{
		var tag = value.$;

		if (typeof tag === 'number')
		{
			return _Debug_internalColor(ansi, '<internals>');
		}

		if (tag[0] === '#')
		{
			var output = [];
			for (var k in value)
			{
				if (k === '$') continue;
				output.push(_Debug_toAnsiString(ansi, value[k]));
			}
			return '(' + output.join(',') + ')';
		}

		if (tag === 'Set_elm_builtin')
		{
			return _Debug_ctorColor(ansi, 'Set')
				+ _Debug_fadeColor(ansi, '.fromList') + ' '
				+ _Debug_toAnsiString(ansi, $elm$core$Set$toList(value));
		}

		if (tag === 'RBNode_elm_builtin' || tag === 'RBEmpty_elm_builtin')
		{
			return _Debug_ctorColor(ansi, 'Dict')
				+ _Debug_fadeColor(ansi, '.fromList') + ' '
				+ _Debug_toAnsiString(ansi, $elm$core$Dict$toList(value));
		}

		if (tag === 'Array_elm_builtin')
		{
			return _Debug_ctorColor(ansi, 'Array')
				+ _Debug_fadeColor(ansi, '.fromList') + ' '
				+ _Debug_toAnsiString(ansi, $elm$core$Array$toList(value));
		}

		if (tag === '::' || tag === '[]')
		{
			var output = '[';

			value.b && (output += _Debug_toAnsiString(ansi, value.a), value = value.b)

			for (; value.b; value = value.b) // WHILE_CONS
			{
				output += ',' + _Debug_toAnsiString(ansi, value.a);
			}
			return output + ']';
		}

		var output = '';
		for (var i in value)
		{
			if (i === '$') continue;
			var str = _Debug_toAnsiString(ansi, value[i]);
			var c0 = str[0];
			var parenless = c0 === '{' || c0 === '(' || c0 === '[' || c0 === '<' || c0 === '"' || str.indexOf(' ') < 0;
			output += ' ' + (parenless ? str : '(' + str + ')');
		}
		return _Debug_ctorColor(ansi, tag) + output;
	}

	if (typeof DataView === 'function' && value instanceof DataView)
	{
		return _Debug_stringColor(ansi, '<' + value.byteLength + ' bytes>');
	}

	if (typeof File !== 'undefined' && value instanceof File)
	{
		return _Debug_internalColor(ansi, '<' + value.name + '>');
	}

	if (typeof value === 'object')
	{
		var output = [];
		for (var key in value)
		{
			var field = key[0] === '_' ? key.slice(1) : key;
			output.push(_Debug_fadeColor(ansi, field) + ' = ' + _Debug_toAnsiString(ansi, value[key]));
		}
		if (output.length === 0)
		{
			return '{}';
		}
		return '{ ' + output.join(', ') + ' }';
	}

	return _Debug_internalColor(ansi, '<internals>');
}

function _Debug_addSlashes(str, isChar)
{
	var s = str
		.replace(/\\/g, '\\\\')
		.replace(/\n/g, '\\n')
		.replace(/\t/g, '\\t')
		.replace(/\r/g, '\\r')
		.replace(/\v/g, '\\v')
		.replace(/\0/g, '\\0');

	if (isChar)
	{
		return s.replace(/\'/g, '\\\'');
	}
	else
	{
		return s.replace(/\"/g, '\\"');
	}
}

function _Debug_ctorColor(ansi, string)
{
	return ansi ? '\x1b[96m' + string + '\x1b[0m' : string;
}

function _Debug_numberColor(ansi, string)
{
	return ansi ? '\x1b[95m' + string + '\x1b[0m' : string;
}

function _Debug_stringColor(ansi, string)
{
	return ansi ? '\x1b[93m' + string + '\x1b[0m' : string;
}

function _Debug_charColor(ansi, string)
{
	return ansi ? '\x1b[92m' + string + '\x1b[0m' : string;
}

function _Debug_fadeColor(ansi, string)
{
	return ansi ? '\x1b[37m' + string + '\x1b[0m' : string;
}

function _Debug_internalColor(ansi, string)
{
	return ansi ? '\x1b[36m' + string + '\x1b[0m' : string;
}

function _Debug_toHexDigit(n)
{
	return String.fromCharCode(n < 10 ? 48 + n : 55 + n);
}


// CRASH


function _Debug_crash_UNUSED(identifier)
{
	throw new Error('https://github.com/elm/core/blob/1.0.0/hints/' + identifier + '.md');
}


function _Debug_crash(identifier, fact1, fact2, fact3, fact4)
{
	switch(identifier)
	{
		case 0:
			throw new Error('What node should I take over? In JavaScript I need something like:\n\n    Elm.Main.init({\n        node: document.getElementById("elm-node")\n    })\n\nYou need to do this with any Browser.sandbox or Browser.element program.');

		case 1:
			throw new Error('Browser.application programs cannot handle URLs like this:\n\n    ' + document.location.href + '\n\nWhat is the root? The root of your file system? Try looking at this program with `elm reactor` or some other server.');

		case 2:
			var jsonErrorString = fact1;
			throw new Error('Problem with the flags given to your Elm program on initialization.\n\n' + jsonErrorString);

		case 3:
			var portName = fact1;
			throw new Error('There can only be one port named `' + portName + '`, but your program has multiple.');

		case 4:
			var portName = fact1;
			var problem = fact2;
			throw new Error('Trying to send an unexpected type of value through port `' + portName + '`:\n' + problem);

		case 5:
			throw new Error('Trying to use `(==)` on functions.\nThere is no way to know if functions are "the same" in the Elm sense.\nRead more about this at https://package.elm-lang.org/packages/elm/core/latest/Basics#== which describes why it is this way and what the better version will look like.');

		case 6:
			var moduleName = fact1;
			throw new Error('Your page is loading multiple Elm scripts with a module named ' + moduleName + '. Maybe a duplicate script is getting loaded accidentally? If not, rename one of them so I know which is which!');

		case 8:
			var moduleName = fact1;
			var region = fact2;
			var message = fact3;
			throw new Error('TODO in module `' + moduleName + '` ' + _Debug_regionToString(region) + '\n\n' + message);

		case 9:
			var moduleName = fact1;
			var region = fact2;
			var value = fact3;
			var message = fact4;
			throw new Error(
				'TODO in module `' + moduleName + '` from the `case` expression '
				+ _Debug_regionToString(region) + '\n\nIt received the following value:\n\n    '
				+ _Debug_toString(value).replace('\n', '\n    ')
				+ '\n\nBut the branch that handles it says:\n\n    ' + message.replace('\n', '\n    ')
			);

		case 10:
			throw new Error('Bug in https://github.com/elm/virtual-dom/issues');

		case 11:
			throw new Error('Cannot perform mod 0. Division by zero error.');
	}
}

function _Debug_regionToString(region)
{
	if (region.start.line === region.end.line)
	{
		return 'on line ' + region.start.line;
	}
	return 'on lines ' + region.start.line + ' through ' + region.end.line;
}



// EQUALITY

function _Utils_eq(x, y)
{
	for (
		var pair, stack = [], isEqual = _Utils_eqHelp(x, y, 0, stack);
		isEqual && (pair = stack.pop());
		isEqual = _Utils_eqHelp(pair.a, pair.b, 0, stack)
		)
	{}

	return isEqual;
}

function _Utils_eqHelp(x, y, depth, stack)
{
	if (x === y)
	{
		return true;
	}

	if (typeof x !== 'object' || x === null || y === null)
	{
		typeof x === 'function' && _Debug_crash(5);
		return false;
	}

	if (depth > 100)
	{
		stack.push(_Utils_Tuple2(x,y));
		return true;
	}

	/**/
	if (x.$ === 'Set_elm_builtin')
	{
		x = $elm$core$Set$toList(x);
		y = $elm$core$Set$toList(y);
	}
	if (x.$ === 'RBNode_elm_builtin' || x.$ === 'RBEmpty_elm_builtin')
	{
		x = $elm$core$Dict$toList(x);
		y = $elm$core$Dict$toList(y);
	}
	//*/

	/**_UNUSED/
	if (x.$ < 0)
	{
		x = $elm$core$Dict$toList(x);
		y = $elm$core$Dict$toList(y);
	}
	//*/

	for (var key in x)
	{
		if (!_Utils_eqHelp(x[key], y[key], depth + 1, stack))
		{
			return false;
		}
	}
	return true;
}

var _Utils_equal = F2(_Utils_eq);
var _Utils_notEqual = F2(function(a, b) { return !_Utils_eq(a,b); });



// COMPARISONS

// Code in Generate/JavaScript.hs, Basics.js, and List.js depends on
// the particular integer values assigned to LT, EQ, and GT.

function _Utils_cmp(x, y, ord)
{
	if (typeof x !== 'object')
	{
		return x === y ? /*EQ*/ 0 : x < y ? /*LT*/ -1 : /*GT*/ 1;
	}

	/**/
	if (x instanceof String)
	{
		var a = x.valueOf();
		var b = y.valueOf();
		return a === b ? 0 : a < b ? -1 : 1;
	}
	//*/

	/**_UNUSED/
	if (typeof x.$ === 'undefined')
	//*/
	/**/
	if (x.$[0] === '#')
	//*/
	{
		return (ord = _Utils_cmp(x.a, y.a))
			? ord
			: (ord = _Utils_cmp(x.b, y.b))
				? ord
				: _Utils_cmp(x.c, y.c);
	}

	// traverse conses until end of a list or a mismatch
	for (; x.b && y.b && !(ord = _Utils_cmp(x.a, y.a)); x = x.b, y = y.b) {} // WHILE_CONSES
	return ord || (x.b ? /*GT*/ 1 : y.b ? /*LT*/ -1 : /*EQ*/ 0);
}

var _Utils_lt = F2(function(a, b) { return _Utils_cmp(a, b) < 0; });
var _Utils_le = F2(function(a, b) { return _Utils_cmp(a, b) < 1; });
var _Utils_gt = F2(function(a, b) { return _Utils_cmp(a, b) > 0; });
var _Utils_ge = F2(function(a, b) { return _Utils_cmp(a, b) >= 0; });

var _Utils_compare = F2(function(x, y)
{
	var n = _Utils_cmp(x, y);
	return n < 0 ? $elm$core$Basics$LT : n ? $elm$core$Basics$GT : $elm$core$Basics$EQ;
});


// COMMON VALUES

var _Utils_Tuple0_UNUSED = 0;
var _Utils_Tuple0 = { $: '#0' };

function _Utils_Tuple2_UNUSED(a, b) { return { a: a, b: b }; }
function _Utils_Tuple2(a, b) { return { $: '#2', a: a, b: b }; }

function _Utils_Tuple3_UNUSED(a, b, c) { return { a: a, b: b, c: c }; }
function _Utils_Tuple3(a, b, c) { return { $: '#3', a: a, b: b, c: c }; }

function _Utils_chr_UNUSED(c) { return c; }
function _Utils_chr(c) { return new String(c); }


// RECORDS

function _Utils_update(oldRecord, updatedFields)
{
	var newRecord = {};

	for (var key in oldRecord)
	{
		newRecord[key] = oldRecord[key];
	}

	for (var key in updatedFields)
	{
		newRecord[key] = updatedFields[key];
	}

	return newRecord;
}


// APPEND

var _Utils_append = F2(_Utils_ap);

function _Utils_ap(xs, ys)
{
	// append Strings
	if (typeof xs === 'string')
	{
		return xs + ys;
	}

	// append Lists
	if (!xs.b)
	{
		return ys;
	}
	var root = _List_Cons(xs.a, ys);
	xs = xs.b
	for (var curr = root; xs.b; xs = xs.b) // WHILE_CONS
	{
		curr = curr.b = _List_Cons(xs.a, ys);
	}
	return root;
}



// MATH

var _Basics_add = F2(function(a, b) { return a + b; });
var _Basics_sub = F2(function(a, b) { return a - b; });
var _Basics_mul = F2(function(a, b) { return a * b; });
var _Basics_fdiv = F2(function(a, b) { return a / b; });
var _Basics_idiv = F2(function(a, b) { return (a / b) | 0; });
var _Basics_pow = F2(Math.pow);

var _Basics_remainderBy = F2(function(b, a) { return a % b; });

// https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/divmodnote-letter.pdf
var _Basics_modBy = F2(function(modulus, x)
{
	var answer = x % modulus;
	return modulus === 0
		? _Debug_crash(11)
		:
	((answer > 0 && modulus < 0) || (answer < 0 && modulus > 0))
		? answer + modulus
		: answer;
});


// TRIGONOMETRY

var _Basics_pi = Math.PI;
var _Basics_e = Math.E;
var _Basics_cos = Math.cos;
var _Basics_sin = Math.sin;
var _Basics_tan = Math.tan;
var _Basics_acos = Math.acos;
var _Basics_asin = Math.asin;
var _Basics_atan = Math.atan;
var _Basics_atan2 = F2(Math.atan2);


// MORE MATH

function _Basics_toFloat(x) { return x; }
function _Basics_truncate(n) { return n | 0; }
function _Basics_isInfinite(n) { return n === Infinity || n === -Infinity; }

var _Basics_ceiling = Math.ceil;
var _Basics_floor = Math.floor;
var _Basics_round = Math.round;
var _Basics_sqrt = Math.sqrt;
var _Basics_log = Math.log;
var _Basics_isNaN = isNaN;


// BOOLEANS

function _Basics_not(bool) { return !bool; }
var _Basics_and = F2(function(a, b) { return a && b; });
var _Basics_or  = F2(function(a, b) { return a || b; });
var _Basics_xor = F2(function(a, b) { return a !== b; });



var _String_cons = F2(function(chr, str)
{
	return chr + str;
});

function _String_uncons(string)
{
	var word = string.charCodeAt(0);
	return !isNaN(word)
		? $elm$core$Maybe$Just(
			0xD800 <= word && word <= 0xDBFF
				? _Utils_Tuple2(_Utils_chr(string[0] + string[1]), string.slice(2))
				: _Utils_Tuple2(_Utils_chr(string[0]), string.slice(1))
		)
		: $elm$core$Maybe$Nothing;
}

var _String_append = F2(function(a, b)
{
	return a + b;
});

function _String_length(str)
{
	return str.length;
}

var _String_map = F2(function(func, string)
{
	var len = string.length;
	var array = new Array(len);
	var i = 0;
	while (i < len)
	{
		var word = string.charCodeAt(i);
		if (0xD800 <= word && word <= 0xDBFF)
		{
			array[i] = func(_Utils_chr(string[i] + string[i+1]));
			i += 2;
			continue;
		}
		array[i] = func(_Utils_chr(string[i]));
		i++;
	}
	return array.join('');
});

var _String_filter = F2(function(isGood, str)
{
	var arr = [];
	var len = str.length;
	var i = 0;
	while (i < len)
	{
		var char = str[i];
		var word = str.charCodeAt(i);
		i++;
		if (0xD800 <= word && word <= 0xDBFF)
		{
			char += str[i];
			i++;
		}

		if (isGood(_Utils_chr(char)))
		{
			arr.push(char);
		}
	}
	return arr.join('');
});

function _String_reverse(str)
{
	var len = str.length;
	var arr = new Array(len);
	var i = 0;
	while (i < len)
	{
		var word = str.charCodeAt(i);
		if (0xD800 <= word && word <= 0xDBFF)
		{
			arr[len - i] = str[i + 1];
			i++;
			arr[len - i] = str[i - 1];
			i++;
		}
		else
		{
			arr[len - i] = str[i];
			i++;
		}
	}
	return arr.join('');
}

var _String_foldl = F3(function(func, state, string)
{
	var len = string.length;
	var i = 0;
	while (i < len)
	{
		var char = string[i];
		var word = string.charCodeAt(i);
		i++;
		if (0xD800 <= word && word <= 0xDBFF)
		{
			char += string[i];
			i++;
		}
		state = A2(func, _Utils_chr(char), state);
	}
	return state;
});

var _String_foldr = F3(function(func, state, string)
{
	var i = string.length;
	while (i--)
	{
		var char = string[i];
		var word = string.charCodeAt(i);
		if (0xDC00 <= word && word <= 0xDFFF)
		{
			i--;
			char = string[i] + char;
		}
		state = A2(func, _Utils_chr(char), state);
	}
	return state;
});

var _String_split = F2(function(sep, str)
{
	return str.split(sep);
});

var _String_join = F2(function(sep, strs)
{
	return strs.join(sep);
});

var _String_slice = F3(function(start, end, str) {
	return str.slice(start, end);
});

function _String_trim(str)
{
	return str.trim();
}

function _String_trimLeft(str)
{
	return str.replace(/^\s+/, '');
}

function _String_trimRight(str)
{
	return str.replace(/\s+$/, '');
}

function _String_words(str)
{
	return _List_fromArray(str.trim().split(/\s+/g));
}

function _String_lines(str)
{
	return _List_fromArray(str.split(/\r\n|\r|\n/g));
}

function _String_toUpper(str)
{
	return str.toUpperCase();
}

function _String_toLower(str)
{
	return str.toLowerCase();
}

var _String_any = F2(function(isGood, string)
{
	var i = string.length;
	while (i--)
	{
		var char = string[i];
		var word = string.charCodeAt(i);
		if (0xDC00 <= word && word <= 0xDFFF)
		{
			i--;
			char = string[i] + char;
		}
		if (isGood(_Utils_chr(char)))
		{
			return true;
		}
	}
	return false;
});

var _String_all = F2(function(isGood, string)
{
	var i = string.length;
	while (i--)
	{
		var char = string[i];
		var word = string.charCodeAt(i);
		if (0xDC00 <= word && word <= 0xDFFF)
		{
			i--;
			char = string[i] + char;
		}
		if (!isGood(_Utils_chr(char)))
		{
			return false;
		}
	}
	return true;
});

var _String_contains = F2(function(sub, str)
{
	return str.indexOf(sub) > -1;
});

var _String_startsWith = F2(function(sub, str)
{
	return str.indexOf(sub) === 0;
});

var _String_endsWith = F2(function(sub, str)
{
	return str.length >= sub.length &&
		str.lastIndexOf(sub) === str.length - sub.length;
});

var _String_indexes = F2(function(sub, str)
{
	var subLen = sub.length;

	if (subLen < 1)
	{
		return _List_Nil;
	}

	var i = 0;
	var is = [];

	while ((i = str.indexOf(sub, i)) > -1)
	{
		is.push(i);
		i = i + subLen;
	}

	return _List_fromArray(is);
});


// TO STRING

function _String_fromNumber(number)
{
	return number + '';
}


// INT CONVERSIONS

function _String_toInt(str)
{
	var total = 0;
	var code0 = str.charCodeAt(0);
	var start = code0 == 0x2B /* + */ || code0 == 0x2D /* - */ ? 1 : 0;

	for (var i = start; i < str.length; ++i)
	{
		var code = str.charCodeAt(i);
		if (code < 0x30 || 0x39 < code)
		{
			return $elm$core$Maybe$Nothing;
		}
		total = 10 * total + code - 0x30;
	}

	return i == start
		? $elm$core$Maybe$Nothing
		: $elm$core$Maybe$Just(code0 == 0x2D ? -total : total);
}


// FLOAT CONVERSIONS

function _String_toFloat(s)
{
	// check if it is a hex, octal, or binary number
	if (s.length === 0 || /[\sxbo]/.test(s))
	{
		return $elm$core$Maybe$Nothing;
	}
	var n = +s;
	// faster isNaN check
	return n === n ? $elm$core$Maybe$Just(n) : $elm$core$Maybe$Nothing;
}

function _String_fromList(chars)
{
	return _List_toArray(chars).join('');
}




function _Char_toCode(char)
{
	var code = char.charCodeAt(0);
	if (0xD800 <= code && code <= 0xDBFF)
	{
		return (code - 0xD800) * 0x400 + char.charCodeAt(1) - 0xDC00 + 0x10000
	}
	return code;
}

function _Char_fromCode(code)
{
	return _Utils_chr(
		(code < 0 || 0x10FFFF < code)
			? '\uFFFD'
			:
		(code <= 0xFFFF)
			? String.fromCharCode(code)
			:
		(code -= 0x10000,
			String.fromCharCode(Math.floor(code / 0x400) + 0xD800, code % 0x400 + 0xDC00)
		)
	);
}

function _Char_toUpper(char)
{
	return _Utils_chr(char.toUpperCase());
}

function _Char_toLower(char)
{
	return _Utils_chr(char.toLowerCase());
}

function _Char_toLocaleUpper(char)
{
	return _Utils_chr(char.toLocaleUpperCase());
}

function _Char_toLocaleLower(char)
{
	return _Utils_chr(char.toLocaleLowerCase());
}



/**/
function _Json_errorToString(error)
{
	return $elm$json$Json$Decode$errorToString(error);
}
//*/


// CORE DECODERS

function _Json_succeed(msg)
{
	return {
		$: 0,
		a: msg
	};
}

function _Json_fail(msg)
{
	return {
		$: 1,
		a: msg
	};
}

function _Json_decodePrim(decoder)
{
	return { $: 2, b: decoder };
}

var _Json_decodeInt = _Json_decodePrim(function(value) {
	return (typeof value !== 'number')
		? _Json_expecting('an INT', value)
		:
	(-2147483647 < value && value < 2147483647 && (value | 0) === value)
		? $elm$core$Result$Ok(value)
		:
	(isFinite(value) && !(value % 1))
		? $elm$core$Result$Ok(value)
		: _Json_expecting('an INT', value);
});

var _Json_decodeBool = _Json_decodePrim(function(value) {
	return (typeof value === 'boolean')
		? $elm$core$Result$Ok(value)
		: _Json_expecting('a BOOL', value);
});

var _Json_decodeFloat = _Json_decodePrim(function(value) {
	return (typeof value === 'number')
		? $elm$core$Result$Ok(value)
		: _Json_expecting('a FLOAT', value);
});

var _Json_decodeValue = _Json_decodePrim(function(value) {
	return $elm$core$Result$Ok(_Json_wrap(value));
});

var _Json_decodeString = _Json_decodePrim(function(value) {
	return (typeof value === 'string')
		? $elm$core$Result$Ok(value)
		: (value instanceof String)
			? $elm$core$Result$Ok(value + '')
			: _Json_expecting('a STRING', value);
});

function _Json_decodeList(decoder) { return { $: 3, b: decoder }; }
function _Json_decodeArray(decoder) { return { $: 4, b: decoder }; }

function _Json_decodeNull(value) { return { $: 5, c: value }; }

var _Json_decodeField = F2(function(field, decoder)
{
	return {
		$: 6,
		d: field,
		b: decoder
	};
});

var _Json_decodeIndex = F2(function(index, decoder)
{
	return {
		$: 7,
		e: index,
		b: decoder
	};
});

function _Json_decodeKeyValuePairs(decoder)
{
	return {
		$: 8,
		b: decoder
	};
}

function _Json_mapMany(f, decoders)
{
	return {
		$: 9,
		f: f,
		g: decoders
	};
}

var _Json_andThen = F2(function(callback, decoder)
{
	return {
		$: 10,
		b: decoder,
		h: callback
	};
});

function _Json_oneOf(decoders)
{
	return {
		$: 11,
		g: decoders
	};
}


// DECODING OBJECTS

var _Json_map1 = F2(function(f, d1)
{
	return _Json_mapMany(f, [d1]);
});

var _Json_map2 = F3(function(f, d1, d2)
{
	return _Json_mapMany(f, [d1, d2]);
});

var _Json_map3 = F4(function(f, d1, d2, d3)
{
	return _Json_mapMany(f, [d1, d2, d3]);
});

var _Json_map4 = F5(function(f, d1, d2, d3, d4)
{
	return _Json_mapMany(f, [d1, d2, d3, d4]);
});

var _Json_map5 = F6(function(f, d1, d2, d3, d4, d5)
{
	return _Json_mapMany(f, [d1, d2, d3, d4, d5]);
});

var _Json_map6 = F7(function(f, d1, d2, d3, d4, d5, d6)
{
	return _Json_mapMany(f, [d1, d2, d3, d4, d5, d6]);
});

var _Json_map7 = F8(function(f, d1, d2, d3, d4, d5, d6, d7)
{
	return _Json_mapMany(f, [d1, d2, d3, d4, d5, d6, d7]);
});

var _Json_map8 = F9(function(f, d1, d2, d3, d4, d5, d6, d7, d8)
{
	return _Json_mapMany(f, [d1, d2, d3, d4, d5, d6, d7, d8]);
});


// DECODE

var _Json_runOnString = F2(function(decoder, string)
{
	try
	{
		var value = JSON.parse(string);
		return _Json_runHelp(decoder, value);
	}
	catch (e)
	{
		return $elm$core$Result$Err(A2($elm$json$Json$Decode$Failure, 'This is not valid JSON! ' + e.message, _Json_wrap(string)));
	}
});

var _Json_run = F2(function(decoder, value)
{
	return _Json_runHelp(decoder, _Json_unwrap(value));
});

function _Json_runHelp(decoder, value)
{
	switch (decoder.$)
	{
		case 2:
			return decoder.b(value);

		case 5:
			return (value === null)
				? $elm$core$Result$Ok(decoder.c)
				: _Json_expecting('null', value);

		case 3:
			if (!_Json_isArray(value))
			{
				return _Json_expecting('a LIST', value);
			}
			return _Json_runArrayDecoder(decoder.b, value, _List_fromArray);

		case 4:
			if (!_Json_isArray(value))
			{
				return _Json_expecting('an ARRAY', value);
			}
			return _Json_runArrayDecoder(decoder.b, value, _Json_toElmArray);

		case 6:
			var field = decoder.d;
			if (typeof value !== 'object' || value === null || !(field in value))
			{
				return _Json_expecting('an OBJECT with a field named `' + field + '`', value);
			}
			var result = _Json_runHelp(decoder.b, value[field]);
			return ($elm$core$Result$isOk(result)) ? result : $elm$core$Result$Err(A2($elm$json$Json$Decode$Field, field, result.a));

		case 7:
			var index = decoder.e;
			if (!_Json_isArray(value))
			{
				return _Json_expecting('an ARRAY', value);
			}
			if (index >= value.length)
			{
				return _Json_expecting('a LONGER array. Need index ' + index + ' but only see ' + value.length + ' entries', value);
			}
			var result = _Json_runHelp(decoder.b, value[index]);
			return ($elm$core$Result$isOk(result)) ? result : $elm$core$Result$Err(A2($elm$json$Json$Decode$Index, index, result.a));

		case 8:
			if (typeof value !== 'object' || value === null || _Json_isArray(value))
			{
				return _Json_expecting('an OBJECT', value);
			}

			var keyValuePairs = _List_Nil;
			// TODO test perf of Object.keys and switch when support is good enough
			for (var key in value)
			{
				if (value.hasOwnProperty(key))
				{
					var result = _Json_runHelp(decoder.b, value[key]);
					if (!$elm$core$Result$isOk(result))
					{
						return $elm$core$Result$Err(A2($elm$json$Json$Decode$Field, key, result.a));
					}
					keyValuePairs = _List_Cons(_Utils_Tuple2(key, result.a), keyValuePairs);
				}
			}
			return $elm$core$Result$Ok($elm$core$List$reverse(keyValuePairs));

		case 9:
			var answer = decoder.f;
			var decoders = decoder.g;
			for (var i = 0; i < decoders.length; i++)
			{
				var result = _Json_runHelp(decoders[i], value);
				if (!$elm$core$Result$isOk(result))
				{
					return result;
				}
				answer = answer(result.a);
			}
			return $elm$core$Result$Ok(answer);

		case 10:
			var result = _Json_runHelp(decoder.b, value);
			return (!$elm$core$Result$isOk(result))
				? result
				: _Json_runHelp(decoder.h(result.a), value);

		case 11:
			var errors = _List_Nil;
			for (var temp = decoder.g; temp.b; temp = temp.b) // WHILE_CONS
			{
				var result = _Json_runHelp(temp.a, value);
				if ($elm$core$Result$isOk(result))
				{
					return result;
				}
				errors = _List_Cons(result.a, errors);
			}
			return $elm$core$Result$Err($elm$json$Json$Decode$OneOf($elm$core$List$reverse(errors)));

		case 1:
			return $elm$core$Result$Err(A2($elm$json$Json$Decode$Failure, decoder.a, _Json_wrap(value)));

		case 0:
			return $elm$core$Result$Ok(decoder.a);
	}
}

function _Json_runArrayDecoder(decoder, value, toElmValue)
{
	var len = value.length;
	var array = new Array(len);
	for (var i = 0; i < len; i++)
	{
		var result = _Json_runHelp(decoder, value[i]);
		if (!$elm$core$Result$isOk(result))
		{
			return $elm$core$Result$Err(A2($elm$json$Json$Decode$Index, i, result.a));
		}
		array[i] = result.a;
	}
	return $elm$core$Result$Ok(toElmValue(array));
}

function _Json_isArray(value)
{
	return Array.isArray(value) || (typeof FileList !== 'undefined' && value instanceof FileList);
}

function _Json_toElmArray(array)
{
	return A2($elm$core$Array$initialize, array.length, function(i) { return array[i]; });
}

function _Json_expecting(type, value)
{
	return $elm$core$Result$Err(A2($elm$json$Json$Decode$Failure, 'Expecting ' + type, _Json_wrap(value)));
}


// EQUALITY

function _Json_equality(x, y)
{
	if (x === y)
	{
		return true;
	}

	if (x.$ !== y.$)
	{
		return false;
	}

	switch (x.$)
	{
		case 0:
		case 1:
			return x.a === y.a;

		case 2:
			return x.b === y.b;

		case 5:
			return x.c === y.c;

		case 3:
		case 4:
		case 8:
			return _Json_equality(x.b, y.b);

		case 6:
			return x.d === y.d && _Json_equality(x.b, y.b);

		case 7:
			return x.e === y.e && _Json_equality(x.b, y.b);

		case 9:
			return x.f === y.f && _Json_listEquality(x.g, y.g);

		case 10:
			return x.h === y.h && _Json_equality(x.b, y.b);

		case 11:
			return _Json_listEquality(x.g, y.g);
	}
}

function _Json_listEquality(aDecoders, bDecoders)
{
	var len = aDecoders.length;
	if (len !== bDecoders.length)
	{
		return false;
	}
	for (var i = 0; i < len; i++)
	{
		if (!_Json_equality(aDecoders[i], bDecoders[i]))
		{
			return false;
		}
	}
	return true;
}


// ENCODE

var _Json_encode = F2(function(indentLevel, value)
{
	return JSON.stringify(_Json_unwrap(value), null, indentLevel) + '';
});

function _Json_wrap(value) { return { $: 0, a: value }; }
function _Json_unwrap(value) { return value.a; }

function _Json_wrap_UNUSED(value) { return value; }
function _Json_unwrap_UNUSED(value) { return value; }

function _Json_emptyArray() { return []; }
function _Json_emptyObject() { return {}; }

var _Json_addField = F3(function(key, value, object)
{
	object[key] = _Json_unwrap(value);
	return object;
});

function _Json_addEntry(func)
{
	return F2(function(entry, array)
	{
		array.push(_Json_unwrap(func(entry)));
		return array;
	});
}

var _Json_encodeNull = _Json_wrap(null);



// TASKS

function _Scheduler_succeed(value)
{
	return {
		$: 0,
		a: value
	};
}

function _Scheduler_fail(error)
{
	return {
		$: 1,
		a: error
	};
}

function _Scheduler_binding(callback)
{
	return {
		$: 2,
		b: callback,
		c: null
	};
}

var _Scheduler_andThen = F2(function(callback, task)
{
	return {
		$: 3,
		b: callback,
		d: task
	};
});

var _Scheduler_onError = F2(function(callback, task)
{
	return {
		$: 4,
		b: callback,
		d: task
	};
});

function _Scheduler_receive(callback)
{
	return {
		$: 5,
		b: callback
	};
}


// PROCESSES

var _Scheduler_guid = 0;

function _Scheduler_rawSpawn(task)
{
	var proc = {
		$: 0,
		e: _Scheduler_guid++,
		f: task,
		g: null,
		h: []
	};

	_Scheduler_enqueue(proc);

	return proc;
}

function _Scheduler_spawn(task)
{
	return _Scheduler_binding(function(callback) {
		callback(_Scheduler_succeed(_Scheduler_rawSpawn(task)));
	});
}

function _Scheduler_rawSend(proc, msg)
{
	proc.h.push(msg);
	_Scheduler_enqueue(proc);
}

var _Scheduler_send = F2(function(proc, msg)
{
	return _Scheduler_binding(function(callback) {
		_Scheduler_rawSend(proc, msg);
		callback(_Scheduler_succeed(_Utils_Tuple0));
	});
});

function _Scheduler_kill(proc)
{
	return _Scheduler_binding(function(callback) {
		var task = proc.f;
		if (task.$ === 2 && task.c)
		{
			task.c();
		}

		proc.f = null;

		callback(_Scheduler_succeed(_Utils_Tuple0));
	});
}


/* STEP PROCESSES

type alias Process =
  { $ : tag
  , id : unique_id
  , root : Task
  , stack : null | { $: SUCCEED | FAIL, a: callback, b: stack }
  , mailbox : [msg]
  }

*/


var _Scheduler_working = false;
var _Scheduler_queue = [];


function _Scheduler_enqueue(proc)
{
	_Scheduler_queue.push(proc);
	if (_Scheduler_working)
	{
		return;
	}
	_Scheduler_working = true;
	while (proc = _Scheduler_queue.shift())
	{
		_Scheduler_step(proc);
	}
	_Scheduler_working = false;
}


function _Scheduler_step(proc)
{
	while (proc.f)
	{
		var rootTag = proc.f.$;
		if (rootTag === 0 || rootTag === 1)
		{
			while (proc.g && proc.g.$ !== rootTag)
			{
				proc.g = proc.g.i;
			}
			if (!proc.g)
			{
				return;
			}
			proc.f = proc.g.b(proc.f.a);
			proc.g = proc.g.i;
		}
		else if (rootTag === 2)
		{
			proc.f.c = proc.f.b(function(newRoot) {
				proc.f = newRoot;
				_Scheduler_enqueue(proc);
			});
			return;
		}
		else if (rootTag === 5)
		{
			if (proc.h.length === 0)
			{
				return;
			}
			proc.f = proc.f.b(proc.h.shift());
		}
		else // if (rootTag === 3 || rootTag === 4)
		{
			proc.g = {
				$: rootTag === 3 ? 0 : 1,
				b: proc.f.b,
				i: proc.g
			};
			proc.f = proc.f.d;
		}
	}
}



function _Process_sleep(time)
{
	return _Scheduler_binding(function(callback) {
		var id = setTimeout(function() {
			callback(_Scheduler_succeed(_Utils_Tuple0));
		}, time);

		return function() { clearTimeout(id); };
	});
}




// PROGRAMS


var _Platform_worker = F4(function(impl, flagDecoder, debugMetadata, args)
{
	return _Platform_initialize(
		flagDecoder,
		args,
		impl.init,
		impl.update,
		impl.subscriptions,
		function() { return function() {} }
	);
});



// INITIALIZE A PROGRAM


function _Platform_initialize(flagDecoder, args, init, update, subscriptions, stepperBuilder)
{
	var result = A2(_Json_run, flagDecoder, _Json_wrap(args ? args['flags'] : undefined));
	$elm$core$Result$isOk(result) || _Debug_crash(2 /**/, _Json_errorToString(result.a) /**/);
	var managers = {};
	var initPair = init(result.a);
	var model = initPair.a;
	var stepper = stepperBuilder(sendToApp, model);
	var ports = _Platform_setupEffects(managers, sendToApp);

	function sendToApp(msg, viewMetadata)
	{
		var pair = A2(update, msg, model);
		stepper(model = pair.a, viewMetadata);
		_Platform_enqueueEffects(managers, pair.b, subscriptions(model));
	}

	_Platform_enqueueEffects(managers, initPair.b, subscriptions(model));

	return ports ? { ports: ports } : {};
}



// TRACK PRELOADS
//
// This is used by code in elm/browser and elm/http
// to register any HTTP requests that are triggered by init.
//


var _Platform_preload;


function _Platform_registerPreload(url)
{
	_Platform_preload.add(url);
}



// EFFECT MANAGERS


var _Platform_effectManagers = {};


function _Platform_setupEffects(managers, sendToApp)
{
	var ports;

	// setup all necessary effect managers
	for (var key in _Platform_effectManagers)
	{
		var manager = _Platform_effectManagers[key];

		if (manager.a)
		{
			ports = ports || {};
			ports[key] = manager.a(key, sendToApp);
		}

		managers[key] = _Platform_instantiateManager(manager, sendToApp);
	}

	return ports;
}


function _Platform_createManager(init, onEffects, onSelfMsg, cmdMap, subMap)
{
	return {
		b: init,
		c: onEffects,
		d: onSelfMsg,
		e: cmdMap,
		f: subMap
	};
}


function _Platform_instantiateManager(info, sendToApp)
{
	var router = {
		g: sendToApp,
		h: undefined
	};

	var onEffects = info.c;
	var onSelfMsg = info.d;
	var cmdMap = info.e;
	var subMap = info.f;

	function loop(state)
	{
		return A2(_Scheduler_andThen, loop, _Scheduler_receive(function(msg)
		{
			var value = msg.a;

			if (msg.$ === 0)
			{
				return A3(onSelfMsg, router, value, state);
			}

			return cmdMap && subMap
				? A4(onEffects, router, value.i, value.j, state)
				: A3(onEffects, router, cmdMap ? value.i : value.j, state);
		}));
	}

	return router.h = _Scheduler_rawSpawn(A2(_Scheduler_andThen, loop, info.b));
}



// ROUTING


var _Platform_sendToApp = F2(function(router, msg)
{
	return _Scheduler_binding(function(callback)
	{
		router.g(msg);
		callback(_Scheduler_succeed(_Utils_Tuple0));
	});
});


var _Platform_sendToSelf = F2(function(router, msg)
{
	return A2(_Scheduler_send, router.h, {
		$: 0,
		a: msg
	});
});



// BAGS


function _Platform_leaf(home)
{
	return function(value)
	{
		return {
			$: 1,
			k: home,
			l: value
		};
	};
}


function _Platform_batch(list)
{
	return {
		$: 2,
		m: list
	};
}


var _Platform_map = F2(function(tagger, bag)
{
	return {
		$: 3,
		n: tagger,
		o: bag
	}
});



// PIPE BAGS INTO EFFECT MANAGERS
//
// Effects must be queued!
//
// Say your init contains a synchronous command, like Time.now or Time.here
//
//   - This will produce a batch of effects (FX_1)
//   - The synchronous task triggers the subsequent `update` call
//   - This will produce a batch of effects (FX_2)
//
// If we just start dispatching FX_2, subscriptions from FX_2 can be processed
// before subscriptions from FX_1. No good! Earlier versions of this code had
// this problem, leading to these reports:
//
//   https://github.com/elm/core/issues/980
//   https://github.com/elm/core/pull/981
//   https://github.com/elm/compiler/issues/1776
//
// The queue is necessary to avoid ordering issues for synchronous commands.


// Why use true/false here? Why not just check the length of the queue?
// The goal is to detect "are we currently dispatching effects?" If we
// are, we need to bail and let the ongoing while loop handle things.
//
// Now say the queue has 1 element. When we dequeue the final element,
// the queue will be empty, but we are still actively dispatching effects.
// So you could get queue jumping in a really tricky category of cases.
//
var _Platform_effectsQueue = [];
var _Platform_effectsActive = false;


function _Platform_enqueueEffects(managers, cmdBag, subBag)
{
	_Platform_effectsQueue.push({ p: managers, q: cmdBag, r: subBag });

	if (_Platform_effectsActive) return;

	_Platform_effectsActive = true;
	for (var fx; fx = _Platform_effectsQueue.shift(); )
	{
		_Platform_dispatchEffects(fx.p, fx.q, fx.r);
	}
	_Platform_effectsActive = false;
}


function _Platform_dispatchEffects(managers, cmdBag, subBag)
{
	var effectsDict = {};
	_Platform_gatherEffects(true, cmdBag, effectsDict, null);
	_Platform_gatherEffects(false, subBag, effectsDict, null);

	for (var home in managers)
	{
		_Scheduler_rawSend(managers[home], {
			$: 'fx',
			a: effectsDict[home] || { i: _List_Nil, j: _List_Nil }
		});
	}
}


function _Platform_gatherEffects(isCmd, bag, effectsDict, taggers)
{
	switch (bag.$)
	{
		case 1:
			var home = bag.k;
			var effect = _Platform_toEffect(isCmd, home, taggers, bag.l);
			effectsDict[home] = _Platform_insert(isCmd, effect, effectsDict[home]);
			return;

		case 2:
			for (var list = bag.m; list.b; list = list.b) // WHILE_CONS
			{
				_Platform_gatherEffects(isCmd, list.a, effectsDict, taggers);
			}
			return;

		case 3:
			_Platform_gatherEffects(isCmd, bag.o, effectsDict, {
				s: bag.n,
				t: taggers
			});
			return;
	}
}


function _Platform_toEffect(isCmd, home, taggers, value)
{
	function applyTaggers(x)
	{
		for (var temp = taggers; temp; temp = temp.t)
		{
			x = temp.s(x);
		}
		return x;
	}

	var map = isCmd
		? _Platform_effectManagers[home].e
		: _Platform_effectManagers[home].f;

	return A2(map, applyTaggers, value)
}


function _Platform_insert(isCmd, newEffect, effects)
{
	effects = effects || { i: _List_Nil, j: _List_Nil };

	isCmd
		? (effects.i = _List_Cons(newEffect, effects.i))
		: (effects.j = _List_Cons(newEffect, effects.j));

	return effects;
}



// PORTS


function _Platform_checkPortName(name)
{
	if (_Platform_effectManagers[name])
	{
		_Debug_crash(3, name)
	}
}



// OUTGOING PORTS


function _Platform_outgoingPort(name, converter)
{
	_Platform_checkPortName(name);
	_Platform_effectManagers[name] = {
		e: _Platform_outgoingPortMap,
		u: converter,
		a: _Platform_setupOutgoingPort
	};
	return _Platform_leaf(name);
}


var _Platform_outgoingPortMap = F2(function(tagger, value) { return value; });


function _Platform_setupOutgoingPort(name)
{
	var subs = [];
	var converter = _Platform_effectManagers[name].u;

	// CREATE MANAGER

	var init = _Process_sleep(0);

	_Platform_effectManagers[name].b = init;
	_Platform_effectManagers[name].c = F3(function(router, cmdList, state)
	{
		for ( ; cmdList.b; cmdList = cmdList.b) // WHILE_CONS
		{
			// grab a separate reference to subs in case unsubscribe is called
			var currentSubs = subs;
			var value = _Json_unwrap(converter(cmdList.a));
			for (var i = 0; i < currentSubs.length; i++)
			{
				currentSubs[i](value);
			}
		}
		return init;
	});

	// PUBLIC API

	function subscribe(callback)
	{
		subs.push(callback);
	}

	function unsubscribe(callback)
	{
		// copy subs into a new array in case unsubscribe is called within a
		// subscribed callback
		subs = subs.slice();
		var index = subs.indexOf(callback);
		if (index >= 0)
		{
			subs.splice(index, 1);
		}
	}

	return {
		subscribe: subscribe,
		unsubscribe: unsubscribe
	};
}



// INCOMING PORTS


function _Platform_incomingPort(name, converter)
{
	_Platform_checkPortName(name);
	_Platform_effectManagers[name] = {
		f: _Platform_incomingPortMap,
		u: converter,
		a: _Platform_setupIncomingPort
	};
	return _Platform_leaf(name);
}


var _Platform_incomingPortMap = F2(function(tagger, finalTagger)
{
	return function(value)
	{
		return tagger(finalTagger(value));
	};
});


function _Platform_setupIncomingPort(name, sendToApp)
{
	var subs = _List_Nil;
	var converter = _Platform_effectManagers[name].u;

	// CREATE MANAGER

	var init = _Scheduler_succeed(null);

	_Platform_effectManagers[name].b = init;
	_Platform_effectManagers[name].c = F3(function(router, subList, state)
	{
		subs = subList;
		return init;
	});

	// PUBLIC API

	function send(incomingValue)
	{
		var result = A2(_Json_run, converter, _Json_wrap(incomingValue));

		$elm$core$Result$isOk(result) || _Debug_crash(4, name, result.a);

		var value = result.a;
		for (var temp = subs; temp.b; temp = temp.b) // WHILE_CONS
		{
			sendToApp(temp.a(value));
		}
	}

	return { send: send };
}



// EXPORT ELM MODULES
//
// Have DEBUG and PROD versions so that we can (1) give nicer errors in
// debug mode and (2) not pay for the bits needed for that in prod mode.
//


function _Platform_export_UNUSED(exports)
{
	scope['Elm']
		? _Platform_mergeExportsProd(scope['Elm'], exports)
		: scope['Elm'] = exports;
}


function _Platform_mergeExportsProd(obj, exports)
{
	for (var name in exports)
	{
		(name in obj)
			? (name == 'init')
				? _Debug_crash(6)
				: _Platform_mergeExportsProd(obj[name], exports[name])
			: (obj[name] = exports[name]);
	}
}


function _Platform_export(exports)
{
	scope['Elm']
		? _Platform_mergeExportsDebug('Elm', scope['Elm'], exports)
		: scope['Elm'] = exports;
}


function _Platform_mergeExportsDebug(moduleName, obj, exports)
{
	for (var name in exports)
	{
		(name in obj)
			? (name == 'init')
				? _Debug_crash(6, moduleName)
				: _Platform_mergeExportsDebug(moduleName + '.' + name, obj[name], exports[name])
			: (obj[name] = exports[name]);
	}
}
var $elm$core$Basics$EQ = {$: 'EQ'};
var $elm$core$Basics$LT = {$: 'LT'};
var $elm$core$List$cons = _List_cons;
var $elm$core$Elm$JsArray$foldr = _JsArray_foldr;
var $elm$core$Array$foldr = F3(
	function (func, baseCase, _v0) {
		var tree = _v0.c;
		var tail = _v0.d;
		var helper = F2(
			function (node, acc) {
				if (node.$ === 'SubTree') {
					var subTree = node.a;
					return A3($elm$core$Elm$JsArray$foldr, helper, acc, subTree);
				} else {
					var values = node.a;
					return A3($elm$core$Elm$JsArray$foldr, func, acc, values);
				}
			});
		return A3(
			$elm$core$Elm$JsArray$foldr,
			helper,
			A3($elm$core$Elm$JsArray$foldr, func, baseCase, tail),
			tree);
	});
var $elm$core$Array$toList = function (array) {
	return A3($elm$core$Array$foldr, $elm$core$List$cons, _List_Nil, array);
};
var $elm$core$Dict$foldr = F3(
	function (func, acc, t) {
		foldr:
		while (true) {
			if (t.$ === 'RBEmpty_elm_builtin') {
				return acc;
			} else {
				var key = t.b;
				var value = t.c;
				var left = t.d;
				var right = t.e;
				var $temp$func = func,
					$temp$acc = A3(
					func,
					key,
					value,
					A3($elm$core$Dict$foldr, func, acc, right)),
					$temp$t = left;
				func = $temp$func;
				acc = $temp$acc;
				t = $temp$t;
				continue foldr;
			}
		}
	});
var $elm$core$Dict$toList = function (dict) {
	return A3(
		$elm$core$Dict$foldr,
		F3(
			function (key, value, list) {
				return A2(
					$elm$core$List$cons,
					_Utils_Tuple2(key, value),
					list);
			}),
		_List_Nil,
		dict);
};
var $elm$core$Dict$keys = function (dict) {
	return A3(
		$elm$core$Dict$foldr,
		F3(
			function (key, value, keyList) {
				return A2($elm$core$List$cons, key, keyList);
			}),
		_List_Nil,
		dict);
};
var $elm$core$Set$toList = function (_v0) {
	var dict = _v0.a;
	return $elm$core$Dict$keys(dict);
};
var $elm$core$Basics$GT = {$: 'GT'};
var $elm$core$Basics$identity = function (x) {
	return x;
};
var $author$project$BridgeReplay$Run = function (a) {
	return {$: 'Run', a: a};
};
var $elm$core$Result$Err = function (a) {
	return {$: 'Err', a: a};
};
var $elm$json$Json$Decode$Failure = F2(
	function (a, b) {
		return {$: 'Failure', a: a, b: b};
	});
var $elm$json$Json$Decode$Field = F2(
	function (a, b) {
		return {$: 'Field', a: a, b: b};
	});
var $elm$json$Json$Decode$Index = F2(
	function (a, b) {
		return {$: 'Index', a: a, b: b};
	});
var $elm$core$Result$Ok = function (a) {
	return {$: 'Ok', a: a};
};
var $elm$json$Json$Decode$OneOf = function (a) {
	return {$: 'OneOf', a: a};
};
var $elm$core$Basics$False = {$: 'False'};
var $elm$core$Basics$add = _Basics_add;
var $elm$core$Maybe$Just = function (a) {
	return {$: 'Just', a: a};
};
var $elm$core$Maybe$Nothing = {$: 'Nothing'};
var $elm$core$String$all = _String_all;
var $elm$core$Basics$and = _Basics_and;
var $elm$core$Basics$append = _Utils_append;
var $elm$json$Json$Encode$encode = _Json_encode;
var $elm$core$String$fromInt = _String_fromNumber;
var $elm$core$String$join = F2(
	function (sep, chunks) {
		return A2(
			_String_join,
			sep,
			_List_toArray(chunks));
	});
var $elm$core$String$split = F2(
	function (sep, string) {
		return _List_fromArray(
			A2(_String_split, sep, string));
	});
var $elm$json$Json$Decode$indent = function (str) {
	return A2(
		$elm$core$String$join,
		'\u000A    ',
		A2($elm$core$String$split, '\u000A', str));
};
var $elm$core$List$foldl = F3(
	function (func, acc, list) {
		foldl:
		while (true) {
			if (!list.b) {
				return acc;
			} else {
				var x = list.a;
				var xs = list.b;
				var $temp$func = func,
					$temp$acc = A2(func, x, acc),
					$temp$list = xs;
				func = $temp$func;
				acc = $temp$acc;
				list = $temp$list;
				continue foldl;
			}
		}
	});
var $elm$core$List$length = function (xs) {
	return A3(
		$elm$core$List$foldl,
		F2(
			function (_v0, i) {
				return i + 1;
			}),
		0,
		xs);
};
var $elm$core$List$map2 = _List_map2;
var $elm$core$Basics$le = _Utils_le;
var $elm$core$Basics$sub = _Basics_sub;
var $elm$core$List$rangeHelp = F3(
	function (lo, hi, list) {
		rangeHelp:
		while (true) {
			if (_Utils_cmp(lo, hi) < 1) {
				var $temp$lo = lo,
					$temp$hi = hi - 1,
					$temp$list = A2($elm$core$List$cons, hi, list);
				lo = $temp$lo;
				hi = $temp$hi;
				list = $temp$list;
				continue rangeHelp;
			} else {
				return list;
			}
		}
	});
var $elm$core$List$range = F2(
	function (lo, hi) {
		return A3($elm$core$List$rangeHelp, lo, hi, _List_Nil);
	});
var $elm$core$List$indexedMap = F2(
	function (f, xs) {
		return A3(
			$elm$core$List$map2,
			f,
			A2(
				$elm$core$List$range,
				0,
				$elm$core$List$length(xs) - 1),
			xs);
	});
var $elm$core$Char$toCode = _Char_toCode;
var $elm$core$Char$isLower = function (_char) {
	var code = $elm$core$Char$toCode(_char);
	return (97 <= code) && (code <= 122);
};
var $elm$core$Char$isUpper = function (_char) {
	var code = $elm$core$Char$toCode(_char);
	return (code <= 90) && (65 <= code);
};
var $elm$core$Basics$or = _Basics_or;
var $elm$core$Char$isAlpha = function (_char) {
	return $elm$core$Char$isLower(_char) || $elm$core$Char$isUpper(_char);
};
var $elm$core$Char$isDigit = function (_char) {
	var code = $elm$core$Char$toCode(_char);
	return (code <= 57) && (48 <= code);
};
var $elm$core$Char$isAlphaNum = function (_char) {
	return $elm$core$Char$isLower(_char) || ($elm$core$Char$isUpper(_char) || $elm$core$Char$isDigit(_char));
};
var $elm$core$List$reverse = function (list) {
	return A3($elm$core$List$foldl, $elm$core$List$cons, _List_Nil, list);
};
var $elm$core$String$uncons = _String_uncons;
var $elm$json$Json$Decode$errorOneOf = F2(
	function (i, error) {
		return '\u000A\u000A(' + ($elm$core$String$fromInt(i + 1) + (') ' + $elm$json$Json$Decode$indent(
			$elm$json$Json$Decode$errorToString(error))));
	});
var $elm$json$Json$Decode$errorToString = function (error) {
	return A2($elm$json$Json$Decode$errorToStringHelp, error, _List_Nil);
};
var $elm$json$Json$Decode$errorToStringHelp = F2(
	function (error, context) {
		errorToStringHelp:
		while (true) {
			switch (error.$) {
				case 'Field':
					var f = error.a;
					var err = error.b;
					var isSimple = function () {
						var _v1 = $elm$core$String$uncons(f);
						if (_v1.$ === 'Nothing') {
							return false;
						} else {
							var _v2 = _v1.a;
							var _char = _v2.a;
							var rest = _v2.b;
							return $elm$core$Char$isAlpha(_char) && A2($elm$core$String$all, $elm$core$Char$isAlphaNum, rest);
						}
					}();
					var fieldName = isSimple ? ('.' + f) : ('[\u0027' + (f + '\u0027]'));
					var $temp$error = err,
						$temp$context = A2($elm$core$List$cons, fieldName, context);
					error = $temp$error;
					context = $temp$context;
					continue errorToStringHelp;
				case 'Index':
					var i = error.a;
					var err = error.b;
					var indexName = '[' + ($elm$core$String$fromInt(i) + ']');
					var $temp$error = err,
						$temp$context = A2($elm$core$List$cons, indexName, context);
					error = $temp$error;
					context = $temp$context;
					continue errorToStringHelp;
				case 'OneOf':
					var errors = error.a;
					if (!errors.b) {
						return 'Ran into a Json.Decode.oneOf with no possibilities' + function () {
							if (!context.b) {
								return '!';
							} else {
								return ' at json' + A2(
									$elm$core$String$join,
									'',
									$elm$core$List$reverse(context));
							}
						}();
					} else {
						if (!errors.b.b) {
							var err = errors.a;
							var $temp$error = err,
								$temp$context = context;
							error = $temp$error;
							context = $temp$context;
							continue errorToStringHelp;
						} else {
							var starter = function () {
								if (!context.b) {
									return 'Json.Decode.oneOf';
								} else {
									return 'The Json.Decode.oneOf at json' + A2(
										$elm$core$String$join,
										'',
										$elm$core$List$reverse(context));
								}
							}();
							var introduction = starter + (' failed in the following ' + ($elm$core$String$fromInt(
								$elm$core$List$length(errors)) + ' ways:'));
							return A2(
								$elm$core$String$join,
								'\u000A\u000A',
								A2(
									$elm$core$List$cons,
									introduction,
									A2($elm$core$List$indexedMap, $elm$json$Json$Decode$errorOneOf, errors)));
						}
					}
				default:
					var msg = error.a;
					var json = error.b;
					var introduction = function () {
						if (!context.b) {
							return 'Problem with the given value:\u000A\u000A';
						} else {
							return 'Problem with the value at json' + (A2(
								$elm$core$String$join,
								'',
								$elm$core$List$reverse(context)) + ':\u000A\u000A    ');
						}
					}();
					return introduction + ($elm$json$Json$Decode$indent(
						A2($elm$json$Json$Encode$encode, 4, json)) + ('\u000A\u000A' + msg));
			}
		}
	});
var $elm$core$Array$branchFactor = 32;
var $elm$core$Array$Array_elm_builtin = F4(
	function (a, b, c, d) {
		return {$: 'Array_elm_builtin', a: a, b: b, c: c, d: d};
	});
var $elm$core$Elm$JsArray$empty = _JsArray_empty;
var $elm$core$Basics$ceiling = _Basics_ceiling;
var $elm$core$Basics$fdiv = _Basics_fdiv;
var $elm$core$Basics$logBase = F2(
	function (base, number) {
		return _Basics_log(number) / _Basics_log(base);
	});
var $elm$core$Basics$toFloat = _Basics_toFloat;
var $elm$core$Array$shiftStep = $elm$core$Basics$ceiling(
	A2($elm$core$Basics$logBase, 2, $elm$core$Array$branchFactor));
var $elm$core$Array$empty = A4($elm$core$Array$Array_elm_builtin, 0, $elm$core$Array$shiftStep, $elm$core$Elm$JsArray$empty, $elm$core$Elm$JsArray$empty);
var $elm$core$Elm$JsArray$initialize = _JsArray_initialize;
var $elm$core$Array$Leaf = function (a) {
	return {$: 'Leaf', a: a};
};
var $elm$core$Basics$apL = F2(
	function (f, x) {
		return f(x);
	});
var $elm$core$Basics$apR = F2(
	function (x, f) {
		return f(x);
	});
var $elm$core$Basics$eq = _Utils_equal;
var $elm$core$Basics$floor = _Basics_floor;
var $elm$core$Elm$JsArray$length = _JsArray_length;
var $elm$core$Basics$gt = _Utils_gt;
var $elm$core$Basics$max = F2(
	function (x, y) {
		return (_Utils_cmp(x, y) > 0) ? x : y;
	});
var $elm$core$Basics$mul = _Basics_mul;
var $elm$core$Array$SubTree = function (a) {
	return {$: 'SubTree', a: a};
};
var $elm$core$Elm$JsArray$initializeFromList = _JsArray_initializeFromList;
var $elm$core$Array$compressNodes = F2(
	function (nodes, acc) {
		compressNodes:
		while (true) {
			var _v0 = A2($elm$core$Elm$JsArray$initializeFromList, $elm$core$Array$branchFactor, nodes);
			var node = _v0.a;
			var remainingNodes = _v0.b;
			var newAcc = A2(
				$elm$core$List$cons,
				$elm$core$Array$SubTree(node),
				acc);
			if (!remainingNodes.b) {
				return $elm$core$List$reverse(newAcc);
			} else {
				var $temp$nodes = remainingNodes,
					$temp$acc = newAcc;
				nodes = $temp$nodes;
				acc = $temp$acc;
				continue compressNodes;
			}
		}
	});
var $elm$core$Tuple$first = function (_v0) {
	var x = _v0.a;
	return x;
};
var $elm$core$Array$treeFromBuilder = F2(
	function (nodeList, nodeListSize) {
		treeFromBuilder:
		while (true) {
			var newNodeSize = $elm$core$Basics$ceiling(nodeListSize / $elm$core$Array$branchFactor);
			if (newNodeSize === 1) {
				return A2($elm$core$Elm$JsArray$initializeFromList, $elm$core$Array$branchFactor, nodeList).a;
			} else {
				var $temp$nodeList = A2($elm$core$Array$compressNodes, nodeList, _List_Nil),
					$temp$nodeListSize = newNodeSize;
				nodeList = $temp$nodeList;
				nodeListSize = $temp$nodeListSize;
				continue treeFromBuilder;
			}
		}
	});
var $elm$core$Array$builderToArray = F2(
	function (reverseNodeList, builder) {
		if (!builder.nodeListSize) {
			return A4(
				$elm$core$Array$Array_elm_builtin,
				$elm$core$Elm$JsArray$length(builder.tail),
				$elm$core$Array$shiftStep,
				$elm$core$Elm$JsArray$empty,
				builder.tail);
		} else {
			var treeLen = builder.nodeListSize * $elm$core$Array$branchFactor;
			var depth = $elm$core$Basics$floor(
				A2($elm$core$Basics$logBase, $elm$core$Array$branchFactor, treeLen - 1));
			var correctNodeList = reverseNodeList ? $elm$core$List$reverse(builder.nodeList) : builder.nodeList;
			var tree = A2($elm$core$Array$treeFromBuilder, correctNodeList, builder.nodeListSize);
			return A4(
				$elm$core$Array$Array_elm_builtin,
				$elm$core$Elm$JsArray$length(builder.tail) + treeLen,
				A2($elm$core$Basics$max, 5, depth * $elm$core$Array$shiftStep),
				tree,
				builder.tail);
		}
	});
var $elm$core$Basics$idiv = _Basics_idiv;
var $elm$core$Basics$lt = _Utils_lt;
var $elm$core$Array$initializeHelp = F5(
	function (fn, fromIndex, len, nodeList, tail) {
		initializeHelp:
		while (true) {
			if (fromIndex < 0) {
				return A2(
					$elm$core$Array$builderToArray,
					false,
					{nodeList: nodeList, nodeListSize: (len / $elm$core$Array$branchFactor) | 0, tail: tail});
			} else {
				var leaf = $elm$core$Array$Leaf(
					A3($elm$core$Elm$JsArray$initialize, $elm$core$Array$branchFactor, fromIndex, fn));
				var $temp$fn = fn,
					$temp$fromIndex = fromIndex - $elm$core$Array$branchFactor,
					$temp$len = len,
					$temp$nodeList = A2($elm$core$List$cons, leaf, nodeList),
					$temp$tail = tail;
				fn = $temp$fn;
				fromIndex = $temp$fromIndex;
				len = $temp$len;
				nodeList = $temp$nodeList;
				tail = $temp$tail;
				continue initializeHelp;
			}
		}
	});
var $elm$core$Basics$remainderBy = _Basics_remainderBy;
var $elm$core$Array$initialize = F2(
	function (len, fn) {
		if (len <= 0) {
			return $elm$core$Array$empty;
		} else {
			var tailLen = len % $elm$core$Array$branchFactor;
			var tail = A3($elm$core$Elm$JsArray$initialize, tailLen, len - tailLen, fn);
			var initialFromIndex = (len - tailLen) - $elm$core$Array$branchFactor;
			return A5($elm$core$Array$initializeHelp, fn, initialFromIndex, len, _List_Nil, tail);
		}
	});
var $elm$core$Basics$True = {$: 'True'};
var $elm$core$Result$isOk = function (result) {
	if (result.$ === 'Ok') {
		return true;
	} else {
		return false;
	}
};
var $elm$json$Json$Decode$value = _Json_decodeValue;
var $author$project$BridgeReplay$incoming = _Platform_incomingPort('incoming', $elm$json$Json$Decode$value);
var $elm$core$Platform$Cmd$batch = _Platform_batch;
var $elm$core$Platform$Cmd$none = $elm$core$Platform$Cmd$batch(_List_Nil);
var $author$project$BridgeReplay$outgoing = _Platform_outgoingPort('outgoing', $elm$core$Basics$identity);
var $elm$json$Json$Encode$bool = _Json_wrap;
var $elm$json$Json$Decode$decodeValue = _Json_run;
var $elm$json$Json$Decode$field = _Json_decodeField;
var $author$project$MenuBridge$Model = function (a) {
	return {$: 'Model', a: a};
};
var $author$project$ReceiptRouter$Model = function (a) {
	return {$: 'Model', a: a};
};
var $author$project$ReceiptRouter$empty = $author$project$ReceiptRouter$Model(_List_Nil);
var $author$project$Menu$Model = function (a) {
	return {$: 'Model', a: a};
};
var $author$project$Menu$init = $author$project$Menu$Model(
	{exhausted: false, invalidated: _List_Nil, lastOutcome: $elm$core$Maybe$Nothing, menu: $elm$core$Maybe$Nothing, nextIntent: 1, nextMenu: 1, outstanding: _List_Nil, retiredOutputs: _List_Nil});
var $author$project$MenuBridge$initial = $author$project$MenuBridge$Model(
	{menu: $author$project$Menu$init, provider: $elm$core$Maybe$Nothing, router: $author$project$ReceiptRouter$empty});
var $author$project$Shell$Detached = {$: 'Detached'};
var $author$project$UInt64$Counter = function (a) {
	return {$: 'Counter', a: a};
};
var $author$project$UInt64$zero = $author$project$UInt64$Counter('0');
var $author$project$Effects$empty = {connected: false, generation: $author$project$UInt64$zero, observed: $elm$core$Maybe$Nothing, request: $author$project$UInt64$zero, transaction: $elm$core$Maybe$Nothing};
var $author$project$Shell$initial = {binding: $elm$core$Maybe$Nothing, effects: $author$project$Effects$empty, expected: $elm$core$Maybe$Nothing, notice: 'Connecting…', phase: $author$project$Shell$Detached, reconnecting: true, request: $author$project$UInt64$zero};
var $author$project$TaskbarShell$initial = {generation: $author$project$UInt64$zero, menus: $author$project$MenuBridge$initial, picker: $elm$core$Maybe$Nothing, shell: $author$project$Shell$initial};
var $author$project$BridgeReplay$initial = {ids: _List_Nil, intents: _List_Nil, model: $author$project$TaskbarShell$initial, results: _List_Nil, sent: _List_Nil};
var $elm$json$Json$Decode$list = _Json_decodeList;
var $elm$json$Json$Encode$list = F2(
	function (func, entries) {
		return _Json_wrap(
			A3(
				$elm$core$List$foldl,
				_Json_addEntry(func),
				_Json_emptyArray(_Utils_Tuple0),
				entries));
	});
var $elm$json$Json$Encode$object = function (pairs) {
	return _Json_wrap(
		A3(
			$elm$core$List$foldl,
			F2(
				function (_v0, obj) {
					var k = _v0.a;
					var v = _v0.b;
					return A3(_Json_addField, k, v, obj);
				}),
			_Json_emptyObject(_Utils_Tuple0),
			pairs));
};
var $author$project$Shell$Act = F3(
	function (a, b, c) {
		return {$: 'Act', a: a, b: b, c: c};
	});
var $author$project$Menu$Activate = F3(
	function (a, b, c) {
		return {$: 'Activate', a: a, b: b, c: c};
	});
var $author$project$Menu$Committed = {$: 'Committed'};
var $author$project$Menu$Dismiss = function (a) {
	return {$: 'Dismiss', a: a};
};
var $author$project$Shell$Incoming = function (a) {
	return {$: 'Incoming', a: a};
};
var $author$project$TaskbarShell$MenuEvent = function (a) {
	return {$: 'MenuEvent', a: a};
};
var $author$project$TaskbarShell$Native = function (a) {
	return {$: 'Native', a: a};
};
var $author$project$TaskbarShell$OpenMenu = function (a) {
	return {$: 'OpenMenu', a: a};
};
var $author$project$TaskbarShell$Primary = F2(
	function (a, b) {
		return {$: 'Primary', a: a, b: b};
	});
var $author$project$Menu$ReceiveFor = F3(
	function (a, b, c) {
		return {$: 'ReceiveFor', a: a, b: b, c: c};
	});
var $author$project$Shell$Reconnect = {$: 'Reconnect'};
var $author$project$Shell$Refresh = {$: 'Refresh'};
var $elm$core$Maybe$andThen = F2(
	function (callback, maybeValue) {
		if (maybeValue.$ === 'Just') {
			var value = maybeValue.a;
			return callback(value);
		} else {
			return $elm$core$Maybe$Nothing;
		}
	});
var $elm$core$Result$andThen = F2(
	function (callback, result) {
		if (result.$ === 'Ok') {
			var value = result.a;
			return callback(value);
		} else {
			var msg = result.a;
			return $elm$core$Result$Err(msg);
		}
	});
var $elm$core$Maybe$map = F2(
	function (f, maybe) {
		if (maybe.$ === 'Just') {
			var value = maybe.a;
			return $elm$core$Maybe$Just(
				f(value));
		} else {
			return $elm$core$Maybe$Nothing;
		}
	});
var $author$project$MenuBridge$currentProvider = function (_v0) {
	var state = _v0.a;
	return A2(
		$elm$core$Maybe$map,
		function ($) {
			return $.snapshot;
		},
		state.provider);
};
var $elm$json$Json$Decode$andThen = _Json_andThen;
var $author$project$Provider$Raw = F7(
	function (provider, capabilitiesGeneration, context, target, heading, capabilities, entries) {
		return {capabilities: capabilities, capabilitiesGeneration: capabilitiesGeneration, context: context, entries: entries, heading: heading, provider: provider, target: target};
	});
var $author$project$Provider$Snapshot = function (a) {
	return {$: 'Snapshot', a: a};
};
var $author$project$Menu$Window = function (a) {
	return {$: 'Window', a: a};
};
var $elm$core$List$any = F2(
	function (isOkay, list) {
		any:
		while (true) {
			if (!list.b) {
				return false;
			} else {
				var x = list.a;
				var xs = list.b;
				if (isOkay(x)) {
					return true;
				} else {
					var $temp$isOkay = isOkay,
						$temp$list = xs;
					isOkay = $temp$isOkay;
					list = $temp$list;
					continue any;
				}
			}
		}
	});
var $author$project$UInt64$string = function (_v0) {
	var value = _v0.a;
	return value;
};
var $author$project$Binding$authorityIdentity = function (_v0) {
	var lifetime = _v0.a;
	var session = _v0.b;
	return $author$project$UInt64$string(lifetime) + (':' + $author$project$UInt64$string(session));
};
var $author$project$Menu$Binding = function (a) {
	return {$: 'Binding', a: a};
};
var $author$project$Menu$binding = $author$project$Menu$Binding;
var $elm$json$Json$Decode$fail = _Json_fail;
var $elm$json$Json$Decode$index = _Json_decodeIndex;
var $author$project$Provider$boundedList = F2(
	function (limit, body) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (value) {
				var _v0 = A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$index, limit, $elm$json$Json$Decode$value),
					value);
				if (_v0.$ === 'Ok') {
					return $elm$json$Json$Decode$fail('Provider array bound');
				} else {
					return $elm$json$Json$Decode$list(body);
				}
			},
			$elm$json$Json$Decode$value);
	});
var $elm$core$Basics$composeR = F3(
	function (f, g, x) {
		return g(
			f(x));
	});
var $author$project$Provider$Context = F7(
	function (_native, lifetime, session, frontend, revision, outputId, outputGeneration) {
		return {frontend: frontend, lifetime: lifetime, _native: _native, outputGeneration: outputGeneration, outputId: outputId, revision: revision, session: session};
	});
var $elm$json$Json$Decode$map7 = _Json_map7;
var $author$project$Binding$Binding = F3(
	function (a, b, c) {
		return {$: 'Binding', a: a, b: b, c: c};
	});
var $elm$json$Json$Decode$keyValuePairs = _Json_decodeKeyValuePairs;
var $elm$core$List$foldrHelper = F4(
	function (fn, acc, ctr, ls) {
		if (!ls.b) {
			return acc;
		} else {
			var a = ls.a;
			var r1 = ls.b;
			if (!r1.b) {
				return A2(fn, a, acc);
			} else {
				var b = r1.a;
				var r2 = r1.b;
				if (!r2.b) {
					return A2(
						fn,
						a,
						A2(fn, b, acc));
				} else {
					var c = r2.a;
					var r3 = r2.b;
					if (!r3.b) {
						return A2(
							fn,
							a,
							A2(
								fn,
								b,
								A2(fn, c, acc)));
					} else {
						var d = r3.a;
						var r4 = r3.b;
						var res = (ctr > 500) ? A3(
							$elm$core$List$foldl,
							fn,
							acc,
							$elm$core$List$reverse(r4)) : A4($elm$core$List$foldrHelper, fn, acc, ctr + 1, r4);
						return A2(
							fn,
							a,
							A2(
								fn,
								b,
								A2(
									fn,
									c,
									A2(fn, d, res))));
					}
				}
			}
		}
	});
var $elm$core$List$foldr = F3(
	function (fn, acc, ls) {
		return A4($elm$core$List$foldrHelper, fn, acc, 0, ls);
	});
var $elm$core$List$map = F2(
	function (f, xs) {
		return A3(
			$elm$core$List$foldr,
			F2(
				function (x, acc) {
					return A2(
						$elm$core$List$cons,
						f(x),
						acc);
				}),
			_List_Nil,
			xs);
	});
var $elm$json$Json$Decode$map3 = _Json_map3;
var $elm$core$Basics$neq = _Utils_notEqual;
var $elm$core$Basics$ge = _Utils_ge;
var $elm$core$String$isEmpty = function (string) {
	return string === '';
};
var $elm$core$String$length = _String_length;
var $elm$core$Basics$not = _Basics_not;
var $elm$core$String$startsWith = _String_startsWith;
var $elm$json$Json$Decode$string = _Json_decodeString;
var $elm$json$Json$Decode$succeed = _Json_succeed;
var $author$project$UInt64$decoder = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return ((!$elm$core$String$isEmpty(value)) && (A2(
			$elm$core$String$all,
			function (c) {
				return (_Utils_cmp(
					c,
					_Utils_chr('0')) > -1) && (_Utils_cmp(
					c,
					_Utils_chr('9')) < 1);
			},
			value) && (((value === '0') || (!A2($elm$core$String$startsWith, '0', value))) && (($elm$core$String$length(value) <= 20) && (($elm$core$String$length(value) < 20) || (value <= '18446744073709551615')))))) ? $elm$json$Json$Decode$succeed(
			$author$project$UInt64$Counter(value)) : $elm$json$Json$Decode$fail('Expected canonical uint64 string');
	},
	$elm$json$Json$Decode$string);
var $author$project$Binding$nonzero = A2(
	$elm$json$Json$Decode$andThen,
	function (v) {
		return _Utils_eq(v, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero identity') : $elm$json$Json$Decode$succeed(v);
	},
	$author$project$UInt64$decoder);
var $elm$core$List$sortBy = _List_sortBy;
var $elm$core$List$sort = function (xs) {
	return A2($elm$core$List$sortBy, $elm$core$Basics$identity, xs);
};
var $author$project$Binding$decoder = A2(
	$elm$json$Json$Decode$andThen,
	function (fields) {
		return (!_Utils_eq(
			$elm$core$List$sort(
				A2($elm$core$List$map, $elm$core$Tuple$first, fields)),
			_List_fromArray(
				['frontend', 'lifetime', 'session']))) ? $elm$json$Json$Decode$fail('Binding fields') : A4(
			$elm$json$Json$Decode$map3,
			$author$project$Binding$Binding,
			A2($elm$json$Json$Decode$field, 'lifetime', $author$project$Binding$nonzero),
			A2($elm$json$Json$Decode$field, 'session', $author$project$Binding$nonzero),
			A2($elm$json$Json$Decode$field, 'frontend', $author$project$Binding$nonzero));
	},
	$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
var $author$project$Provider$nonzero = A2(
	$elm$json$Json$Decode$andThen,
	function (counter) {
		return _Utils_eq(counter, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero provider identity') : $elm$json$Json$Decode$succeed(counter);
	},
	$author$project$UInt64$decoder);
var $elm$json$Json$Encode$string = _Json_wrap;
var $author$project$Provider$nativeDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		var _v0 = A2($elm$json$Json$Decode$decodeValue, $author$project$Binding$decoder, value);
		if (_v0.$ === 'Ok') {
			var _native = _v0.a;
			return $elm$json$Json$Decode$succeed(_native);
		} else {
			return $elm$json$Json$Decode$fail('Native provider binding');
		}
	},
	A4(
		$elm$json$Json$Decode$map3,
		F3(
			function (lifetime, session, frontend) {
				return $elm$json$Json$Encode$object(
					_List_fromArray(
						[
							_Utils_Tuple2(
							'lifetime',
							$elm$json$Json$Encode$string(
								$author$project$UInt64$string(lifetime))),
							_Utils_Tuple2(
							'session',
							$elm$json$Json$Encode$string(
								$author$project$UInt64$string(session))),
							_Utils_Tuple2(
							'frontend',
							$elm$json$Json$Encode$string(
								$author$project$UInt64$string(frontend)))
						]));
			}),
		A2($elm$json$Json$Decode$field, 'lifetime', $author$project$Provider$nonzero),
		A2($elm$json$Json$Decode$field, 'session', $author$project$Provider$nonzero),
		A2($elm$json$Json$Decode$field, 'frontend', $author$project$Provider$nonzero)));
var $author$project$Provider$strict = F2(
	function (fields, body) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? body : $elm$json$Json$Decode$fail('Unexpected provider fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$Provider$contextDecoder = A2(
	$author$project$Provider$strict,
	_List_fromArray(
		['lifetime', 'session', 'frontend', 'revision', 'outputId', 'outputGeneration']),
	A8(
		$elm$json$Json$Decode$map7,
		$author$project$Provider$Context,
		$author$project$Provider$nativeDecoder,
		A2($elm$json$Json$Decode$field, 'lifetime', $author$project$Provider$nonzero),
		A2($elm$json$Json$Decode$field, 'session', $author$project$Provider$nonzero),
		A2($elm$json$Json$Decode$field, 'frontend', $author$project$Provider$nonzero),
		A2($elm$json$Json$Decode$field, 'revision', $author$project$Provider$nonzero),
		A2($elm$json$Json$Decode$field, 'outputId', $author$project$Provider$nonzero),
		A2($elm$json$Json$Decode$field, 'outputGeneration', $author$project$Provider$nonzero)));
var $author$project$Binding$encode = function (_v0) {
	var lifetime = _v0.a;
	var session = _v0.b;
	var frontend = _v0.c;
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'lifetime',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(lifetime))),
				_Utils_Tuple2(
				'session',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(session))),
				_Utils_Tuple2(
				'frontend',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(frontend)))
			]));
};
var $author$project$Menu$AlwaysOnTop = function (a) {
	return {$: 'AlwaysOnTop', a: a};
};
var $author$project$Menu$Close = {$: 'Close'};
var $author$project$Menu$ExitFullscreen = {$: 'ExitFullscreen'};
var $author$project$Menu$Maximize = {$: 'Maximize'};
var $author$project$Menu$Minimize = {$: 'Minimize'};
var $author$project$Menu$Move = {$: 'Move'};
var $author$project$Menu$Restore = {$: 'Restore'};
var $author$project$Menu$Size = {$: 'Size'};
var $elm$json$Json$Decode$bool = _Json_decodeBool;
var $author$project$Provider$actionKinds = _List_fromArray(
	['Restore', 'Minimize', 'Move', 'Size', 'Maximize', 'Close', 'ExitFullscreen', 'AlwaysOnTop']);
var $elm$core$List$member = F2(
	function (x, xs) {
		return A2(
			$elm$core$List$any,
			function (a) {
				return _Utils_eq(a, x);
			},
			xs);
	});
var $author$project$Provider$kindDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (kind) {
		return A2($elm$core$List$member, kind, $author$project$Provider$actionKinds) ? $elm$json$Json$Decode$succeed(kind) : $elm$json$Json$Decode$fail('Unsupported window action');
	},
	$elm$json$Json$Decode$string);
var $elm$json$Json$Decode$map = _Json_map1;
var $author$project$Provider$actionDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (kind) {
		var plain = function (action) {
			return A2(
				$author$project$Provider$strict,
				_List_fromArray(
					['kind']),
				$elm$json$Json$Decode$succeed(
					_Utils_Tuple2(kind, action)));
		};
		switch (kind) {
			case 'Restore':
				return plain($author$project$Menu$Restore);
			case 'Minimize':
				return plain($author$project$Menu$Minimize);
			case 'Move':
				return plain($author$project$Menu$Move);
			case 'Size':
				return plain($author$project$Menu$Size);
			case 'Maximize':
				return plain($author$project$Menu$Maximize);
			case 'Close':
				return plain($author$project$Menu$Close);
			case 'ExitFullscreen':
				return plain($author$project$Menu$ExitFullscreen);
			case 'AlwaysOnTop':
				return A2(
					$author$project$Provider$strict,
					_List_fromArray(
						['kind', 'checked']),
					A2(
						$elm$json$Json$Decode$map,
						function (checked) {
							return _Utils_Tuple2(
								kind,
								$author$project$Menu$AlwaysOnTop(checked));
						},
						A2($elm$json$Json$Decode$field, 'checked', $elm$json$Json$Decode$bool)));
			default:
				return $elm$json$Json$Decode$fail('Unsupported window action');
		}
	},
	A2($elm$json$Json$Decode$field, 'kind', $author$project$Provider$kindDecoder));
var $elm$json$Json$Decode$map4 = _Json_map4;
var $elm$core$String$any = _String_any;
var $elm$core$String$trim = _String_trim;
var $elm$core$String$slice = _String_slice;
var $elm$core$String$dropLeft = F2(
	function (n, string) {
		return (n < 1) ? string : A3(
			$elm$core$String$slice,
			n,
			$elm$core$String$length(string),
			string);
	});
var $elm$core$String$cons = _String_cons;
var $elm$core$String$fromChar = function (_char) {
	return A2($elm$core$String$cons, _char, '');
};
var $author$project$Provider$validUnicode = function (value) {
	validUnicode:
	while (true) {
		var _v0 = $elm$core$String$uncons(value);
		if (_v0.$ === 'Nothing') {
			return true;
		} else {
			var _v1 = _v0.a;
			var character = _v1.a;
			var rest = _v1.b;
			var units = $elm$core$String$fromChar(character);
			var code = $elm$core$Char$toCode(character);
			var valid = function () {
				if ($elm$core$String$length(units) === 1) {
					return (code < 55296) || (code > 57343);
				} else {
					if ($elm$core$String$length(units) === 2) {
						var _v2 = $elm$core$String$uncons(
							A2($elm$core$String$dropLeft, 1, units));
						if (_v2.$ === 'Just') {
							var _v3 = _v2.a;
							var second = _v3.a;
							var low = $elm$core$Char$toCode(second);
							return (low >= 56320) && ((low <= 57343) && ((code >= 65536) && (code <= 1114111)));
						} else {
							return false;
						}
					} else {
						return false;
					}
				}
			}();
			if (valid) {
				var $temp$value = rest;
				value = $temp$value;
				continue validUnicode;
			} else {
				return false;
			}
		}
	}
};
var $author$project$Provider$textDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		var forbidden = function (character) {
			var code = $elm$core$Char$toCode(character);
			return (code < 32) || (((code >= 127) && (code <= 159)) || ((code >= 55296) && (code <= 57343)));
		};
		return (($elm$core$String$length(value) > 256) || ((!$author$project$Provider$validUnicode(value)) || ($elm$core$String$isEmpty(
			$elm$core$String$trim(value)) || A2($elm$core$String$any, forbidden, value)))) ? $elm$json$Json$Decode$fail('Invalid provider label/title') : $elm$json$Json$Decode$succeed(value);
	},
	$elm$json$Json$Decode$string);
var $author$project$Provider$entryDecoder = A2(
	$author$project$Provider$strict,
	_List_fromArray(
		['id', 'label', 'enabled', 'action']),
	A5(
		$elm$json$Json$Decode$map4,
		F4(
			function (identity, label, enabled, _v0) {
				var kind = _v0.a;
				var action = _v0.b;
				return {
					id: $author$project$UInt64$string(identity),
					item: {action: action, enabled: enabled, label: label},
					kind: kind
				};
			}),
		A2($elm$json$Json$Decode$field, 'id', $author$project$Provider$nonzero),
		A2($elm$json$Json$Decode$field, 'label', $author$project$Provider$textDecoder),
		A2($elm$json$Json$Decode$field, 'enabled', $elm$json$Json$Decode$bool),
		A2($elm$json$Json$Decode$field, 'action', $author$project$Provider$actionDecoder)));
var $elm$core$Set$Set_elm_builtin = function (a) {
	return {$: 'Set_elm_builtin', a: a};
};
var $elm$core$Dict$RBEmpty_elm_builtin = {$: 'RBEmpty_elm_builtin'};
var $elm$core$Dict$empty = $elm$core$Dict$RBEmpty_elm_builtin;
var $elm$core$Set$empty = $elm$core$Set$Set_elm_builtin($elm$core$Dict$empty);
var $elm$core$Dict$Black = {$: 'Black'};
var $elm$core$Dict$RBNode_elm_builtin = F5(
	function (a, b, c, d, e) {
		return {$: 'RBNode_elm_builtin', a: a, b: b, c: c, d: d, e: e};
	});
var $elm$core$Dict$Red = {$: 'Red'};
var $elm$core$Dict$balance = F5(
	function (color, key, value, left, right) {
		if ((right.$ === 'RBNode_elm_builtin') && (right.a.$ === 'Red')) {
			var _v1 = right.a;
			var rK = right.b;
			var rV = right.c;
			var rLeft = right.d;
			var rRight = right.e;
			if ((left.$ === 'RBNode_elm_builtin') && (left.a.$ === 'Red')) {
				var _v3 = left.a;
				var lK = left.b;
				var lV = left.c;
				var lLeft = left.d;
				var lRight = left.e;
				return A5(
					$elm$core$Dict$RBNode_elm_builtin,
					$elm$core$Dict$Red,
					key,
					value,
					A5($elm$core$Dict$RBNode_elm_builtin, $elm$core$Dict$Black, lK, lV, lLeft, lRight),
					A5($elm$core$Dict$RBNode_elm_builtin, $elm$core$Dict$Black, rK, rV, rLeft, rRight));
			} else {
				return A5(
					$elm$core$Dict$RBNode_elm_builtin,
					color,
					rK,
					rV,
					A5($elm$core$Dict$RBNode_elm_builtin, $elm$core$Dict$Red, key, value, left, rLeft),
					rRight);
			}
		} else {
			if ((((left.$ === 'RBNode_elm_builtin') && (left.a.$ === 'Red')) && (left.d.$ === 'RBNode_elm_builtin')) && (left.d.a.$ === 'Red')) {
				var _v5 = left.a;
				var lK = left.b;
				var lV = left.c;
				var _v6 = left.d;
				var _v7 = _v6.a;
				var llK = _v6.b;
				var llV = _v6.c;
				var llLeft = _v6.d;
				var llRight = _v6.e;
				var lRight = left.e;
				return A5(
					$elm$core$Dict$RBNode_elm_builtin,
					$elm$core$Dict$Red,
					lK,
					lV,
					A5($elm$core$Dict$RBNode_elm_builtin, $elm$core$Dict$Black, llK, llV, llLeft, llRight),
					A5($elm$core$Dict$RBNode_elm_builtin, $elm$core$Dict$Black, key, value, lRight, right));
			} else {
				return A5($elm$core$Dict$RBNode_elm_builtin, color, key, value, left, right);
			}
		}
	});
var $elm$core$Basics$compare = _Utils_compare;
var $elm$core$Dict$insertHelp = F3(
	function (key, value, dict) {
		if (dict.$ === 'RBEmpty_elm_builtin') {
			return A5($elm$core$Dict$RBNode_elm_builtin, $elm$core$Dict$Red, key, value, $elm$core$Dict$RBEmpty_elm_builtin, $elm$core$Dict$RBEmpty_elm_builtin);
		} else {
			var nColor = dict.a;
			var nKey = dict.b;
			var nValue = dict.c;
			var nLeft = dict.d;
			var nRight = dict.e;
			var _v1 = A2($elm$core$Basics$compare, key, nKey);
			switch (_v1.$) {
				case 'LT':
					return A5(
						$elm$core$Dict$balance,
						nColor,
						nKey,
						nValue,
						A3($elm$core$Dict$insertHelp, key, value, nLeft),
						nRight);
				case 'EQ':
					return A5($elm$core$Dict$RBNode_elm_builtin, nColor, nKey, value, nLeft, nRight);
				default:
					return A5(
						$elm$core$Dict$balance,
						nColor,
						nKey,
						nValue,
						nLeft,
						A3($elm$core$Dict$insertHelp, key, value, nRight));
			}
		}
	});
var $elm$core$Dict$insert = F3(
	function (key, value, dict) {
		var _v0 = A3($elm$core$Dict$insertHelp, key, value, dict);
		if ((_v0.$ === 'RBNode_elm_builtin') && (_v0.a.$ === 'Red')) {
			var _v1 = _v0.a;
			var k = _v0.b;
			var v = _v0.c;
			var l = _v0.d;
			var r = _v0.e;
			return A5($elm$core$Dict$RBNode_elm_builtin, $elm$core$Dict$Black, k, v, l, r);
		} else {
			var x = _v0;
			return x;
		}
	});
var $elm$core$Set$insert = F2(
	function (key, _v0) {
		var dict = _v0.a;
		return $elm$core$Set$Set_elm_builtin(
			A3($elm$core$Dict$insert, key, _Utils_Tuple0, dict));
	});
var $elm$core$Set$fromList = function (list) {
	return A3($elm$core$List$foldl, $elm$core$Set$insert, $elm$core$Set$empty, list);
};
var $elm$json$Json$Decode$int = _Json_decodeInt;
var $elm$json$Json$Decode$map2 = _Json_map2;
var $author$project$Menu$OutputId = function (a) {
	return {$: 'OutputId', a: a};
};
var $author$project$Menu$outputId = $author$project$Menu$OutputId;
var $elm$core$Dict$sizeHelp = F2(
	function (n, dict) {
		sizeHelp:
		while (true) {
			if (dict.$ === 'RBEmpty_elm_builtin') {
				return n;
			} else {
				var left = dict.d;
				var right = dict.e;
				var $temp$n = A2($elm$core$Dict$sizeHelp, n + 1, right),
					$temp$dict = left;
				n = $temp$n;
				dict = $temp$dict;
				continue sizeHelp;
			}
		}
	});
var $elm$core$Dict$size = function (dict) {
	return A2($elm$core$Dict$sizeHelp, 0, dict);
};
var $elm$core$Set$size = function (_v0) {
	var dict = _v0.a;
	return $elm$core$Dict$size(dict);
};
var $author$project$Provider$Target = F3(
	function (lifetime, session, incarnation) {
		return {incarnation: incarnation, lifetime: lifetime, session: session};
	});
var $author$project$Provider$targetDecoder = A2(
	$author$project$Provider$strict,
	_List_fromArray(
		['lifetime', 'session', 'incarnation']),
	A4(
		$elm$json$Json$Decode$map3,
		$author$project$Provider$Target,
		A2($elm$json$Json$Decode$field, 'lifetime', $author$project$Provider$nonzero),
		A2($elm$json$Json$Decode$field, 'session', $author$project$Provider$nonzero),
		A2($elm$json$Json$Decode$field, 'incarnation', $author$project$Provider$nonzero)));
var $author$project$Menu$WindowId = F2(
	function (a, b) {
		return {$: 'WindowId', a: a, b: b};
	});
var $author$project$Menu$windowId = $author$project$Menu$WindowId;
var $author$project$Provider$envelopeDecoder = function () {
	var version = A2(
		$elm$json$Json$Decode$andThen,
		function (number) {
			return (number === 1) ? $elm$json$Json$Decode$succeed(_Utils_Tuple0) : $elm$json$Json$Decode$fail('Provider protocol version');
		},
		A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int));
	var body = A8(
		$elm$json$Json$Decode$map7,
		$author$project$Provider$Raw,
		A2($elm$json$Json$Decode$field, 'providerId', $author$project$Provider$nonzero),
		A2($elm$json$Json$Decode$field, 'capabilityGeneration', $author$project$Provider$nonzero),
		A2($elm$json$Json$Decode$field, 'binding', $author$project$Provider$contextDecoder),
		A2($elm$json$Json$Decode$field, 'target', $author$project$Provider$targetDecoder),
		A2($elm$json$Json$Decode$field, 'title', $author$project$Provider$textDecoder),
		A2(
			$elm$json$Json$Decode$field,
			'capabilities',
			A2($author$project$Provider$boundedList, 8, $author$project$Provider$kindDecoder)),
		A2(
			$elm$json$Json$Decode$field,
			'items',
			A2($author$project$Provider$boundedList, 64, $author$project$Provider$entryDecoder)));
	return A2(
		$elm$json$Json$Decode$andThen,
		function (raw) {
			var unsupportedEnabled = A2(
				$elm$core$List$any,
				function (entry) {
					return entry.item.enabled && (!A2($elm$core$List$member, entry.kind, raw.capabilities));
				},
				raw.entries);
			var identities = A2(
				$elm$core$List$map,
				function ($) {
					return $.id;
				},
				raw.entries);
			var duplicateIds = !_Utils_eq(
				$elm$core$List$length(identities),
				$elm$core$Set$size(
					$elm$core$Set$fromList(identities)));
			var duplicateCapabilities = !_Utils_eq(
				$elm$core$List$length(raw.capabilities),
				$elm$core$Set$size(
					$elm$core$Set$fromList(raw.capabilities)));
			var coherent = _Utils_eq(raw.target.lifetime, raw.context.lifetime) && _Utils_eq(raw.target.session, raw.context.session);
			var authority = A2(
				$elm$json$Json$Encode$encode,
				0,
				A2(
					$elm$json$Json$Encode$list,
					$elm$core$Basics$identity,
					_List_fromArray(
						[
							$author$project$Binding$encode(raw.context._native),
							$elm$json$Json$Encode$string(
							$author$project$UInt64$string(raw.provider)),
							$elm$json$Json$Encode$string(
							$author$project$UInt64$string(raw.capabilitiesGeneration))
						])));
			var actions = A2(
				$elm$core$List$map,
				A2(
					$elm$core$Basics$composeR,
					function ($) {
						return $.item;
					},
					function ($) {
						return $.action;
					}),
				raw.entries);
			var uniqueActions = A3(
				$elm$core$List$foldl,
				F2(
					function (action, seen) {
						return A2($elm$core$List$member, action, seen) ? seen : A2($elm$core$List$cons, action, seen);
					}),
				_List_Nil,
				actions);
			var duplicateActions = !_Utils_eq(
				$elm$core$List$length(actions),
				$elm$core$List$length(uniqueActions));
			return ((!coherent) || (duplicateIds || (duplicateActions || (duplicateCapabilities || unsupportedEnabled)))) ? $elm$json$Json$Decode$fail('Incoherent provider identity/capabilities') : $elm$json$Json$Decode$succeed(
				$author$project$Provider$Snapshot(
					{
						binding: $author$project$Menu$binding(
							{
								authority: authority,
								output: $author$project$Menu$outputId(
									$author$project$UInt64$string(raw.context.outputId)),
								outputGeneration: $author$project$UInt64$string(raw.context.outputGeneration),
								revision: $author$project$UInt64$string(raw.context.revision),
								target: $author$project$Menu$Window(
									A2(
										$author$project$Menu$windowId,
										$author$project$Binding$authorityIdentity(raw.context._native),
										$author$project$UInt64$string(raw.target.incarnation)))
							}),
						capabilityGeneration: raw.capabilitiesGeneration,
						context: raw.context,
						incarnation: raw.target.incarnation,
						items: A2(
							$elm$core$List$map,
							function ($) {
								return $.item;
							},
							raw.entries),
						providerId: raw.provider,
						title: raw.heading
					}));
		},
		A2(
			$author$project$Provider$strict,
			_List_fromArray(
				['protocolVersion', 'providerId', 'capabilityGeneration', 'binding', 'target', 'title', 'capabilities', 'items']),
			A3(
				$elm$json$Json$Decode$map2,
				F2(
					function (_v0, raw) {
						return raw;
					}),
				version,
				body)));
}();
var $author$project$Provider$maximumBytes = 16384;
var $elm$core$String$foldl = _String_foldl;
var $author$project$Provider$utf8Bytes = function (value) {
	return A3(
		$elm$core$String$foldl,
		F2(
			function (character, total) {
				var code = $elm$core$Char$toCode(character);
				return total + ((code <= 127) ? 1 : ((code <= 2047) ? 2 : ((code <= 65535) ? 3 : 4)));
			}),
		0,
		value);
};
var $author$project$Provider$decoder = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (validated) {
				return (_Utils_cmp(
					$author$project$Provider$utf8Bytes(
						A2($elm$json$Json$Encode$encode, 0, value)),
					$author$project$Provider$maximumBytes) > 0) ? $elm$json$Json$Decode$fail('Provider encoded byte bound') : $elm$json$Json$Decode$succeed(validated);
			},
			$author$project$Provider$envelopeDecoder);
	},
	$elm$json$Json$Decode$value);
var $elm$core$String$left = F2(
	function (n, string) {
		return (n < 1) ? '' : A3($elm$core$String$slice, 0, n, string);
	});
var $author$project$Provider$errorSummary = function (error) {
	switch (error.$) {
		case 'Field':
			var field = error.a;
			var nested = error.b;
			return 'Provider field ' + (field + (': ' + $author$project$Provider$errorSummary(nested)));
		case 'Index':
			var index = error.a;
			var nested = error.b;
			return 'Provider index ' + ($elm$core$String$fromInt(index) + (': ' + $author$project$Provider$errorSummary(nested)));
		case 'OneOf':
			return 'Provider alternatives rejected';
		default:
			var reason = error.a;
			return A2($elm$core$String$left, 256, reason);
	}
};
var $elm$core$Result$mapError = F2(
	function (f, result) {
		if (result.$ === 'Ok') {
			var v = result.a;
			return $elm$core$Result$Ok(v);
		} else {
			var e = result.a;
			return $elm$core$Result$Err(
				f(e));
		}
	});
var $author$project$Provider$decode = function (value) {
	return A2(
		$elm$core$Result$mapError,
		$author$project$Provider$errorSummary,
		A2($elm$json$Json$Decode$decodeValue, $author$project$Provider$decoder, value));
};
var $elm$core$List$drop = F2(
	function (n, list) {
		drop:
		while (true) {
			if (n <= 0) {
				return list;
			} else {
				if (!list.b) {
					return list;
				} else {
					var x = list.a;
					var xs = list.b;
					var $temp$n = n - 1,
						$temp$list = xs;
					n = $temp$n;
					list = $temp$list;
					continue drop;
				}
			}
		}
	});
var $elm$core$Result$withDefault = F2(
	function (def, result) {
		if (result.$ === 'Ok') {
			var a = result.a;
			return a;
		} else {
			return def;
		}
	});
var $author$project$BridgeReplay$commandKind = function (value) {
	return A2(
		$elm$core$Result$withDefault,
		'invalid',
		A2(
			$elm$json$Json$Decode$decodeValue,
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			value));
};
var $author$project$Shell$Ready = {$: 'Ready'};
var $author$project$Effects$Pending = {$: 'Pending'};
var $elm$core$Maybe$withDefault = F2(
	function (_default, maybe) {
		if (maybe.$ === 'Just') {
			var value = maybe.a;
			return value;
		} else {
			return _default;
		}
	});
var $author$project$Effects$pending = function (model) {
	return A2(
		$elm$core$Maybe$withDefault,
		false,
		A2(
			$elm$core$Maybe$map,
			function (transaction) {
				return _Utils_eq(transaction.status, $author$project$Effects$Pending);
			},
			model.transaction));
};
var $author$project$Shell$available = function (model) {
	return _Utils_eq(model.phase, $author$project$Shell$Ready) && (!$author$project$Effects$pending(model.effects));
};
var $author$project$Effects$counter = A2($elm$core$Basics$composeR, $author$project$UInt64$string, $elm$json$Json$Encode$string);
var $author$project$Effects$encodeContext = function (context) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'lifetime',
				$author$project$Effects$counter(context.lifetime)),
				_Utils_Tuple2(
				'epoch',
				$author$project$Effects$counter(context.epoch)),
				_Utils_Tuple2(
				'output',
				$author$project$Effects$counter(context.output)),
				_Utils_Tuple2(
				'revision',
				$author$project$Effects$counter(context.revision))
			]));
};
var $author$project$Effects$operationName = function (operation) {
	switch (operation.$) {
		case 'Minimize':
			return 'minimize';
		case 'Restore':
			return 'restore';
		default:
			return 'activate';
	}
};
var $author$project$Effects$encodeIntent = function (intent) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'request',
				$author$project$Effects$counter(intent.request)),
				_Utils_Tuple2(
				'generation',
				$author$project$Effects$counter(intent.generation)),
				_Utils_Tuple2(
				'incarnation',
				$author$project$Effects$counter(intent.incarnation)),
				_Utils_Tuple2(
				'operation',
				$elm$json$Json$Encode$string(
					$author$project$Effects$operationName(intent.operation))),
				_Utils_Tuple2(
				'context',
				$author$project$Effects$encodeContext(intent.context))
			]));
};
var $elm$json$Json$Encode$null = _Json_encodeNull;
var $author$project$Effects$statusName = function (status) {
	switch (status.$) {
		case 'Pending':
			return 'Pending';
		case 'Committed':
			return 'Committed';
		case 'Refused':
			return 'Refused';
		case 'Cancelled':
			return 'Cancelled';
		default:
			return 'Unknown';
	}
};
var $author$project$ActionProjection$windows = function (_v0) {
	var rows = _v0.c;
	return rows;
};
var $author$project$Effects$encode = function (model) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'windows',
				A2(
					$elm$core$Maybe$withDefault,
					$elm$json$Json$Encode$null,
					A2(
						$elm$core$Maybe$map,
						A2(
							$elm$core$Basics$composeR,
							function ($) {
								return $.scene;
							},
							A2(
								$elm$core$Basics$composeR,
								$author$project$ActionProjection$windows,
								$elm$json$Json$Encode$list(
									function (w) {
										return $elm$json$Json$Encode$object(
											_List_fromArray(
												[
													_Utils_Tuple2(
													'incarnation',
													$author$project$Effects$counter(w.incarnation)),
													_Utils_Tuple2(
													'minimized',
													$elm$json$Json$Encode$bool(w.minimized))
												]));
									}))),
						model.observed))),
				_Utils_Tuple2(
				'connected',
				$elm$json$Json$Encode$bool(model.connected)),
				_Utils_Tuple2(
				'request',
				$author$project$Effects$counter(model.request)),
				_Utils_Tuple2(
				'generation',
				$author$project$Effects$counter(model.generation)),
				_Utils_Tuple2(
				'transaction',
				A2(
					$elm$core$Maybe$withDefault,
					$elm$json$Json$Encode$null,
					A2(
						$elm$core$Maybe$map,
						function (transaction) {
							return $elm$json$Json$Encode$object(
								_List_fromArray(
									[
										_Utils_Tuple2(
										'intent',
										$author$project$Effects$encodeIntent(transaction.intent)),
										_Utils_Tuple2(
										'status',
										$elm$json$Json$Encode$string(
											$author$project$Effects$statusName(transaction.status)))
									]));
						},
						model.transaction)))
			]));
};
var $author$project$Shell$encode = function (model) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'phase',
				$elm$json$Json$Encode$string(
					function () {
						var _v0 = model.phase;
						switch (_v0.$) {
							case 'Detached':
								return 'Detached';
							case 'Reconciling':
								return 'Reconciling';
							case 'Ready':
								return 'Ready';
							default:
								return 'Exhausted';
						}
					}())),
				_Utils_Tuple2(
				'request',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(model.request))),
				_Utils_Tuple2(
				'available',
				$elm$json$Json$Encode$bool(
					$author$project$Shell$available(model))),
				_Utils_Tuple2(
				'reconnecting',
				$elm$json$Json$Encode$bool(model.reconnecting)),
				_Utils_Tuple2(
				'effects',
				$author$project$Effects$encode(model.effects))
			]));
};
var $elm$core$List$filter = F2(
	function (isGood, list) {
		return A3(
			$elm$core$List$foldr,
			F2(
				function (x, xs) {
					return isGood(x) ? A2($elm$core$List$cons, x, xs) : xs;
				}),
			_List_Nil,
			list);
	});
var $author$project$Provider$getBinding = function (_v0) {
	var value = _v0.a;
	return value.binding;
};
var $author$project$Provider$getItems = function (_v0) {
	var value = _v0.a;
	return value.items;
};
var $author$project$Provider$incarnation = function (_v0) {
	var value = _v0.a;
	return value.incarnation;
};
var $elm$json$Json$Encode$int = _Json_wrap;
var $author$project$Menu$menuNumber = function (_v0) {
	var number = _v0.a;
	return number;
};
var $author$project$Menu$snapshot = function (_v0) {
	var state = _v0.a;
	return {
		exhausted: state.exhausted,
		invalidatedCount: $elm$core$List$length(state.invalidated),
		lastOutcome: state.lastOutcome,
		menu: state.menu,
		outstanding: $elm$core$List$length(state.outstanding),
		retiredOutputCount: $elm$core$List$length(state.retiredOutputs)
	};
};
var $author$project$MenuBridge$menuSnapshot = function (_v0) {
	var state = _v0.a;
	return $author$project$Menu$snapshot(state.menu);
};
var $author$project$Provider$nativeBinding = function (_v0) {
	var value = _v0.a;
	return value.context._native;
};
var $author$project$Provider$nativeContext = function (_v0) {
	var value = _v0.a;
	return {epoch: value.context.frontend, lifetime: value.context.lifetime, output: value.context.outputGeneration, revision: value.context.revision};
};
var $author$project$BridgeReplay$observed = function (shell) {
	var _v0 = shell.effects.observed;
	if (_v0.$ === 'Nothing') {
		return $elm$json$Json$Encode$null;
	} else {
		var snapshot = _v0.a;
		return $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'context',
					$elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'lifetime',
								$elm$json$Json$Encode$string(
									$author$project$UInt64$string(snapshot.context.lifetime))),
								_Utils_Tuple2(
								'epoch',
								$elm$json$Json$Encode$string(
									$author$project$UInt64$string(snapshot.context.epoch))),
								_Utils_Tuple2(
								'output',
								$elm$json$Json$Encode$string(
									$author$project$UInt64$string(snapshot.context.output))),
								_Utils_Tuple2(
								'revision',
								$elm$json$Json$Encode$string(
									$author$project$UInt64$string(snapshot.context.revision)))
							]))),
					_Utils_Tuple2(
					'windows',
					A2(
						$elm$json$Json$Encode$list,
						function (window) {
							return $elm$json$Json$Encode$object(
								_List_fromArray(
									[
										_Utils_Tuple2(
										'incarnation',
										$elm$json$Json$Encode$string(
											$author$project$UInt64$string(window.incarnation))),
										_Utils_Tuple2(
										'minimized',
										$elm$json$Json$Encode$bool(window.minimized)),
										_Utils_Tuple2(
										'available',
										$elm$json$Json$Encode$bool(window.available))
									]));
						},
						$author$project$ActionProjection$windows(snapshot.scene)))
				]));
	}
};
var $author$project$ReceiptRouter$count = function (_v0) {
	var entries = _v0.a;
	return $elm$core$List$length(entries);
};
var $author$project$MenuBridge$receiptCount = function (_v0) {
	var state = _v0.a;
	return $author$project$ReceiptRouter$count(state.router);
};
var $author$project$BridgeReplay$status = function (value) {
	switch (value.$) {
		case 'Ready':
			return 'ready';
		case 'Pending':
			return 'pending';
		case 'Refused':
			return 'refused';
		case 'Cancelled':
			return 'cancelled';
		default:
			return 'unknown';
	}
};
var $author$project$Provider$title = function (_v0) {
	var value = _v0.a;
	return value.title;
};
var $author$project$BridgeReplay$encode = F4(
	function (state, error, produced, expected) {
		var windowCommands = A2(
			$elm$core$List$filter,
			A2(
				$elm$core$Basics$composeR,
				$author$project$BridgeReplay$commandKind,
				$elm$core$Basics$eq('window-effect')),
			state.sent);
		var snapshot = $author$project$MenuBridge$menuSnapshot(state.model.menus);
		var producer = function () {
			if (produced.$ === 'Nothing') {
				return $elm$json$Json$Encode$null;
			} else {
				var provider = produced.a;
				return $elm$json$Json$Encode$object(
					_List_fromArray(
						[
							_Utils_Tuple2(
							'incarnation',
							$elm$json$Json$Encode$string(
								$author$project$UInt64$string(
									$author$project$Provider$incarnation(provider)))),
							_Utils_Tuple2(
							'title',
							$elm$json$Json$Encode$string(
								$author$project$Provider$title(provider))),
							_Utils_Tuple2(
							'enabled',
							A2(
								$elm$json$Json$Encode$list,
								function (item) {
									return $elm$json$Json$Encode$bool(item.enabled);
								},
								$author$project$Provider$getItems(provider))),
							_Utils_Tuple2(
							'output',
							$elm$json$Json$Encode$string(
								$author$project$UInt64$string(
									$author$project$Provider$nativeContext(provider).output))),
							_Utils_Tuple2(
							'nativeBinding',
							$author$project$Binding$encode(
								$author$project$Provider$nativeBinding(provider))),
							_Utils_Tuple2(
							'matchesExpectedBinding',
							A2(
								$elm$core$Maybe$withDefault,
								$elm$json$Json$Encode$null,
								A2(
									$elm$core$Maybe$map,
									function (reference) {
										return $elm$json$Json$Encode$bool(
											_Utils_eq(
												$author$project$Provider$getBinding(reference),
												$author$project$Provider$getBinding(provider)));
									},
									expected)))
						]));
			}
		}();
		var menu = function () {
			var _v0 = snapshot.menu;
			if (_v0.$ === 'Nothing') {
				return $elm$json$Json$Encode$null;
			} else {
				var current = _v0.a;
				return $elm$json$Json$Encode$object(
					_List_fromArray(
						[
							_Utils_Tuple2(
							'id',
							$elm$json$Json$Encode$int(
								$author$project$Menu$menuNumber(current.id))),
							_Utils_Tuple2(
							'selected',
							A2(
								$elm$core$Maybe$withDefault,
								$elm$json$Json$Encode$null,
								A2($elm$core$Maybe$map, $elm$json$Json$Encode$int, current.selected))),
							_Utils_Tuple2(
							'status',
							$elm$json$Json$Encode$string(
								$author$project$BridgeReplay$status(current.status)))
						]));
			}
		}();
		return $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'shell',
					$author$project$Shell$encode(state.model.shell)),
					_Utils_Tuple2('menu', menu),
					_Utils_Tuple2(
					'outstanding',
					$elm$json$Json$Encode$int(snapshot.outstanding)),
					_Utils_Tuple2(
					'registry',
					$elm$json$Json$Encode$int(
						$author$project$MenuBridge$receiptCount(state.model.menus))),
					_Utils_Tuple2(
					'picker',
					A2(
						$elm$core$Maybe$withDefault,
						$elm$json$Json$Encode$null,
						A2(
							$elm$core$Maybe$map,
							function (picker) {
								return $elm$json$Json$Encode$object(
									_List_fromArray(
										[
											_Utils_Tuple2(
											'key',
											$elm$json$Json$Encode$string(picker.key)),
											_Utils_Tuple2(
											'generation',
											$elm$json$Json$Encode$string(
												$author$project$UInt64$string(picker.generation)))
										]));
							},
							state.model.picker))),
					_Utils_Tuple2(
					'observed',
					$author$project$BridgeReplay$observed(state.model.shell)),
					_Utils_Tuple2(
					'commands',
					A2($elm$json$Json$Encode$list, $elm$core$Basics$identity, windowCommands)),
					_Utils_Tuple2(
					'sent',
					A2($elm$json$Json$Encode$list, $elm$core$Basics$identity, state.sent)),
					_Utils_Tuple2(
					'error',
					A2(
						$elm$core$Maybe$withDefault,
						$elm$json$Json$Encode$null,
						A2($elm$core$Maybe$map, $elm$json$Json$Encode$string, error))),
					_Utils_Tuple2('produced', producer)
				]));
	});
var $author$project$NativeProvider$counter = A2($elm$core$Basics$composeR, $author$project$UInt64$string, $elm$json$Json$Encode$string);
var $elm$core$List$head = function (list) {
	if (list.b) {
		var x = list.a;
		var xs = list.b;
		return $elm$core$Maybe$Just(x);
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$Binding$matchesContext = F3(
	function (life, epoch, _v0) {
		var lifetime = _v0.a;
		var frontend = _v0.c;
		return _Utils_eq(life, lifetime) && _Utils_eq(epoch, frontend);
	});
var $elm$core$Dict$get = F2(
	function (targetKey, dict) {
		get:
		while (true) {
			if (dict.$ === 'RBEmpty_elm_builtin') {
				return $elm$core$Maybe$Nothing;
			} else {
				var key = dict.b;
				var value = dict.c;
				var left = dict.d;
				var right = dict.e;
				var _v1 = A2($elm$core$Basics$compare, targetKey, key);
				switch (_v1.$) {
					case 'LT':
						var $temp$targetKey = targetKey,
							$temp$dict = left;
						targetKey = $temp$targetKey;
						dict = $temp$dict;
						continue get;
					case 'EQ':
						return $elm$core$Maybe$Just(value);
					default:
						var $temp$targetKey = targetKey,
							$temp$dict = right;
						targetKey = $temp$targetKey;
						dict = $temp$dict;
						continue get;
				}
			}
		}
	});
var $author$project$ActionProjection$rootOf = F2(
	function (identity, _v0) {
		var cache = _v0.d;
		return A2(
			$elm$core$Dict$get,
			$author$project$UInt64$string(identity),
			cache);
	});
var $author$project$NativeProvider$fromShell = F3(
	function (scope, incarnation, shell) {
		if (_Utils_eq(scope.outputId, $author$project$UInt64$zero) || (_Utils_eq(scope.providerId, $author$project$UInt64$zero) || _Utils_eq(scope.capabilityGeneration, $author$project$UInt64$zero))) {
			return $elm$core$Result$Err('Missing registered provider/output identity');
		} else {
			if (!_Utils_eq(shell.phase, $author$project$Shell$Ready)) {
				return $elm$core$Result$Err('Native window facts are not ready');
			} else {
				var _v0 = _Utils_Tuple2(shell.binding, shell.effects.observed);
				if ((_v0.a.$ === 'Just') && (_v0.b.$ === 'Just')) {
					var binding = _v0.a.a;
					var observed = _v0.b.a;
					if (!A3($author$project$Binding$matchesContext, observed.context.lifetime, observed.context.epoch, binding)) {
						return $elm$core$Result$Err('Native observation binding mismatch');
					} else {
						var _v1 = A2(
							$elm$core$Maybe$andThen,
							function (root) {
								return $elm$core$List$head(
									A2(
										$elm$core$List$filter,
										function (window) {
											return _Utils_eq(window.incarnation, root);
										},
										$author$project$ActionProjection$windows(observed.scene)));
							},
							A2($author$project$ActionProjection$rootOf, incarnation, observed.scene));
						if (_v1.$ === 'Nothing') {
							return $elm$core$Result$Err('Native window no longer exists');
						} else {
							var window = _v1.a;
							var positive = function (name) {
								return A2($elm$json$Json$Decode$field, name, $author$project$UInt64$decoder);
							};
							var item = F4(
								function (id, label, enabled, kind) {
									return $elm$json$Json$Encode$object(
										_List_fromArray(
											[
												_Utils_Tuple2(
												'id',
												$elm$json$Json$Encode$string(id)),
												_Utils_Tuple2(
												'label',
												$elm$json$Json$Encode$string(label)),
												_Utils_Tuple2(
												'enabled',
												$elm$json$Json$Encode$bool(enabled)),
												_Utils_Tuple2(
												'action',
												$elm$json$Json$Encode$object(
													_List_fromArray(
														[
															_Utils_Tuple2(
															'kind',
															$elm$json$Json$Encode$string(kind))
														])))
											]));
								});
							var identities = A2(
								$elm$json$Json$Decode$decodeValue,
								A4(
									$elm$json$Json$Decode$map3,
									F3(
										function (life, session, frontend) {
											return _Utils_Tuple3(life, session, frontend);
										}),
									positive('lifetime'),
									positive('session'),
									positive('frontend')),
								$author$project$Binding$encode(binding));
							if (identities.$ === 'Err') {
								return $elm$core$Result$Err('Invalid native identity');
							} else {
								var _v3 = identities.a;
								var lifetime = _v3.a;
								var session = _v3.b;
								var frontend = _v3.c;
								return $author$project$Provider$decode(
									$elm$json$Json$Encode$object(
										_List_fromArray(
											[
												_Utils_Tuple2(
												'protocolVersion',
												$elm$json$Json$Encode$int(1)),
												_Utils_Tuple2(
												'providerId',
												$author$project$NativeProvider$counter(scope.providerId)),
												_Utils_Tuple2(
												'capabilityGeneration',
												$author$project$NativeProvider$counter(scope.capabilityGeneration)),
												_Utils_Tuple2(
												'binding',
												$elm$json$Json$Encode$object(
													_List_fromArray(
														[
															_Utils_Tuple2(
															'lifetime',
															$author$project$NativeProvider$counter(lifetime)),
															_Utils_Tuple2(
															'session',
															$author$project$NativeProvider$counter(session)),
															_Utils_Tuple2(
															'frontend',
															$author$project$NativeProvider$counter(frontend)),
															_Utils_Tuple2(
															'revision',
															$author$project$NativeProvider$counter(observed.context.revision)),
															_Utils_Tuple2(
															'outputId',
															$author$project$NativeProvider$counter(scope.outputId)),
															_Utils_Tuple2(
															'outputGeneration',
															$author$project$NativeProvider$counter(observed.context.output))
														]))),
												_Utils_Tuple2(
												'target',
												$elm$json$Json$Encode$object(
													_List_fromArray(
														[
															_Utils_Tuple2(
															'lifetime',
															$author$project$NativeProvider$counter(lifetime)),
															_Utils_Tuple2(
															'session',
															$author$project$NativeProvider$counter(session)),
															_Utils_Tuple2(
															'incarnation',
															$author$project$NativeProvider$counter(window.incarnation))
														]))),
												_Utils_Tuple2(
												'title',
												$elm$json$Json$Encode$string(
													($elm$core$String$trim(window.label) === '') ? 'Window actions' : window.label)),
												_Utils_Tuple2(
												'capabilities',
												A2(
													$elm$json$Json$Encode$list,
													$elm$json$Json$Encode$string,
													_List_fromArray(
														['Restore', 'Minimize']))),
												_Utils_Tuple2(
												'items',
												A2(
													$elm$json$Json$Encode$list,
													$elm$core$Basics$identity,
													_List_fromArray(
														[
															A4(item, '1', 'Restore', window.available && window.minimized, 'Restore'),
															A4(item, '2', 'Minimize', window.available && (!window.minimized), 'Minimize')
														])))
											])));
							}
						}
					}
				} else {
					return $elm$core$Result$Err('No admitted native window observation');
				}
			}
		}
	});
var $author$project$Effects$Activate = {$: 'Activate'};
var $author$project$Effects$Minimize = {$: 'Minimize'};
var $author$project$Effects$Restore = {$: 'Restore'};
var $author$project$Effects$operationDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (name) {
		switch (name) {
			case 'minimize':
				return $elm$json$Json$Decode$succeed($author$project$Effects$Minimize);
			case 'restore':
				return $elm$json$Json$Decode$succeed($author$project$Effects$Restore);
			case 'activate':
				return $elm$json$Json$Decode$succeed($author$project$Effects$Activate);
			default:
				return $elm$json$Json$Decode$fail('Unsupported operation');
		}
	},
	$elm$json$Json$Decode$string);
var $elm$core$Tuple$pair = F2(
	function (a, b) {
		return _Utils_Tuple2(a, b);
	});
var $author$project$NativeProvider$Scope = F3(
	function (outputId, providerId, capabilityGeneration) {
		return {capabilityGeneration: capabilityGeneration, outputId: outputId, providerId: providerId};
	});
var $author$project$BridgeReplay$scopeDecoder = A4(
	$elm$json$Json$Decode$map3,
	$author$project$NativeProvider$Scope,
	A2($elm$json$Json$Decode$field, 'outputId', $author$project$UInt64$decoder),
	A2($elm$json$Json$Decode$field, 'providerId', $author$project$UInt64$decoder),
	A2($elm$json$Json$Decode$field, 'capabilityGeneration', $author$project$UInt64$decoder));
var $author$project$Shell$Stamp = F3(
	function (a, b, c) {
		return {$: 'Stamp', a: a, b: b, c: c};
	});
var $author$project$Shell$capture = function (model) {
	var _v0 = _Utils_Tuple2(model.binding, model.effects.observed);
	if ((_v0.a.$ === 'Just') && (_v0.b.$ === 'Just')) {
		var binding = _v0.a.a;
		var observed = _v0.b.a;
		return A3($author$project$Binding$matchesContext, observed.context.lifetime, observed.context.epoch, binding) ? $elm$core$Maybe$Just(
			A3($author$project$Shell$Stamp, binding, observed.context.output, observed.context.revision)) : $elm$core$Maybe$Nothing;
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $elm$core$Result$map = F2(
	function (func, ra) {
		if (ra.$ === 'Ok') {
			var a = ra.a;
			return $elm$core$Result$Ok(
				func(a));
		} else {
			var e = ra.a;
			return $elm$core$Result$Err(e);
		}
	});
var $author$project$Shell$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (!_Utils_eq(value, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Zero displayed scope');
	},
	$author$project$UInt64$decoder);
var $author$project$Shell$strict = F2(
	function (fields, decoder) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? decoder : $elm$json$Json$Decode$fail('Unexpected fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$Shell$stampDecoder = A2(
	$author$project$Shell$strict,
	_List_fromArray(
		['binding', 'output', 'revision']),
	A4(
		$elm$json$Json$Decode$map3,
		$author$project$Shell$Stamp,
		A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
		A2($elm$json$Json$Decode$field, 'output', $author$project$Shell$positive),
		A2($elm$json$Json$Decode$field, 'revision', $author$project$Shell$positive)));
var $elm$core$Result$toMaybe = function (result) {
	if (result.$ === 'Ok') {
		var v = result.a;
		return $elm$core$Maybe$Just(v);
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$BridgeReplay$stampFor = F2(
	function (value, shell) {
		return A2(
			$elm$core$Result$withDefault,
			false,
			A2(
				$elm$core$Result$map,
				A2(
					$elm$core$Basics$composeR,
					$elm$core$List$map($elm$core$Tuple$first),
					$elm$core$List$member('stamp')),
				A2(
					$elm$json$Json$Decode$decodeValue,
					$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value),
					value))) ? $elm$core$Result$toMaybe(
			A2(
				$elm$json$Json$Decode$decodeValue,
				A2($elm$json$Json$Decode$field, 'stamp', $author$project$Shell$stampDecoder),
				value)) : $author$project$Shell$capture(shell);
	});
var $elm$core$List$maybeCons = F3(
	function (f, mx, xs) {
		var _v0 = f(mx);
		if (_v0.$ === 'Just') {
			var x = _v0.a;
			return A2($elm$core$List$cons, x, xs);
		} else {
			return xs;
		}
	});
var $elm$core$List$filterMap = F2(
	function (f, xs) {
		return A3(
			$elm$core$List$foldr,
			$elm$core$List$maybeCons(f),
			_List_Nil,
			xs);
	});
var $author$project$Menu$Unknown = function (a) {
	return {$: 'Unknown', a: a};
};
var $author$project$Menu$markDisconnected = function (_v0) {
	var state = _v0.a;
	return $author$project$Menu$Model(
		_Utils_update(
			state,
			{
				menu: A2(
					$elm$core$Maybe$map,
					function (menu) {
						var _v1 = menu.status;
						if (_v1.$ === 'Pending') {
							var intent = _v1.a;
							return _Utils_update(
								menu,
								{
									status: $author$project$Menu$Unknown(intent)
								});
						} else {
							return menu;
						}
					},
					state.menu),
				outstanding: A2(
					$elm$core$List$map,
					function (entry) {
						return _Utils_update(
							entry,
							{uncertain: true});
					},
					state.outstanding)
			}));
};
var $author$project$Menu$Cancelled = {$: 'Cancelled'};
var $author$project$Menu$Dispatch = F3(
	function (a, b, c) {
		return {$: 'Dispatch', a: a, b: b, c: c};
	});
var $author$project$Menu$IntentId = function (a) {
	return {$: 'IntentId', a: a};
};
var $author$project$Menu$MenuId = function (a) {
	return {$: 'MenuId', a: a};
};
var $author$project$Menu$Pending = function (a) {
	return {$: 'Pending', a: a};
};
var $author$project$Menu$Ready = {$: 'Ready'};
var $author$project$Menu$Refused = function (a) {
	return {$: 'Refused', a: a};
};
var $author$project$Menu$Uncertain = {$: 'Uncertain'};
var $author$project$Menu$awaits = F2(
	function (id, status) {
		switch (status.$) {
			case 'Pending':
				var pending = status.a;
				return _Utils_eq(pending, id);
			case 'Unknown':
				var unknown = status.a;
				return _Utils_eq(unknown, id);
			default:
				return false;
		}
	});
var $author$project$Menu$Refusal = function (a) {
	return {$: 'Refusal', a: a};
};
var $author$project$Menu$maxLabel = 256;
var $elm$core$String$foldr = _String_foldr;
var $elm$core$String$toList = function (string) {
	return A3($elm$core$String$foldr, $elm$core$List$cons, _List_Nil, string);
};
var $author$project$Menu$boundedOutcome = function (outcome) {
	if (outcome.$ === 'Refusal') {
		var reason = outcome.a;
		var take = F2(
			function (remaining, characters) {
				if (!characters.b) {
					return '';
				} else {
					var character = characters.a;
					var rest = characters.b;
					var value = $elm$core$String$fromChar(character);
					return (_Utils_cmp(
						$elm$core$String$length(value),
						remaining) > 0) ? '' : _Utils_ap(
						value,
						A2(
							take,
							remaining - $elm$core$String$length(value),
							rest));
				}
			});
		var completePrefix = A2(
			take,
			$author$project$Menu$maxLabel,
			$elm$core$String$toList(
				A2($elm$core$String$left, $author$project$Menu$maxLabel + 1, reason)));
		return $author$project$Menu$Refusal(completePrefix);
	} else {
		return outcome;
	}
};
var $author$project$Menu$enabledIndices = function (items) {
	return A2(
		$elm$core$List$filterMap,
		$elm$core$Basics$identity,
		A2(
			$elm$core$List$indexedMap,
			F2(
				function (index, item) {
					return item.enabled ? $elm$core$Maybe$Just(index) : $elm$core$Maybe$Nothing;
				}),
			items));
};
var $author$project$Menu$itemAt = F2(
	function (index, items) {
		return (index < 0) ? $elm$core$Maybe$Nothing : $elm$core$List$head(
			A2($elm$core$List$drop, index, items));
	});
var $author$project$Menu$maxOutstanding = 64;
var $author$project$Menu$maxRetired = 128;
var $author$project$Menu$orElse = F2(
	function (fallback, value) {
		if (value.$ === 'Just') {
			return value;
		} else {
			return fallback;
		}
	});
var $author$project$Menu$navigate = F2(
	function (direction, menu) {
		var enabled = $author$project$Menu$enabledIndices(menu.items);
		var first = $elm$core$List$head(enabled);
		var last = $elm$core$List$head(
			$elm$core$List$reverse(enabled));
		var selected = function () {
			switch (direction.$) {
				case 'Home':
					return first;
				case 'End':
					return last;
				case 'Down':
					var _v1 = menu.selected;
					if (_v1.$ === 'Nothing') {
						return first;
					} else {
						var index = _v1.a;
						return A2(
							$author$project$Menu$orElse,
							first,
							$elm$core$List$head(
								A2(
									$elm$core$List$filter,
									$elm$core$Basics$lt(index),
									enabled)));
					}
				default:
					var _v2 = menu.selected;
					if (_v2.$ === 'Nothing') {
						return last;
					} else {
						var index = _v2.a;
						return A2(
							$author$project$Menu$orElse,
							last,
							$elm$core$List$head(
								$elm$core$List$reverse(
									A2(
										$elm$core$List$filter,
										$elm$core$Basics$gt(index),
										enabled))));
					}
			}
		}();
		return _Utils_update(
			menu,
			{selected: selected});
	});
var $author$project$Menu$outputTuple = function (_v0) {
	var value = _v0.a;
	return _Utils_Tuple2(value.output, value.outputGeneration);
};
var $author$project$Menu$sameTarget = F2(
	function (_v0, _v1) {
		var left = _v0.a;
		var right = _v1.a;
		return _Utils_eq(left.target, right.target);
	});
var $elm$core$Basics$composeL = F3(
	function (g, f, x) {
		return g(
			f(x));
	});
var $elm$core$List$all = F2(
	function (isOkay, list) {
		return !A2(
			$elm$core$List$any,
			A2($elm$core$Basics$composeL, $elm$core$Basics$not, isOkay),
			list);
	});
var $author$project$Menu$maxItems = 64;
var $author$project$Menu$validItems = function (items) {
	var uniqueActions = F2(
		function (remaining, seen) {
			uniqueActions:
			while (true) {
				if (!remaining.b) {
					return true;
				} else {
					var item = remaining.a;
					var rest = remaining.b;
					if (A2($elm$core$List$member, item.action, seen)) {
						return false;
					} else {
						var $temp$remaining = rest,
							$temp$seen = A2($elm$core$List$cons, item.action, seen);
						remaining = $temp$remaining;
						seen = $temp$seen;
						continue uniqueActions;
					}
				}
			}
		});
	return (_Utils_cmp(
		$elm$core$List$length(items),
		$author$project$Menu$maxItems) < 1) && (A2(
		$elm$core$List$all,
		function (item) {
			return (_Utils_cmp(
				$elm$core$String$length(item.label),
				$author$project$Menu$maxLabel) < 1) && (!$elm$core$String$isEmpty(
				$elm$core$String$trim(item.label)));
		},
		items) && A2(uniqueActions, items, _List_Nil));
};
var $author$project$Menu$update = F2(
	function (message, model) {
		var state = model.a;
		var valid = function (target) {
			return (!A2($elm$core$List$member, target, state.invalidated)) && (!A2(
				$elm$core$List$member,
				$author$project$Menu$outputTuple(target),
				state.retiredOutputs));
		};
		var unchanged = _Utils_Tuple2(model, _List_Nil);
		var editMenu = F2(
			function (id, transform) {
				var _v8 = state.menu;
				if (_v8.$ === 'Just') {
					var menu = _v8.a;
					return _Utils_eq(menu.id, id) ? _Utils_Tuple2(
						$author$project$Menu$Model(
							_Utils_update(
								state,
								{
									menu: transform(menu)
								})),
						_List_Nil) : unchanged;
				} else {
					return unchanged;
				}
			});
		switch (message.$) {
			case 'Open':
				var target = message.a;
				var items = message.b;
				if (state.exhausted || ((!valid(target)) || ((!$author$project$Menu$validItems(items)) || (state.nextMenu > 2147483647)))) {
					return unchanged;
				} else {
					var status = function () {
						var _v1 = $elm$core$List$head(
							A2(
								$elm$core$List$filter,
								function (entry) {
									return A2($author$project$Menu$sameTarget, entry.binding, target);
								},
								state.outstanding));
						if (_v1.$ === 'Nothing') {
							return $author$project$Menu$Ready;
						} else {
							var entry = _v1.a;
							return entry.uncertain ? $author$project$Menu$Unknown(entry.id) : $author$project$Menu$Pending(entry.id);
						}
					}();
					var menu = {
						binding: target,
						id: $author$project$Menu$MenuId(state.nextMenu),
						items: items,
						selected: $elm$core$List$head(
							$author$project$Menu$enabledIndices(items)),
						status: status
					};
					return _Utils_Tuple2(
						$author$project$Menu$Model(
							_Utils_update(
								state,
								{
									menu: $elm$core$Maybe$Just(menu),
									nextMenu: state.nextMenu + 1
								})),
						_List_Nil);
				}
			case 'Select':
				var id = message.a;
				var target = message.b;
				var index = message.c;
				return A2(
					editMenu,
					id,
					function (menu) {
						if (_Utils_eq(menu.binding, target) && valid(target)) {
							var _v2 = A2($author$project$Menu$itemAt, index, menu.items);
							if (_v2.$ === 'Just') {
								var item = _v2.a;
								return item.enabled ? $elm$core$Maybe$Just(
									_Utils_update(
										menu,
										{
											selected: $elm$core$Maybe$Just(index)
										})) : $elm$core$Maybe$Just(menu);
							} else {
								return $elm$core$Maybe$Just(menu);
							}
						} else {
							return $elm$core$Maybe$Just(menu);
						}
					});
			case 'Navigate':
				var id = message.a;
				var direction = message.b;
				return A2(
					editMenu,
					id,
					A2(
						$elm$core$Basics$composeR,
						$author$project$Menu$navigate(direction),
						$elm$core$Maybe$Just));
			case 'Activate':
				var id = message.a;
				var target = message.b;
				var index = message.c;
				var _v3 = state.menu;
				if (_v3.$ === 'Nothing') {
					return unchanged;
				} else {
					var menu = _v3.a;
					if (state.exhausted || ((!_Utils_eq(menu.id, id)) || ((!_Utils_eq(menu.binding, target)) || ((!valid(target)) || (state.nextIntent > 2147483647))))) {
						return unchanged;
					} else {
						if (A2(
							$elm$core$List$any,
							function (entry) {
								return A2($author$project$Menu$sameTarget, entry.binding, target);
							},
							state.outstanding)) {
							return unchanged;
						} else {
							var _v4 = A2($author$project$Menu$itemAt, index, menu.items);
							if (_v4.$ === 'Just') {
								var item = _v4.a;
								if (item.enabled && (_Utils_cmp(
									$elm$core$List$length(state.outstanding),
									$author$project$Menu$maxOutstanding) > -1)) {
									return _Utils_Tuple2(
										$author$project$Menu$Model(
											_Utils_update(
												state,
												{
													menu: $elm$core$Maybe$Just(
														_Utils_update(
															menu,
															{
																status: $author$project$Menu$Refused('Outstanding operation limit reached; reconcile existing requests.')
															}))
												})),
										_List_Nil);
								} else {
									if (item.enabled) {
										var intent = $author$project$Menu$IntentId(state.nextIntent);
										var entry = {binding: target, id: intent, uncertain: false};
										return _Utils_Tuple2(
											$author$project$Menu$Model(
												_Utils_update(
													state,
													{
														menu: $elm$core$Maybe$Just(
															_Utils_update(
																menu,
																{
																	selected: $elm$core$Maybe$Just(index),
																	status: $author$project$Menu$Pending(intent)
																})),
														nextIntent: state.nextIntent + 1,
														outstanding: A2($elm$core$List$cons, entry, state.outstanding)
													})),
											_List_fromArray(
												[
													A3($author$project$Menu$Dispatch, intent, target, item.action)
												]));
									} else {
										return unchanged;
									}
								}
							} else {
								return unchanged;
							}
						}
					}
				}
			case 'ReceiveFor':
				var intent = message.a;
				var receiptBinding = message.b;
				var receivedOutcome = message.c;
				var _v5 = $elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (entry) {
							return _Utils_eq(entry.id, intent) && _Utils_eq(entry.binding, receiptBinding);
						},
						state.outstanding));
				if (_v5.$ === 'Nothing') {
					return unchanged;
				} else {
					var entry = _v5.a;
					var outcome = $author$project$Menu$boundedOutcome(receivedOutcome);
					var outstanding = _Utils_eq(outcome, $author$project$Menu$Uncertain) ? A2(
						$elm$core$List$map,
						function (current) {
							return _Utils_eq(current.id, intent) ? _Utils_update(
								current,
								{uncertain: true}) : current;
						},
						state.outstanding) : A2(
						$elm$core$List$filter,
						function (current) {
							return !_Utils_eq(current.id, intent);
						},
						state.outstanding);
					var menu = A2(
						$elm$core$Maybe$andThen,
						function (current) {
							if (!A2($author$project$Menu$awaits, intent, current.status)) {
								return $elm$core$Maybe$Just(current);
							} else {
								switch (outcome.$) {
									case 'Committed':
										return $elm$core$Maybe$Nothing;
									case 'Refusal':
										var reason = outcome.a;
										return $elm$core$Maybe$Just(
											_Utils_update(
												current,
												{
													status: $author$project$Menu$Refused(reason)
												}));
									case 'Cancellation':
										return $elm$core$Maybe$Just(
											_Utils_update(
												current,
												{status: $author$project$Menu$Cancelled}));
									default:
										return $elm$core$Maybe$Just(
											_Utils_update(
												current,
												{
													status: $author$project$Menu$Unknown(intent)
												}));
								}
							}
						},
						state.menu);
					return _Utils_Tuple2(
						$author$project$Menu$Model(
							_Utils_update(
								state,
								{
									lastOutcome: $elm$core$Maybe$Just(
										_Utils_Tuple2(intent, outcome)),
									menu: menu,
									outstanding: outstanding
								})),
						_List_Nil);
				}
			case 'Dismiss':
				var id = message.a;
				return A2(
					editMenu,
					id,
					function (_v7) {
						return $elm$core$Maybe$Nothing;
					});
			case 'Invalidate':
				var target = message.a;
				if (A2($elm$core$List$member, target, state.invalidated) || state.exhausted) {
					return unchanged;
				} else {
					if (_Utils_cmp(
						$elm$core$List$length(state.invalidated) + $elm$core$List$length(state.retiredOutputs),
						$author$project$Menu$maxRetired) > -1) {
						return _Utils_Tuple2(
							$author$project$Menu$Model(
								_Utils_update(
									state,
									{exhausted: true, menu: $elm$core$Maybe$Nothing})),
							_List_Nil);
					} else {
						var menu = A2(
							$elm$core$Maybe$andThen,
							function (current) {
								return _Utils_eq(current.binding, target) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(current);
							},
							state.menu);
						var invalidated = A2($elm$core$List$cons, target, state.invalidated);
						return _Utils_Tuple2(
							$author$project$Menu$Model(
								_Utils_update(
									state,
									{invalidated: invalidated, menu: menu})),
							_List_Nil);
					}
				}
			default:
				var output = message.a;
				var generation = message.b;
				var retired = _Utils_Tuple2(output, generation);
				if (A2($elm$core$List$member, retired, state.retiredOutputs) || state.exhausted) {
					return unchanged;
				} else {
					if (_Utils_cmp(
						$elm$core$List$length(state.invalidated) + $elm$core$List$length(state.retiredOutputs),
						$author$project$Menu$maxRetired) > -1) {
						return _Utils_Tuple2(
							$author$project$Menu$Model(
								_Utils_update(
									state,
									{exhausted: true, menu: $elm$core$Maybe$Nothing})),
							_List_Nil);
					} else {
						var retiredOutputs = A2($elm$core$List$cons, retired, state.retiredOutputs);
						var menu = A2(
							$elm$core$Maybe$andThen,
							function (current) {
								return _Utils_eq(
									$author$project$Menu$outputTuple(current.binding),
									retired) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(current);
							},
							state.menu);
						return _Utils_Tuple2(
							$author$project$Menu$Model(
								_Utils_update(
									state,
									{menu: menu, retiredOutputs: retiredOutputs})),
							_List_Nil);
					}
				}
		}
	});
var $author$project$MenuBridge$connectionLost = function (_v0) {
	var state = _v0.a;
	var uncertain = $author$project$Menu$markDisconnected(state.menu);
	var closed = function () {
		var _v1 = $author$project$Menu$snapshot(uncertain).menu;
		if (_v1.$ === 'Nothing') {
			return uncertain;
		} else {
			var view = _v1.a;
			return A2(
				$author$project$Menu$update,
				$author$project$Menu$Dismiss(view.id),
				uncertain).a;
		}
	}();
	return $author$project$MenuBridge$Model(
		_Utils_update(
			state,
			{menu: closed}));
};
var $author$project$Menu$hasOutstandingFor = F2(
	function (window, _v0) {
		var state = _v0.a;
		return A2(
			$elm$core$List$any,
			function (entry) {
				var _v1 = entry.binding;
				var value = _v1.a;
				return _Utils_eq(
					value.target,
					$author$project$Menu$Window(window));
			},
			state.outstanding);
	});
var $author$project$MenuBridge$blockedFor = F3(
	function (incarnation, shell, _v0) {
		var state = _v0.a;
		var root = A2(
			$elm$core$Maybe$andThen,
			function (observed) {
				return A2($author$project$ActionProjection$rootOf, incarnation, observed.scene);
			},
			shell.effects.observed);
		var blocked = function () {
			var _v1 = _Utils_Tuple2(shell.binding, root);
			if ((_v1.a.$ === 'Just') && (_v1.b.$ === 'Just')) {
				var _native = _v1.a.a;
				var family = _v1.b.a;
				return A2(
					$author$project$Menu$hasOutstandingFor,
					A2(
						$author$project$Menu$windowId,
						$author$project$Binding$authorityIdentity(_native),
						$author$project$UInt64$string(family)),
					state.menu);
			} else {
				return $author$project$Menu$snapshot(state.menu).outstanding > 0;
			}
		}();
		return blocked;
	});
var $elm$core$List$isEmpty = function (xs) {
	if (!xs.b) {
		return true;
	} else {
		return false;
	}
};
var $author$project$Shell$Reconciling = {$: 'Reconciling'};
var $author$project$Shell$RestartBackend = {$: 'RestartBackend'};
var $author$project$Shell$Send = function (a) {
	return {$: 'Send', a: a};
};
var $author$project$ActionProjection$find = F2(
	function (identity, rows) {
		return $elm$core$List$head(
			A2(
				$elm$core$List$filter,
				function (w) {
					return _Utils_eq(w.incarnation, identity);
				},
				rows));
	});
var $author$project$ActionProjection$actionable = F2(
	function (identity, projection) {
		return A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.available;
				},
				A2(
					$author$project$ActionProjection$find,
					identity,
					$author$project$ActionProjection$windows(projection))));
	});
var $author$project$UInt64$compare = F2(
	function (_v0, _v1) {
		var left = _v0.a;
		var right = _v1.a;
		var _v2 = A2(
			$elm$core$Basics$compare,
			$elm$core$String$length(left),
			$elm$core$String$length(right));
		if (_v2.$ === 'EQ') {
			return A2($elm$core$Basics$compare, left, right);
		} else {
			var order = _v2;
			return order;
		}
	});
var $author$project$Effects$Context = F4(
	function (lifetime, epoch, output, revision) {
		return {epoch: epoch, lifetime: lifetime, output: output, revision: revision};
	});
var $author$project$Effects$identity = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return _Utils_eq(value, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero identity') : $elm$json$Json$Decode$succeed(value);
	},
	$author$project$UInt64$decoder);
var $author$project$Effects$strict = F2(
	function (fields, decoder) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? decoder : $elm$json$Json$Decode$fail('Unexpected/missing field');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$Effects$contextDecoder = A2(
	$author$project$Effects$strict,
	_List_fromArray(
		['lifetime', 'epoch', 'output', 'revision']),
	A5(
		$elm$json$Json$Decode$map4,
		$author$project$Effects$Context,
		A2($elm$json$Json$Decode$field, 'lifetime', $author$project$Effects$identity),
		A2($elm$json$Json$Decode$field, 'epoch', $author$project$Effects$identity),
		A2($elm$json$Json$Decode$field, 'output', $author$project$Effects$identity),
		A2($elm$json$Json$Decode$field, 'revision', $author$project$Effects$identity)));
var $author$project$ActionProjection$Admitted = F4(
	function (a, b, c, d) {
		return {$: 'Admitted', a: a, b: b, c: c, d: d};
	});
var $author$project$ActionProjection$Window = F6(
	function (incarnation, label, minimized, owner, application, available) {
		return {application: application, available: available, incarnation: incarnation, label: label, minimized: minimized, owner: owner};
	});
var $elm$json$Json$Decode$map6 = _Json_map6;
var $author$project$ActionProjection$nonzero = A2(
	$elm$json$Json$Decode$andThen,
	function (v) {
		return _Utils_eq(v, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero identity') : $elm$json$Json$Decode$succeed(v);
	},
	$author$project$UInt64$decoder);
var $elm$json$Json$Decode$null = _Json_decodeNull;
var $elm$json$Json$Decode$oneOf = _Json_oneOf;
var $elm$json$Json$Decode$nullable = function (decoder) {
	return $elm$json$Json$Decode$oneOf(
		_List_fromArray(
			[
				$elm$json$Json$Decode$null($elm$core$Maybe$Nothing),
				A2($elm$json$Json$Decode$map, $elm$core$Maybe$Just, decoder)
			]));
};
var $author$project$ActionProjection$strict = F2(
	function (fields, decoder) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? decoder : $elm$json$Json$Decode$fail('Unexpected projection fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$ActionProjection$windowDecoder = A2(
	$author$project$ActionProjection$strict,
	_List_fromArray(
		['incarnation', 'label', 'minimized', 'owner', 'application', 'available']),
	A7(
		$elm$json$Json$Decode$map6,
		$author$project$ActionProjection$Window,
		A2($elm$json$Json$Decode$field, 'incarnation', $author$project$ActionProjection$nonzero),
		A2($elm$json$Json$Decode$field, 'label', $elm$json$Json$Decode$string),
		A2($elm$json$Json$Decode$field, 'minimized', $elm$json$Json$Decode$bool),
		A2(
			$elm$json$Json$Decode$field,
			'owner',
			$elm$json$Json$Decode$nullable($author$project$ActionProjection$nonzero)),
		A2($elm$json$Json$Decode$field, 'application', $elm$json$Json$Decode$string),
		A2($elm$json$Json$Decode$field, 'available', $elm$json$Json$Decode$bool)));
var $author$project$ActionProjection$bounded = A2(
	$elm$json$Json$Decode$andThen,
	function (v) {
		var _v0 = A2(
			$elm$json$Json$Decode$decodeValue,
			A2($elm$json$Json$Decode$index, 256, $elm$json$Json$Decode$value),
			v);
		if (_v0.$ === 'Ok') {
			return $elm$json$Json$Decode$fail('Window bound');
		} else {
			return $elm$json$Json$Decode$list($author$project$ActionProjection$windowDecoder);
		}
	},
	$elm$json$Json$Decode$value);
var $elm$core$Dict$fromList = function (assocs) {
	return A3(
		$elm$core$List$foldl,
		F2(
			function (_v0, dict) {
				var key = _v0.a;
				var value = _v0.b;
				return A3($elm$core$Dict$insert, key, value, dict);
			}),
		$elm$core$Dict$empty,
		assocs);
};
var $elm$core$Maybe$map2 = F3(
	function (func, ma, mb) {
		if (ma.$ === 'Nothing') {
			return $elm$core$Maybe$Nothing;
		} else {
			var a = ma.a;
			if (mb.$ === 'Nothing') {
				return $elm$core$Maybe$Nothing;
			} else {
				var b = mb.a;
				return $elm$core$Maybe$Just(
					A2(func, a, b));
			}
		}
	});
var $author$project$ActionProjection$rootIn = F3(
	function (fuel, identity, rows) {
		return (fuel <= 0) ? $elm$core$Maybe$Nothing : A2(
			$elm$core$Maybe$andThen,
			function (w) {
				var _v0 = w.owner;
				if (_v0.$ === 'Nothing') {
					return $elm$core$Maybe$Just(w.incarnation);
				} else {
					var parent = _v0.a;
					return A3($author$project$ActionProjection$rootIn, fuel - 1, parent, rows);
				}
			},
			A2(
				$elm$core$Dict$get,
				$author$project$UInt64$string(identity),
				rows));
	});
var $author$project$ActionProjection$validText = function (value) {
	return ($elm$core$String$length(value) <= 256) && (!A2(
		$elm$core$String$any,
		function (c) {
			return $elm$core$Char$toCode(c) < 32;
		},
		value));
};
var $author$project$ActionProjection$decode = function (value) {
	return A2(
		$elm$core$Result$andThen,
		function (projection) {
			var revision_ = projection.a;
			var focus = projection.b;
			var rows = projection.c;
			var validFocus = A2(
				$elm$core$Maybe$withDefault,
				true,
				A2(
					$elm$core$Maybe$map,
					function (identity) {
						return A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (w) {
									return !w.minimized;
								},
								A2($author$project$ActionProjection$find, identity, rows)));
					},
					focus));
			var unique = A3(
				$elm$core$List$foldl,
				F2(
					function (w, seen) {
						return A2($elm$core$List$member, w.incarnation, seen) ? seen : A2($elm$core$List$cons, w.incarnation, seen);
					}),
				_List_Nil,
				rows);
			var table = $elm$core$Dict$fromList(
				A2(
					$elm$core$List$map,
					function (w) {
						return _Utils_Tuple2(
							$author$project$UInt64$string(w.incarnation),
							w);
					},
					rows));
			var roots = A3(
				$elm$core$List$foldl,
				F2(
					function (w, accumulated) {
						return A3(
							$elm$core$Maybe$map2,
							F2(
								function (cache, root) {
									return A3(
										$elm$core$Dict$insert,
										$author$project$UInt64$string(w.incarnation),
										root,
										cache);
								}),
							accumulated,
							A3($author$project$ActionProjection$rootIn, 256, w.incarnation, table));
					}),
				$elm$core$Maybe$Just($elm$core$Dict$empty),
				rows);
			var validFamily = function (w) {
				return A2(
					$elm$core$Maybe$withDefault,
					false,
					A2(
						$elm$core$Maybe$map,
						function (root) {
							return _Utils_eq(root.minimized, w.minimized);
						},
						A2(
							$elm$core$Maybe$andThen,
							function (root) {
								return A2(
									$elm$core$Dict$get,
									$author$project$UInt64$string(root),
									table);
							},
							A2(
								$elm$core$Maybe$andThen,
								$elm$core$Dict$get(
									$author$project$UInt64$string(w.incarnation)),
								roots))));
			};
			if ((!_Utils_eq(
				$elm$core$List$length(unique),
				$elm$core$List$length(rows))) || ((!validFocus) || A2(
				$elm$core$List$any,
				function (w) {
					return !($author$project$ActionProjection$validText(w.label) && ($author$project$ActionProjection$validText(w.application) && validFamily(w)));
				},
				rows))) {
				return $elm$core$Result$Err('Incoherent ownership/focus projection');
			} else {
				if (roots.$ === 'Just') {
					var cache = roots.a;
					return $elm$core$Result$Ok(
						A4($author$project$ActionProjection$Admitted, revision_, focus, rows, cache));
				} else {
					return $elm$core$Result$Err('Invalid ownership graph');
				}
			}
		},
		A2(
			$elm$core$Result$mapError,
			$elm$json$Json$Decode$errorToString,
			A2(
				$elm$json$Json$Decode$decodeValue,
				A2(
					$author$project$ActionProjection$strict,
					_List_fromArray(
						['revision', 'focused', 'windows']),
					A4(
						$elm$json$Json$Decode$map3,
						F3(
							function (revision_, focus_, rows_) {
								return A4($author$project$ActionProjection$Admitted, revision_, focus_, rows_, $elm$core$Dict$empty);
							}),
						A2($elm$json$Json$Decode$field, 'revision', $author$project$ActionProjection$nonzero),
						A2(
							$elm$json$Json$Decode$field,
							'focused',
							$elm$json$Json$Decode$nullable($author$project$ActionProjection$nonzero)),
						A2($elm$json$Json$Decode$field, 'windows', $author$project$ActionProjection$bounded))),
				value)));
};
var $author$project$Effects$Intent = F5(
	function (request, generation, incarnation, operation, context) {
		return {context: context, generation: generation, incarnation: incarnation, operation: operation, request: request};
	});
var $elm$json$Json$Decode$map5 = _Json_map5;
var $author$project$Effects$intentDecoder = A2(
	$author$project$Effects$strict,
	_List_fromArray(
		['request', 'generation', 'incarnation', 'operation', 'context']),
	A6(
		$elm$json$Json$Decode$map5,
		$author$project$Effects$Intent,
		A2($elm$json$Json$Decode$field, 'request', $author$project$Effects$identity),
		A2($elm$json$Json$Decode$field, 'generation', $author$project$Effects$identity),
		A2($elm$json$Json$Decode$field, 'incarnation', $author$project$Effects$identity),
		A2($elm$json$Json$Decode$field, 'operation', $author$project$Effects$operationDecoder),
		A2($elm$json$Json$Decode$field, 'context', $author$project$Effects$contextDecoder)));
var $author$project$ActionProjection$minimized = F2(
	function (identity, projection) {
		return A2(
			$elm$core$Maybe$map,
			function ($) {
				return $.minimized;
			},
			A2(
				$author$project$ActionProjection$find,
				identity,
				$author$project$ActionProjection$windows(projection)));
	});
var $elm$core$Char$fromCode = _Char_fromCode;
var $elm$core$String$fromList = _String_fromList;
var $author$project$UInt64$next = function (_v0) {
	var value = _v0.a;
	var add = function (digits) {
		if (!digits.b) {
			return _List_fromArray(
				[
					_Utils_chr('1')
				]);
		} else {
			if ('9' === digits.a.valueOf()) {
				var rest = digits.b;
				return A2(
					$elm$core$List$cons,
					_Utils_chr('0'),
					add(rest));
			} else {
				var digit = digits.a;
				var rest = digits.b;
				return A2(
					$elm$core$List$cons,
					$elm$core$Char$fromCode(
						$elm$core$Char$toCode(digit) + 1),
					rest);
			}
		}
	};
	return (value === '18446744073709551615') ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(
		$author$project$UInt64$Counter(
			$elm$core$String$fromList(
				$elm$core$List$reverse(
					add(
						$elm$core$List$reverse(
							$elm$core$String$toList(value)))))));
};
var $author$project$ActionProjection$revision = function (_v0) {
	var value = _v0.a;
	return value;
};
var $author$project$Effects$sameAuthority = F2(
	function (a, b) {
		return _Utils_eq(a.lifetime, b.lifetime) && (_Utils_eq(a.epoch, b.epoch) && _Utils_eq(a.output, b.output));
	});
var $author$project$ActionProjection$focused = function (_v0) {
	var focus = _v0.b;
	return focus;
};
var $elm$core$List$sortWith = _List_sortWith;
var $author$project$ActionProjection$sameState = F2(
	function (left, right) {
		var state = function (projection) {
			return A2(
				$elm$core$List$map,
				function (w) {
					return _Utils_Tuple3(
						w.incarnation,
						_Utils_Tuple2(w.minimized, w.owner),
						_Utils_Tuple2(w.application, w.available));
				},
				A2(
					$elm$core$List$sortWith,
					F2(
						function (a, b) {
							return A2($author$project$UInt64$compare, a.incarnation, b.incarnation);
						}),
					$author$project$ActionProjection$windows(projection)));
		};
		return _Utils_eq(
			$author$project$ActionProjection$focused(left),
			$author$project$ActionProjection$focused(right)) && _Utils_eq(
			state(left),
			state(right));
	});
var $author$project$Effects$Cancelled = {$: 'Cancelled'};
var $author$project$Effects$Committed = {$: 'Committed'};
var $author$project$Effects$Refused = {$: 'Refused'};
var $author$project$Effects$Unknown = {$: 'Unknown'};
var $author$project$Effects$statusDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (name) {
		switch (name) {
			case 'Committed':
				return $elm$json$Json$Decode$succeed($author$project$Effects$Committed);
			case 'Refused':
				return $elm$json$Json$Decode$succeed($author$project$Effects$Refused);
			case 'Cancelled':
				return $elm$json$Json$Decode$succeed($author$project$Effects$Cancelled);
			case 'Unknown':
				return $elm$json$Json$Decode$succeed($author$project$Effects$Unknown);
			default:
				return $elm$json$Json$Decode$fail('Not an authoritative terminal outcome');
		}
	},
	$elm$json$Json$Decode$string);
var $author$project$Effects$unknown = $elm$core$Maybe$map(
	function (transaction) {
		return _Utils_eq(transaction.status, $author$project$Effects$Pending) ? _Utils_update(
			transaction,
			{status: $author$project$Effects$Unknown}) : transaction;
	});
var $author$project$Effects$apply = F2(
	function (value, model) {
		var refuse = function (reason) {
			return _Utils_Tuple3(
				model,
				$elm$core$Maybe$Nothing,
				$elm$core$Maybe$Just(reason));
		};
		var decoded = F2(
			function (decoder, action) {
				var _v10 = A2($elm$json$Json$Decode$decodeValue, decoder, value);
				if (_v10.$ === 'Err') {
					var error = _v10.a;
					return refuse(
						$elm$json$Json$Decode$errorToString(error));
				} else {
					var result = _v10.a;
					return action(result);
				}
			});
		var _v0 = A2(
			$elm$json$Json$Decode$decodeValue,
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			value);
		if (_v0.$ === 'Err') {
			var error = _v0.a;
			return refuse(
				$elm$json$Json$Decode$errorToString(error));
		} else {
			switch (_v0.a) {
				case 'snapshot':
					return A2(
						decoded,
						A2(
							$author$project$Effects$strict,
							_List_fromArray(
								['kind', 'context', 'scene']),
							A3(
								$elm$json$Json$Decode$map2,
								$elm$core$Tuple$pair,
								A2($elm$json$Json$Decode$field, 'context', $author$project$Effects$contextDecoder),
								A2($elm$json$Json$Decode$field, 'scene', $elm$json$Json$Decode$value))),
						function (_v1) {
							var context = _v1.a;
							var sceneValue = _v1.b;
							var _v2 = $author$project$ActionProjection$decode(sceneValue);
							if (_v2.$ === 'Err') {
								var error = _v2.a;
								return refuse(error);
							} else {
								var scene = _v2.a;
								if (!_Utils_eq(
									$author$project$ActionProjection$revision(scene),
									context.revision)) {
									return refuse('Scene/context revision mismatch');
								} else {
									var _v3 = model.observed;
									if (_v3.$ === 'Just') {
										var old = _v3.a;
										return (A2($author$project$Effects$sameAuthority, old.context, context) && (_Utils_eq(
											A2($author$project$UInt64$compare, context.revision, old.context.revision),
											$elm$core$Basics$LT) || (_Utils_eq(context.revision, old.context.revision) && (!A2($author$project$ActionProjection$sameState, old.scene, scene))))) ? refuse('Nonincreasing snapshot') : _Utils_Tuple3(
											_Utils_update(
												model,
												{
													connected: true,
													observed: $elm$core$Maybe$Just(
														{context: context, scene: scene}),
													transaction: A2($author$project$Effects$sameAuthority, old.context, context) ? model.transaction : $author$project$Effects$unknown(model.transaction)
												}),
											$elm$core$Maybe$Nothing,
											$elm$core$Maybe$Nothing);
									} else {
										return _Utils_Tuple3(
											_Utils_update(
												model,
												{
													connected: true,
													observed: $elm$core$Maybe$Just(
														{context: context, scene: scene})
												}),
											$elm$core$Maybe$Nothing,
											$elm$core$Maybe$Nothing);
									}
								}
							}
						});
				case 'begin':
					return A2(
						decoded,
						A2(
							$author$project$Effects$strict,
							_List_fromArray(
								['kind', 'operation', 'incarnation']),
							A3(
								$elm$json$Json$Decode$map2,
								$elm$core$Tuple$pair,
								A2($elm$json$Json$Decode$field, 'operation', $author$project$Effects$operationDecoder),
								A2($elm$json$Json$Decode$field, 'incarnation', $author$project$Effects$identity))),
						function (_v4) {
							var operation = _v4.a;
							var incarnation = _v4.b;
							var _v5 = _Utils_Tuple3(
								model.observed,
								$author$project$UInt64$next(model.request),
								$author$project$UInt64$next(model.generation));
							if (((_v5.a.$ === 'Just') && (_v5.b.$ === 'Just')) && (_v5.c.$ === 'Just')) {
								var observed = _v5.a.a;
								var request = _v5.b.a;
								var generation = _v5.c.a;
								if (!model.connected) {
									return refuse('Disconnected');
								} else {
									if ($author$project$Effects$pending(model)) {
										return refuse('Operation already pending');
									} else {
										if (!A2($author$project$ActionProjection$actionable, incarnation, observed.scene)) {
											return refuse('Locked or unmapped target');
										} else {
											var _v6 = A2($author$project$ActionProjection$minimized, incarnation, observed.scene);
											if (_v6.$ === 'Nothing') {
												return refuse('Unknown incarnation');
											} else {
												var minimized = _v6.a;
												if ((_Utils_eq(operation, $author$project$Effects$Minimize) && minimized) || ((_Utils_eq(operation, $author$project$Effects$Restore) && (!minimized)) || (_Utils_eq(operation, $author$project$Effects$Activate) && minimized))) {
													return refuse('Already in requested native state');
												} else {
													var intent = {context: observed.context, generation: generation, incarnation: incarnation, operation: operation, request: request};
													return _Utils_Tuple3(
														_Utils_update(
															model,
															{
																generation: generation,
																request: request,
																transaction: $elm$core$Maybe$Just(
																	{intent: intent, status: $author$project$Effects$Pending})
															}),
														$elm$core$Maybe$Just(
															$elm$json$Json$Encode$object(
																_List_fromArray(
																	[
																		_Utils_Tuple2(
																		'kind',
																		$elm$json$Json$Encode$string('window-effect')),
																		_Utils_Tuple2(
																		'protocol',
																		$elm$json$Json$Encode$int(1)),
																		_Utils_Tuple2(
																		'intent',
																		$author$project$Effects$encodeIntent(intent))
																	]))),
														$elm$core$Maybe$Nothing);
												}
											}
										}
									}
								}
							} else {
								return refuse('Disconnected or exhausted identity');
							}
						});
				case 'receipt':
					return A2(
						decoded,
						A2(
							$author$project$Effects$strict,
							_List_fromArray(
								['kind', 'intent', 'status']),
							A3(
								$elm$json$Json$Decode$map2,
								$elm$core$Tuple$pair,
								A2($elm$json$Json$Decode$field, 'intent', $author$project$Effects$intentDecoder),
								A2($elm$json$Json$Decode$field, 'status', $author$project$Effects$statusDecoder))),
						function (_v7) {
							var intent = _v7.a;
							var status = _v7.b;
							var _v8 = _Utils_Tuple2(model.transaction, model.observed);
							if ((_v8.a.$ === 'Just') && (_v8.b.$ === 'Just')) {
								var transaction = _v8.a.a;
								var observed = _v8.b.a;
								return (model.connected && (_Utils_eq(transaction.status, $author$project$Effects$Pending) && (_Utils_eq(transaction.intent, intent) && A2($author$project$Effects$sameAuthority, observed.context, intent.context)))) ? _Utils_Tuple3(
									_Utils_update(
										model,
										{
											transaction: $elm$core$Maybe$Just(
												_Utils_update(
													transaction,
													{status: status}))
										}),
									$elm$core$Maybe$Nothing,
									$elm$core$Maybe$Nothing) : refuse('Stale, mismatched or terminal receipt');
							} else {
								return refuse('No connected pending operation');
							}
						});
				case 'disconnect':
					return A2(
						decoded,
						A2(
							$author$project$Effects$strict,
							_List_fromArray(
								['kind']),
							$elm$json$Json$Decode$succeed(_Utils_Tuple0)),
						function (_v9) {
							return _Utils_Tuple3(
								_Utils_update(
									model,
									{
										connected: false,
										transaction: $author$project$Effects$unknown(model.transaction)
									}),
								$elm$core$Maybe$Nothing,
								$elm$core$Maybe$Nothing);
						});
				default:
					return refuse('Unsupported message');
			}
		}
	});
var $elm$json$Json$Decode$at = F2(
	function (fields, decoder) {
		return A3($elm$core$List$foldr, $elm$json$Json$Decode$field, decoder, fields);
	});
var $author$project$Shell$disconnect = function (model) {
	var _v0 = A2(
		$author$project$Effects$apply,
		$elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'kind',
					$elm$json$Json$Encode$string('disconnect'))
				])),
		model.effects);
	var effects = _v0.a;
	return _Utils_update(
		model,
		{effects: effects, expected: $elm$core$Maybe$Nothing, notice: 'Connection lost. Reconnect to continue.', phase: $author$project$Shell$Detached, reconnecting: false});
};
var $author$project$Shell$Exhausted = {$: 'Exhausted'};
var $author$project$Shell$refresh = function (model) {
	var _v0 = _Utils_Tuple2(
		model.binding,
		$author$project$UInt64$next(model.request));
	if ((_v0.a.$ === 'Just') && (_v0.b.$ === 'Just')) {
		var binding = _v0.a.a;
		var request = _v0.b.a;
		return _Utils_eq(model.phase, $author$project$Shell$Detached) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
			_Utils_update(
				model,
				{
					expected: $elm$core$Maybe$Just(request),
					phase: $author$project$Shell$Reconciling,
					request: request
				}),
			_List_fromArray(
				[
					$author$project$Shell$Send(
					$elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'protocolVersion',
								$elm$json$Json$Encode$int(3)),
								_Utils_Tuple2(
								'kind',
								$elm$json$Json$Encode$string('projection-request')),
								_Utils_Tuple2(
								'binding',
								$author$project$Binding$encode(binding)),
								_Utils_Tuple2(
								'requestId',
								$elm$json$Json$Encode$string(
									$author$project$UInt64$string(request)))
							])))
				]));
	} else {
		return _Utils_Tuple2(
			_Utils_update(
				model,
				{expected: $elm$core$Maybe$Nothing, notice: 'Restart the shell to continue.', phase: $author$project$Shell$Exhausted}),
			_List_Nil);
	}
};
var $author$project$Binding$replaces = F2(
	function (_v0, _v1) {
		var life = _v0.a;
		var session = _v0.b;
		var frontend = _v0.c;
		var oldLife = _v1.a;
		var oldSession = _v1.b;
		var oldFrontend = _v1.c;
		return (!_Utils_eq(life, oldLife)) || ((!_Utils_eq(session, oldSession)) || _Utils_eq(
			A2($author$project$UInt64$compare, frontend, oldFrontend),
			$elm$core$Basics$GT));
	});
var $author$project$Shell$version = A2(
	$elm$json$Json$Decode$andThen,
	function (v) {
		return (v === 3) ? $elm$json$Json$Decode$succeed(_Utils_Tuple0) : $elm$json$Json$Decode$fail('Protocol version');
	},
	A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int));
var $author$project$Shell$update = F2(
	function (msg, model) {
		switch (msg.$) {
			case 'Refresh':
				return (_Utils_eq(model.phase, $author$project$Shell$Detached) || $author$project$Effects$pending(model.effects)) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$refresh(model);
			case 'Reconnect':
				return (_Utils_eq(model.phase, $author$project$Shell$Detached) && (!model.reconnecting)) ? _Utils_Tuple2(
					_Utils_update(
						model,
						{notice: 'Reconnecting…', reconnecting: true}),
					_List_fromArray(
						[$author$project$Shell$RestartBackend])) : _Utils_Tuple2(model, _List_Nil);
			case 'Ignore':
				return _Utils_Tuple2(model, _List_Nil);
			case 'Act':
				var stamp = msg.a;
				var operation = msg.b;
				var incarnation = msg.c;
				if (!_Utils_eq(
					$author$project$Shell$capture(model),
					$elm$core$Maybe$Just(stamp))) {
					return _Utils_Tuple2(
						_Utils_update(
							model,
							{notice: 'Window list changed. Choose again.'}),
						_List_Nil);
				} else {
					if (!$author$project$Shell$available(model)) {
						return _Utils_Tuple2(model, _List_Nil);
					} else {
						var _v1 = A2(
							$author$project$Effects$apply,
							$elm$json$Json$Encode$object(
								_List_fromArray(
									[
										_Utils_Tuple2(
										'kind',
										$elm$json$Json$Encode$string('begin')),
										_Utils_Tuple2(
										'operation',
										$elm$json$Json$Encode$string(
											$author$project$Effects$operationName(operation))),
										_Utils_Tuple2(
										'incarnation',
										$elm$json$Json$Encode$string(
											$author$project$UInt64$string(incarnation)))
									])),
							model.effects);
						var effects = _v1.a;
						var command = _v1.b;
						var error = _v1.c;
						var commands = function () {
							var _v2 = _Utils_Tuple2(command, model.binding);
							if ((_v2.a.$ === 'Just') && (_v2.b.$ === 'Just')) {
								var value = _v2.a.a;
								var binding = _v2.b.a;
								var _v3 = A2(
									$elm$json$Json$Decode$decodeValue,
									A2($elm$json$Json$Decode$field, 'intent', $elm$json$Json$Decode$value),
									value);
								if (_v3.$ === 'Ok') {
									var intent = _v3.a;
									return _List_fromArray(
										[
											$author$project$Shell$Send(
											$elm$json$Json$Encode$object(
												_List_fromArray(
													[
														_Utils_Tuple2(
														'protocolVersion',
														$elm$json$Json$Encode$int(3)),
														_Utils_Tuple2(
														'kind',
														$elm$json$Json$Encode$string('window-effect')),
														_Utils_Tuple2(
														'effectProtocol',
														$elm$json$Json$Encode$int(1)),
														_Utils_Tuple2(
														'binding',
														$author$project$Binding$encode(binding)),
														_Utils_Tuple2('intent', intent)
													])))
										]);
								} else {
									return _List_Nil;
								}
							} else {
								return _List_Nil;
							}
						}();
						return _Utils_Tuple2(
							_Utils_update(
								model,
								{
									effects: effects,
									notice: A2($elm$core$Maybe$withDefault, model.notice, error)
								}),
							commands);
					}
				}
			default:
				var raw = msg.a;
				var _v4 = A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
					raw);
				_v4$5:
				while (true) {
					if (_v4.$ === 'Ok') {
						switch (_v4.a) {
							case 'host-disconnected':
								return _Utils_Tuple2(
									$author$project$Shell$disconnect(model),
									_List_Nil);
							case 'host-refresh':
								return _Utils_eq(model.phase, $author$project$Shell$Detached) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$refresh(model);
							case 'attached':
								var _v5 = A2(
									$elm$json$Json$Decode$decodeValue,
									A3(
										$elm$json$Json$Decode$map2,
										F2(
											function (_v6, binding) {
												return binding;
											}),
										$author$project$Shell$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder)),
									raw);
								if (_v5.$ === 'Ok') {
									var binding = _v5.a;
									if ((!_Utils_eq(model.phase, $author$project$Shell$Detached)) || ((!model.reconnecting) || A2(
										$elm$core$Maybe$withDefault,
										false,
										A2(
											$elm$core$Maybe$map,
											A2(
												$elm$core$Basics$composeR,
												$author$project$Binding$replaces(binding),
												$elm$core$Basics$not),
											model.binding)))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var detached = $author$project$Shell$disconnect(model);
										return $author$project$Shell$refresh(
											_Utils_update(
												detached,
												{
													binding: $elm$core$Maybe$Just(binding),
													notice: 'Updating window information…',
													phase: $author$project$Shell$Reconciling,
													reconnecting: false
												}));
									}
								} else {
									return _Utils_Tuple2(
										$author$project$Shell$disconnect(model),
										_List_Nil);
								}
							case 'action-projection':
								var decoder = A2(
									$author$project$Shell$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'context', 'scene']),
									A6(
										$elm$json$Json$Decode$map5,
										F5(
											function (_v12, binding, request, life, epoch) {
												return _Utils_Tuple3(
													binding,
													request,
													_Utils_Tuple2(life, epoch));
											}),
										$author$project$Shell$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2(
											$elm$json$Json$Decode$at,
											_List_fromArray(
												['context', 'lifetime']),
											$author$project$UInt64$decoder),
										A2(
											$elm$json$Json$Decode$at,
											_List_fromArray(
												['context', 'epoch']),
											$author$project$UInt64$decoder)));
								var _v7 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (_v7.$ === 'Ok') {
									var _v8 = _v7.a;
									var binding = _v8.a;
									var request = _v8.b;
									var _v9 = _v8.c;
									var life = _v9.a;
									var epoch = _v9.b;
									if (_Utils_eq(model.phase, $author$project$Shell$Detached) || ((!_Utils_eq(
										model.binding,
										$elm$core$Maybe$Just(binding))) || ((!_Utils_eq(
										model.expected,
										$elm$core$Maybe$Just(request))) || (!A3($author$project$Binding$matchesContext, life, epoch, binding))))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var _v10 = A2(
											$elm$json$Json$Decode$decodeValue,
											A3(
												$elm$json$Json$Decode$map2,
												F2(
													function (context, scene) {
														return $elm$json$Json$Encode$object(
															_List_fromArray(
																[
																	_Utils_Tuple2(
																	'kind',
																	$elm$json$Json$Encode$string('snapshot')),
																	_Utils_Tuple2('context', context),
																	_Utils_Tuple2('scene', scene)
																]));
													}),
												A2($elm$json$Json$Decode$field, 'context', $elm$json$Json$Decode$value),
												A2($elm$json$Json$Decode$field, 'scene', $elm$json$Json$Decode$value)),
											raw);
										if (_v10.$ === 'Ok') {
											var snapshot = _v10.a;
											var _v11 = A2($author$project$Effects$apply, snapshot, model.effects);
											var effects = _v11.a;
											var error = _v11.c;
											return _Utils_Tuple2(
												_Utils_update(
													model,
													{
														effects: effects,
														expected: _Utils_eq(error, $elm$core$Maybe$Nothing) ? $elm$core$Maybe$Nothing : model.expected,
														notice: _Utils_eq(error, $elm$core$Maybe$Nothing) ? 'Connected' : 'Window information could not be verified.',
														phase: _Utils_eq(error, $elm$core$Maybe$Nothing) ? $author$project$Shell$Ready : $author$project$Shell$Reconciling
													}),
												_List_Nil);
										} else {
											return _Utils_Tuple2(model, _List_Nil);
										}
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'effect-outcome':
								var _v13 = A2(
									$elm$json$Json$Decode$decodeValue,
									A4(
										$elm$json$Json$Decode$map3,
										F3(
											function (_v14, binding, receipt) {
												return _Utils_Tuple2(binding, receipt);
											}),
										$author$project$Shell$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A3(
											$elm$json$Json$Decode$map2,
											F2(
												function (intent, outcome) {
													return $elm$json$Json$Encode$object(
														_List_fromArray(
															[
																_Utils_Tuple2(
																'kind',
																$elm$json$Json$Encode$string('receipt')),
																_Utils_Tuple2('intent', intent),
																_Utils_Tuple2('status', outcome)
															]));
												}),
											A2($elm$json$Json$Decode$field, 'intent', $elm$json$Json$Decode$value),
											A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$value))),
									raw);
								if (_v13.$ === 'Ok') {
									var _v15 = _v13.a;
									var binding = _v15.a;
									var receipt = _v15.b;
									if (_Utils_eq(model.phase, $author$project$Shell$Detached) || (!_Utils_eq(
										model.binding,
										$elm$core$Maybe$Just(binding)))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var _v16 = A2($author$project$Effects$apply, receipt, model.effects);
										var effects = _v16.a;
										var error = _v16.c;
										return (!_Utils_eq(error, $elm$core$Maybe$Nothing)) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$refresh(
											_Utils_update(
												model,
												{effects: effects}));
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							default:
								break _v4$5;
						}
					} else {
						break _v4$5;
					}
				}
				return _Utils_Tuple2(model, _List_Nil);
		}
	});
var $author$project$MenuBridge$guardedAct = F5(
	function (stamp, action, incarnation, shell, model) {
		var blocked = A3($author$project$MenuBridge$blockedFor, incarnation, shell, model);
		if (blocked) {
			return _Utils_Tuple3(
				shell,
				_List_Nil,
				$elm$core$Maybe$Just('A menu operation for this window family awaits reconciliation'));
		} else {
			var _v0 = A2(
				$author$project$Shell$update,
				A3($author$project$Shell$Act, stamp, action, incarnation),
				shell);
			var next = _v0.a;
			var effects = _v0.b;
			return _Utils_Tuple3(
				next,
				effects,
				$elm$core$List$isEmpty(effects) ? $elm$core$Maybe$Just('Native operation unavailable') : $elm$core$Maybe$Nothing);
		}
	});
var $elm$json$Json$Decode$decodeString = _Json_runOnString;
var $author$project$ReceiptRouter$effectVersion = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (value === 1) ? $elm$json$Json$Decode$succeed(_Utils_Tuple0) : $elm$json$Json$Decode$fail('Effect protocol');
	},
	A2($elm$json$Json$Decode$field, 'effectProtocol', $elm$json$Json$Decode$int));
var $author$project$ReceiptRouter$Key = F2(
	function (_native, intent) {
		return {intent: intent, _native: _native};
	});
var $author$project$ReceiptRouter$Intent = F5(
	function (request, generation, incarnation, operation, context) {
		return {context: context, generation: generation, incarnation: incarnation, operation: operation, request: request};
	});
var $author$project$ReceiptRouter$Context = F4(
	function (lifetime, epoch, output, revision) {
		return {epoch: epoch, lifetime: lifetime, output: output, revision: revision};
	});
var $author$project$ReceiptRouter$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return _Utils_eq(value, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero native identity') : $elm$json$Json$Decode$succeed(value);
	},
	$author$project$UInt64$decoder);
var $author$project$ReceiptRouter$strict = F2(
	function (fields, body) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? body : $elm$json$Json$Decode$fail('Receipt fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$ReceiptRouter$context = A2(
	$author$project$ReceiptRouter$strict,
	_List_fromArray(
		['lifetime', 'epoch', 'output', 'revision']),
	A5(
		$elm$json$Json$Decode$map4,
		$author$project$ReceiptRouter$Context,
		A2($elm$json$Json$Decode$field, 'lifetime', $author$project$ReceiptRouter$positive),
		A2($elm$json$Json$Decode$field, 'epoch', $author$project$ReceiptRouter$positive),
		A2($elm$json$Json$Decode$field, 'output', $author$project$ReceiptRouter$positive),
		A2($elm$json$Json$Decode$field, 'revision', $author$project$ReceiptRouter$positive)));
var $author$project$ReceiptRouter$Minimize = {$: 'Minimize'};
var $author$project$ReceiptRouter$Restore = {$: 'Restore'};
var $author$project$ReceiptRouter$operation = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		switch (value) {
			case 'minimize':
				return $elm$json$Json$Decode$succeed($author$project$ReceiptRouter$Minimize);
			case 'restore':
				return $elm$json$Json$Decode$succeed($author$project$ReceiptRouter$Restore);
			default:
				return $elm$json$Json$Decode$fail('Unsupported native menu operation');
		}
	},
	$elm$json$Json$Decode$string);
var $author$project$ReceiptRouter$intent = A2(
	$author$project$ReceiptRouter$strict,
	_List_fromArray(
		['request', 'generation', 'incarnation', 'operation', 'context']),
	A6(
		$elm$json$Json$Decode$map5,
		$author$project$ReceiptRouter$Intent,
		A2($elm$json$Json$Decode$field, 'request', $author$project$ReceiptRouter$positive),
		A2($elm$json$Json$Decode$field, 'generation', $author$project$ReceiptRouter$positive),
		A2($elm$json$Json$Decode$field, 'incarnation', $author$project$ReceiptRouter$positive),
		A2($elm$json$Json$Decode$field, 'operation', $author$project$ReceiptRouter$operation),
		A2($elm$json$Json$Decode$field, 'context', $author$project$ReceiptRouter$context)));
var $author$project$ReceiptRouter$key = A3(
	$elm$json$Json$Decode$map2,
	$author$project$ReceiptRouter$Key,
	A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
	A2($elm$json$Json$Decode$field, 'intent', $author$project$ReceiptRouter$intent));
var $author$project$ReceiptRouter$kind = function (expected) {
	return A2(
		$elm$json$Json$Decode$andThen,
		function (value) {
			return _Utils_eq(value, expected) ? $elm$json$Json$Decode$succeed(_Utils_Tuple0) : $elm$json$Json$Decode$fail('Native message kind');
		},
		A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string));
};
var $elm$json$Json$Decode$map8 = _Json_map8;
var $author$project$ReceiptRouter$version = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (value === 3) ? $elm$json$Json$Decode$succeed(_Utils_Tuple0) : $elm$json$Json$Decode$fail('Native protocol');
	},
	A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int));
var $author$project$ReceiptRouter$receipt = A2(
	$author$project$ReceiptRouter$strict,
	_List_fromArray(
		['protocolVersion', 'kind', 'effectProtocol', 'binding', 'intent', 'status', 'reason', 'revision', 'outputGeneration']),
	A9(
		$elm$json$Json$Decode$map8,
		F8(
			function (_v0, _v1, _v2, _native, status, reason, _v3, _v4) {
				return _Utils_Tuple2(
					_native,
					function () {
						switch (status) {
							case 'Committed':
								return $author$project$Menu$Committed;
							case 'Refused':
								return $author$project$Menu$Refusal(reason);
							default:
								return $author$project$Menu$Uncertain;
						}
					}());
			}),
		$author$project$ReceiptRouter$version,
		$author$project$ReceiptRouter$kind('effect-outcome'),
		$author$project$ReceiptRouter$effectVersion,
		$author$project$ReceiptRouter$key,
		A2(
			$elm$json$Json$Decode$andThen,
			function (value) {
				return A2(
					$elm$core$List$member,
					value,
					_List_fromArray(
						['Committed', 'Refused', 'Unknown'])) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Native outcome');
			},
			A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string)),
		A2(
			$elm$json$Json$Decode$andThen,
			function (value) {
				return ($elm$core$String$length(value) <= 256) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Native reason bound');
			},
			A2($elm$json$Json$Decode$field, 'reason', $elm$json$Json$Decode$string)),
		A2($elm$json$Json$Decode$field, 'revision', $author$project$ReceiptRouter$positive),
		A2($elm$json$Json$Decode$field, 'outputGeneration', $author$project$ReceiptRouter$positive)));
var $author$project$ReceiptRouter$safeError = function (error) {
	safeError:
	while (true) {
		switch (error.$) {
			case 'Failure':
				var reason = error.a;
				return A2($elm$core$String$left, 256, reason);
			case 'Field':
				var nested = error.b;
				var $temp$error = nested;
				error = $temp$error;
				continue safeError;
			case 'Index':
				var nested = error.b;
				var $temp$error = nested;
				error = $temp$error;
				continue safeError;
			default:
				var alternatives = error.a;
				return A2(
					$elm$core$Maybe$withDefault,
					'Invalid native frame',
					A2(
						$elm$core$Maybe$map,
						$author$project$ReceiptRouter$safeError,
						$elm$core$List$head(alternatives)));
		}
	}
};
var $author$project$ReceiptRouter$utf8Bytes = A2(
	$elm$core$String$foldl,
	F2(
		function (character, total) {
			var code = $elm$core$Char$toCode(character);
			return total + ((code <= 127) ? 1 : ((code <= 2047) ? 2 : ((code <= 65535) ? 3 : 4)));
		}),
	0);
var $author$project$ReceiptRouter$accept = F2(
	function (raw, model) {
		var entries = model.a;
		if (($elm$core$String$length(raw) > 16384) || ($author$project$ReceiptRouter$utf8Bytes(raw) > 16384)) {
			return _Utils_Tuple3(
				model,
				$elm$core$Maybe$Nothing,
				$elm$core$Maybe$Just('Native receipt byte bound'));
		} else {
			var _v0 = A2($elm$json$Json$Decode$decodeString, $author$project$ReceiptRouter$receipt, raw);
			if (_v0.$ === 'Err') {
				var error = _v0.a;
				return _Utils_Tuple3(
					model,
					$elm$core$Maybe$Nothing,
					$elm$core$Maybe$Just(
						$author$project$ReceiptRouter$safeError(error)));
			} else {
				var _v1 = _v0.a;
				var _native = _v1.a;
				var outcome = _v1.b;
				var _v2 = $elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (entry) {
							return _Utils_eq(entry.key, _native);
						},
						entries));
				if (_v2.$ === 'Nothing') {
					return _Utils_Tuple3(
						model,
						$elm$core$Maybe$Nothing,
						$elm$core$Maybe$Just('Unknown or mismatched native receipt'));
				} else {
					var entry = _v2.a;
					var next = _Utils_eq(outcome, $author$project$Menu$Uncertain) ? model : $author$project$ReceiptRouter$Model(
						A2(
							$elm$core$List$filter,
							function (item) {
								return !_Utils_eq(item.local, entry.local);
							},
							entries));
					return _Utils_Tuple3(
						next,
						$elm$core$Maybe$Just(
							A3($author$project$Menu$ReceiveFor, entry.local, entry.binding, outcome)),
						$elm$core$Maybe$Nothing);
				}
			}
		}
	});
var $author$project$MenuBridge$nativeFrame = F2(
	function (raw, model) {
		var state = model.a;
		var _v0 = A2(
			$elm$json$Json$Decode$decodeString,
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			raw);
		if (_v0.$ === 'Err') {
			return _Utils_Tuple2(
				model,
				$elm$core$Maybe$Just('Invalid native frame'));
		} else {
			switch (_v0.a) {
				case 'host-disconnected':
					return _Utils_Tuple2(
						$author$project$MenuBridge$connectionLost(model),
						$elm$core$Maybe$Nothing);
				case 'effect-outcome':
					var _v1 = A2($author$project$ReceiptRouter$accept, raw, state.router);
					var router = _v1.a;
					var receipt = _v1.b;
					var error = _v1.c;
					if (receipt.$ === 'Nothing') {
						return _Utils_Tuple2(model, error);
					} else {
						var message = receipt.a;
						var _v3 = A2($author$project$Menu$update, message, state.menu);
						var menu = _v3.a;
						return _Utils_Tuple2(
							$author$project$MenuBridge$Model(
								_Utils_update(
									state,
									{menu: menu, router: router})),
							error);
					}
				default:
					return _Utils_Tuple2(model, $elm$core$Maybe$Nothing);
			}
		}
	});
var $author$project$NativeOutcome$exact = F3(
	function (name, child, expected) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (value) {
				return _Utils_eq(value, expected) ? $elm$json$Json$Decode$succeed(_Utils_Tuple0) : $elm$json$Json$Decode$fail('Outcome protocol');
			},
			A2($elm$json$Json$Decode$field, name, child));
	});
var $author$project$NativeOutcome$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return _Utils_eq(value, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero outcome identity') : $elm$json$Json$Decode$succeed(value);
	},
	$author$project$UInt64$decoder);
var $author$project$NativeOutcome$strict = F2(
	function (fields, child) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? child : $elm$json$Json$Decode$fail('Outcome schema');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$NativeOutcome$context = A2(
	$author$project$NativeOutcome$strict,
	_List_fromArray(
		['lifetime', 'epoch', 'output', 'revision']),
	A5(
		$elm$json$Json$Decode$map4,
		F4(
			function (_v0, _v1, _v2, _v3) {
				return _Utils_Tuple0;
			}),
		A2($elm$json$Json$Decode$field, 'lifetime', $author$project$NativeOutcome$positive),
		A2($elm$json$Json$Decode$field, 'epoch', $author$project$NativeOutcome$positive),
		A2($elm$json$Json$Decode$field, 'output', $author$project$NativeOutcome$positive),
		A2($elm$json$Json$Decode$field, 'revision', $author$project$NativeOutcome$positive)));
var $author$project$NativeOutcome$intent = A2(
	$author$project$NativeOutcome$strict,
	_List_fromArray(
		['request', 'generation', 'incarnation', 'operation', 'context']),
	A6(
		$elm$json$Json$Decode$map5,
		F5(
			function (_v0, _v1, _v2, _v3, _v4) {
				return _Utils_Tuple0;
			}),
		A2($elm$json$Json$Decode$field, 'request', $author$project$NativeOutcome$positive),
		A2($elm$json$Json$Decode$field, 'generation', $author$project$NativeOutcome$positive),
		A2($elm$json$Json$Decode$field, 'incarnation', $author$project$NativeOutcome$positive),
		A2(
			$elm$json$Json$Decode$andThen,
			function (value) {
				return A2(
					$elm$core$List$member,
					value,
					_List_fromArray(
						['minimize', 'restore', 'activate'])) ? $elm$json$Json$Decode$succeed(_Utils_Tuple0) : $elm$json$Json$Decode$fail('Outcome operation');
			},
			A2($elm$json$Json$Decode$field, 'operation', $elm$json$Json$Decode$string)),
		A2($elm$json$Json$Decode$field, 'context', $author$project$NativeOutcome$context)));
var $author$project$NativeOutcome$decoder = A2(
	$author$project$NativeOutcome$strict,
	_List_fromArray(
		['protocolVersion', 'kind', 'effectProtocol', 'binding', 'intent', 'status', 'reason', 'revision', 'outputGeneration']),
	A9(
		$elm$json$Json$Decode$map8,
		F8(
			function (_v0, _v1, _v2, _v3, _v4, _v5, _v6, _v7) {
				return _Utils_Tuple0;
			}),
		A3($author$project$NativeOutcome$exact, 'protocolVersion', $elm$json$Json$Decode$int, 3),
		A3($author$project$NativeOutcome$exact, 'kind', $elm$json$Json$Decode$string, 'effect-outcome'),
		A3($author$project$NativeOutcome$exact, 'effectProtocol', $elm$json$Json$Decode$int, 1),
		A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
		A2($elm$json$Json$Decode$field, 'intent', $author$project$NativeOutcome$intent),
		A2(
			$elm$json$Json$Decode$andThen,
			function (value) {
				return A2(
					$elm$core$List$member,
					value,
					_List_fromArray(
						['Committed', 'Refused', 'Unknown'])) ? $elm$json$Json$Decode$succeed(_Utils_Tuple0) : $elm$json$Json$Decode$fail('Outcome status');
			},
			A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string)),
		A2(
			$elm$json$Json$Decode$andThen,
			function (value) {
				return ($elm$core$String$length(value) <= 256) ? $elm$json$Json$Decode$succeed(_Utils_Tuple0) : $elm$json$Json$Decode$fail('Outcome reason');
			},
			A2($elm$json$Json$Decode$field, 'reason', $elm$json$Json$Decode$string)),
		A3(
			$elm$json$Json$Decode$map2,
			F2(
				function (_v8, _v9) {
					return _Utils_Tuple0;
				}),
			A2($elm$json$Json$Decode$field, 'revision', $author$project$NativeOutcome$positive),
			A2($elm$json$Json$Decode$field, 'outputGeneration', $author$project$NativeOutcome$positive))));
var $author$project$NativeOutcome$valid = function (value) {
	var _v0 = A2($elm$json$Json$Decode$decodeValue, $author$project$NativeOutcome$decoder, value);
	if (_v0.$ === 'Ok') {
		return true;
	} else {
		return false;
	}
};
var $author$project$TaskbarShell$native = F2(
	function (message, model) {
		var menus = function () {
			if (message.$ === 'Incoming') {
				var raw = message.a;
				var _v4 = A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
					raw);
				_v4$2:
				while (true) {
					if (_v4.$ === 'Ok') {
						switch (_v4.a) {
							case 'effect-outcome':
								return $author$project$NativeOutcome$valid(raw) ? A2(
									$author$project$MenuBridge$nativeFrame,
									A2($elm$json$Json$Encode$encode, 0, raw),
									model.menus).a : model.menus;
							case 'host-disconnected':
								return $author$project$MenuBridge$connectionLost(model.menus);
							default:
								break _v4$2;
						}
					} else {
						break _v4$2;
					}
				}
				return model.menus;
			} else {
				return model.menus;
			}
		}();
		var _v0 = function () {
			switch (message.$) {
				case 'Act':
					var scope = message.a;
					var operation = message.b;
					var target = message.c;
					var _v2 = A5($author$project$MenuBridge$guardedAct, scope, operation, target, model.shell, menus);
					var next = _v2.a;
					var emitted = _v2.b;
					var error = _v2.c;
					return _Utils_Tuple2(
						_Utils_update(
							next,
							{
								notice: A2($elm$core$Maybe$withDefault, next.notice, error)
							}),
						emitted);
				case 'Incoming':
					var raw = message.a;
					return (_Utils_eq(
						A2(
							$elm$json$Json$Decode$decodeValue,
							A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
							raw),
						$elm$core$Result$Ok('effect-outcome')) && false) ? _Utils_Tuple2(model.shell, _List_Nil) : A2($author$project$Shell$update, message, model.shell);
				default:
					return A2($author$project$Shell$update, message, model.shell);
			}
		}();
		var shell = _v0.a;
		var effects = _v0.b;
		var picker = A2(
			$elm$core$Maybe$andThen,
			function (current) {
				return (_Utils_eq(
					$author$project$Shell$capture(shell),
					$elm$core$Maybe$Just(current.scope)) && $author$project$Shell$available(shell)) ? $elm$core$Maybe$Just(current) : $elm$core$Maybe$Nothing;
			},
			model.picker);
		var settledMenus = _Utils_eq(shell.phase, $author$project$Shell$Detached) ? $author$project$MenuBridge$connectionLost(menus) : menus;
		return _Utils_Tuple2(
			_Utils_update(
				model,
				{menus: settledMenus, picker: picker, shell: shell}),
			effects);
	});
var $author$project$TaskbarShell$apply = F3(
	function (scope, decision, model) {
		if (decision.$ === 'Apply') {
			var operation = decision.a;
			var root = decision.b;
			return A2(
				$author$project$TaskbarShell$native,
				A3($author$project$Shell$Act, scope, operation, root),
				_Utils_update(
					model,
					{picker: $elm$core$Maybe$Nothing}));
		} else {
			return _Utils_Tuple2(model, _List_Nil);
		}
	});
var $elm$core$List$append = F2(
	function (xs, ys) {
		if (!ys.b) {
			return xs;
		} else {
			return A3($elm$core$List$foldr, $elm$core$List$cons, ys, xs);
		}
	});
var $elm$core$List$concat = function (lists) {
	return A3($elm$core$List$foldr, $elm$core$List$append, _List_Nil, lists);
};
var $elm$core$List$concatMap = F2(
	function (f, list) {
		return $elm$core$List$concat(
			A2($elm$core$List$map, f, list));
	});
var $author$project$MenuBridge$answer = F4(
	function (bridge, shell, effects, error) {
		return {bridge: bridge, effects: effects, error: error, shell: shell};
	});
var $author$project$MenuBridge$operation = function (action) {
	switch (action.$) {
		case 'Minimize':
			return $elm$core$Maybe$Just($author$project$Effects$Minimize);
		case 'Restore':
			return $elm$core$Maybe$Just($author$project$Effects$Restore);
		default:
			return $elm$core$Maybe$Nothing;
	}
};
var $author$project$MenuBridge$providerMatches = F2(
	function (captured, shell) {
		return _Utils_eq(
			shell.binding,
			$elm$core$Maybe$Just(
				$author$project$Provider$nativeBinding(captured.snapshot))) && (_Utils_eq(
			$author$project$Shell$capture(shell),
			$elm$core$Maybe$Just(captured.stamp)) && (_Utils_eq(
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.context;
				},
				shell.effects.observed),
			$elm$core$Maybe$Just(
				$author$project$Provider$nativeContext(captured.snapshot))) && _Utils_eq(
			A2(
				$elm$core$Maybe$andThen,
				function (observed) {
					return A2(
						$author$project$ActionProjection$rootOf,
						$author$project$Provider$incarnation(captured.snapshot),
						observed.scene);
				},
				shell.effects.observed),
			$elm$core$Maybe$Just(
				$author$project$Provider$incarnation(captured.snapshot)))));
	});
var $author$project$MenuBridge$refuse = F4(
	function (local, binding, reason, _v0) {
		var state = _v0.a;
		var _v1 = A2(
			$author$project$Menu$update,
			A3(
				$author$project$Menu$ReceiveFor,
				local,
				binding,
				$author$project$Menu$Refusal(reason)),
			state.menu);
		var menu = _v1.a;
		return $author$project$MenuBridge$Model(
			_Utils_update(
				state,
				{menu: menu}));
	});
var $author$project$ReceiptRouter$command = A2(
	$author$project$ReceiptRouter$strict,
	_List_fromArray(
		['protocolVersion', 'kind', 'effectProtocol', 'binding', 'intent']),
	A5(
		$elm$json$Json$Decode$map4,
		F4(
			function (_v0, _v1, _v2, value) {
				return value;
			}),
		$author$project$ReceiptRouter$version,
		$author$project$ReceiptRouter$kind('window-effect'),
		$author$project$ReceiptRouter$effectVersion,
		$author$project$ReceiptRouter$key));
var $author$project$ReceiptRouter$register = F4(
	function (_v0, provider, value, model) {
		var local = _v0.a;
		var binding = _v0.b;
		var action = _v0.c;
		var entries = model.a;
		var _v1 = A2($elm$json$Json$Decode$decodeValue, $author$project$ReceiptRouter$command, value);
		if (_v1.$ === 'Err') {
			var error = _v1.a;
			return $elm$core$Result$Err(
				$author$project$ReceiptRouter$safeError(error));
		} else {
			var _native = _v1.a;
			var expectedOperation = function () {
				switch (action.$) {
					case 'Minimize':
						return $elm$core$Maybe$Just($author$project$ReceiptRouter$Minimize);
					case 'Restore':
						return $elm$core$Maybe$Just($author$project$ReceiptRouter$Restore);
					default:
						return $elm$core$Maybe$Nothing;
				}
			}();
			var eligible = A2(
				$elm$core$List$any,
				function (item) {
					return item.enabled && _Utils_eq(item.action, action);
				},
				$author$project$Provider$getItems(provider));
			return ((!_Utils_eq(
				binding,
				$author$project$Provider$getBinding(provider))) || ((!eligible) || ((!_Utils_eq(
				$elm$core$Maybe$Just(_native.intent.operation),
				expectedOperation)) || ((!_Utils_eq(
				_native._native,
				$author$project$Provider$nativeBinding(provider))) || ((!_Utils_eq(
				_native.intent.context,
				$author$project$Provider$nativeContext(provider))) || (!_Utils_eq(
				_native.intent.incarnation,
				$author$project$Provider$incarnation(provider)))))))) ? $elm$core$Result$Err('Native command does not match frozen menu action') : (A2(
				$elm$core$List$any,
				function (entry) {
					return _Utils_eq(entry.local, local) || (_Utils_eq(entry.key, _native) || (_Utils_eq(entry.key._native, _native._native) && _Utils_eq(entry.key.intent.request, _native.intent.request)));
				},
				entries) ? $elm$core$Result$Err('Native/local operation already registered') : ((_Utils_cmp(
				$elm$core$List$length(entries),
				$author$project$Menu$maxOutstanding) > -1) ? $elm$core$Result$Err('Receipt registry capacity') : $elm$core$Result$Ok(
				$author$project$ReceiptRouter$Model(
					A2(
						$elm$core$List$cons,
						{binding: binding, key: _native, local: local},
						entries)))));
		}
	});
var $author$project$MenuBridge$menuEvent = F3(
	function (message, shell, model) {
		var state = model.a;
		switch (message.$) {
			case 'ReceiveFor':
				return A4(
					$author$project$MenuBridge$answer,
					model,
					shell,
					_List_Nil,
					$elm$core$Maybe$Just('Native outcomes require an authenticated frame'));
			case 'Open':
				return A4(
					$author$project$MenuBridge$answer,
					model,
					shell,
					_List_Nil,
					$elm$core$Maybe$Just('Menu opening requires a validated provider'));
			default:
				var preblocked = function () {
					var _v8 = _Utils_Tuple2(message, state.provider);
					if ((_v8.a.$ === 'Activate') && (_v8.b.$ === 'Just')) {
						var _v9 = _v8.a;
						var captured = _v8.b.a;
						return A3(
							$author$project$MenuBridge$blockedFor,
							$author$project$Provider$incarnation(captured.snapshot),
							shell,
							model);
					} else {
						return false;
					}
				}();
				var _v1 = A2($author$project$Menu$update, message, state.menu);
				var menu = _v1.a;
				var effects = _v1.b;
				var updated = $author$project$MenuBridge$Model(
					_Utils_update(
						state,
						{menu: menu}));
				if (preblocked) {
					return A4(
						$author$project$MenuBridge$answer,
						model,
						shell,
						_List_Nil,
						$elm$core$Maybe$Just('A menu operation for this window family awaits reconciliation'));
				} else {
					if (effects.b) {
						if (!effects.b.b) {
							var dispatch = effects.a;
							var local = dispatch.a;
							var binding = dispatch.b;
							var action = dispatch.c;
							var rejected = function (reason) {
								return A4(
									$author$project$MenuBridge$answer,
									A4($author$project$MenuBridge$refuse, local, binding, reason, updated),
									shell,
									_List_Nil,
									$elm$core$Maybe$Just(reason));
							};
							var _v3 = _Utils_Tuple2(
								state.provider,
								$author$project$MenuBridge$operation(action));
							if ((_v3.a.$ === 'Just') && (_v3.b.$ === 'Just')) {
								var captured = _v3.a.a;
								var nativeOperation = _v3.b.a;
								if ((!_Utils_eq(
									$author$project$Provider$getBinding(captured.snapshot),
									binding)) || (!A2($author$project$MenuBridge$providerMatches, captured, shell))) {
									return rejected('Native window information changed; choose again');
								} else {
									var _v4 = A2(
										$author$project$Shell$update,
										A3(
											$author$project$Shell$Act,
											captured.stamp,
											nativeOperation,
											$author$project$Provider$incarnation(captured.snapshot)),
										shell);
									var prepared = _v4.a;
									var commands = _v4.b;
									if ((commands.b && (commands.a.$ === 'Send')) && (!commands.b.b)) {
										var command = commands.a.a;
										var _v6 = A4($author$project$ReceiptRouter$register, dispatch, captured.snapshot, command, state.router);
										if (_v6.$ === 'Err') {
											return rejected('Native menu command could not be registered');
										} else {
											var router = _v6.a;
											var closed = function () {
												var _v7 = $author$project$Menu$snapshot(menu).menu;
												if (_v7.$ === 'Nothing') {
													return menu;
												} else {
													var view = _v7.a;
													return A2(
														$author$project$Menu$update,
														$author$project$Menu$Dismiss(view.id),
														menu).a;
												}
											}();
											return A4(
												$author$project$MenuBridge$answer,
												$author$project$MenuBridge$Model(
													_Utils_update(
														state,
														{menu: closed, router: router})),
												prepared,
												commands,
												$elm$core$Maybe$Nothing);
										}
									} else {
										return rejected('Native operation unavailable');
									}
								}
							} else {
								return rejected('Menu operation unavailable');
							}
						} else {
							return A4(
								$author$project$MenuBridge$answer,
								model,
								shell,
								_List_Nil,
								$elm$core$Maybe$Just('Invalid menu dispatch count'));
						}
					} else {
						return A4($author$project$MenuBridge$answer, updated, shell, _List_Nil, $elm$core$Maybe$Nothing);
					}
				}
		}
	});
var $author$project$TaskbarShell$dismissMenus = function (model) {
	var _v0 = $author$project$MenuBridge$menuSnapshot(model.menus).menu;
	if (_v0.$ === 'Nothing') {
		return model;
	} else {
		var view = _v0.a;
		var result = A3(
			$author$project$MenuBridge$menuEvent,
			$author$project$Menu$Dismiss(view.id),
			model.shell,
			model.menus);
		return _Utils_update(
			model,
			{menus: result.bridge});
	}
};
var $author$project$Taskbar$groups = function (projection) {
	var rows = $author$project$ActionProjection$windows(projection);
	var add = F2(
		function (_v0, accumulated) {
			var key = _v0.a;
			var entry = _v0.b;
			return A2(
				$elm$core$List$any,
				function (g) {
					return _Utils_eq(g.key, key);
				},
				accumulated) ? A2(
				$elm$core$List$map,
				function (g) {
					return _Utils_eq(g.key, key) ? _Utils_update(
						g,
						{
							families: _Utils_ap(
								g.families,
								_List_fromArray(
									[entry]))
						}) : g;
				},
				accumulated) : _Utils_ap(
				accumulated,
				_List_fromArray(
					[
						{
						families: _List_fromArray(
							[entry]),
						key: key
					}
					]));
		});
	var activeRoot = A2(
		$elm$core$Maybe$andThen,
		function (id) {
			return A2($author$project$ActionProjection$rootOf, id, projection);
		},
		$author$project$ActionProjection$focused(projection));
	var family = function (root) {
		var members = A2(
			$elm$core$List$filter,
			function (w) {
				return _Utils_eq(
					A2($author$project$ActionProjection$rootOf, w.incarnation, projection),
					$elm$core$Maybe$Just(root.incarnation));
			},
			rows);
		var key = $elm$core$String$isEmpty(root.application) ? ('window:' + $author$project$UInt64$string(root.incarnation)) : ('application:' + root.application);
		return _Utils_Tuple2(
			key,
			{
				active: _Utils_eq(
					activeRoot,
					$elm$core$Maybe$Just(root.incarnation)),
				application: root.application,
				available: A2(
					$elm$core$List$all,
					function ($) {
						return $.available;
					},
					members),
				label: root.label,
				minimized: root.minimized,
				root: root.incarnation
			});
	};
	return A3(
		$elm$core$List$foldl,
		add,
		_List_Nil,
		A2(
			$elm$core$List$map,
			family,
			A2(
				$elm$core$List$sortWith,
				F2(
					function (a, b) {
						return A2($author$project$UInt64$compare, a.incarnation, b.incarnation);
					}),
				A2(
					$elm$core$List$filter,
					function (w) {
						return _Utils_eq(w.owner, $elm$core$Maybe$Nothing);
					},
					rows))));
};
var $author$project$TaskbarShell$groups = function (model) {
	return A2(
		$elm$core$Maybe$withDefault,
		_List_Nil,
		A2(
			$elm$core$Maybe$map,
			A2(
				$elm$core$Basics$composeR,
				function ($) {
					return $.scene;
				},
				$author$project$Taskbar$groups),
			model.shell.effects.observed));
};
var $author$project$MenuBridge$providerStamp = function (provider) {
	var context = $author$project$Provider$nativeContext(provider);
	return A2(
		$elm$core$Result$mapError,
		function (_v0) {
			return 'Invalid native menu stamp';
		},
		A2(
			$elm$json$Json$Decode$decodeValue,
			$author$project$Shell$stampDecoder,
			$elm$json$Json$Encode$object(
				_List_fromArray(
					[
						_Utils_Tuple2(
						'binding',
						$author$project$Binding$encode(
							$author$project$Provider$nativeBinding(provider))),
						_Utils_Tuple2(
						'output',
						$elm$json$Json$Encode$string(
							$author$project$UInt64$string(context.output))),
						_Utils_Tuple2(
						'revision',
						$elm$json$Json$Encode$string(
							$author$project$UInt64$string(context.revision)))
					]))));
};
var $author$project$Menu$Open = F2(
	function (a, b) {
		return {$: 'Open', a: a, b: b};
	});
var $author$project$Provider$toOpen = function (_v0) {
	var value = _v0.a;
	return A2($author$project$Menu$Open, value.binding, value.items);
};
var $author$project$MenuBridge$open = F2(
	function (provider, model) {
		var state = model.a;
		var _v0 = $author$project$MenuBridge$providerStamp(provider);
		if (_v0.$ === 'Err') {
			return model;
		} else {
			var stamp = _v0.a;
			var before = $author$project$Menu$snapshot(state.menu);
			var _v1 = A2(
				$author$project$Menu$update,
				$author$project$Provider$toOpen(provider),
				state.menu);
			var menu = _v1.a;
			return _Utils_eq(
				$author$project$Menu$snapshot(menu).menu,
				before.menu) ? model : $author$project$MenuBridge$Model(
				_Utils_update(
					state,
					{
						menu: menu,
						provider: $elm$core$Maybe$Just(
							{snapshot: provider, stamp: stamp})
					}));
		}
	});
var $author$project$Taskbar$Apply = F2(
	function (a, b) {
		return {$: 'Apply', a: a, b: b};
	});
var $author$project$Taskbar$Launch = {$: 'Launch'};
var $author$project$Taskbar$Picker = {$: 'Picker'};
var $author$project$Taskbar$Unavailable = {$: 'Unavailable'};
var $author$project$Taskbar$primary = F2(
	function (pinned, families) {
		if (!families.b) {
			return pinned ? $author$project$Taskbar$Launch : $author$project$Taskbar$Unavailable;
		} else {
			if (!families.b.b) {
				var entry = families.a;
				return (!entry.available) ? $author$project$Taskbar$Unavailable : (entry.minimized ? A2($author$project$Taskbar$Apply, $author$project$Effects$Restore, entry.root) : (entry.active ? A2($author$project$Taskbar$Apply, $author$project$Effects$Minimize, entry.root) : A2($author$project$Taskbar$Apply, $author$project$Effects$Activate, entry.root)));
			} else {
				return $author$project$Taskbar$Picker;
			}
		}
	});
var $author$project$Taskbar$selection = function (entry) {
	return (!entry.available) ? $author$project$Taskbar$Unavailable : A2(
		$author$project$Taskbar$Apply,
		entry.minimized ? $author$project$Effects$Restore : $author$project$Effects$Activate,
		entry.root);
};
var $author$project$TaskbarShell$valid = F2(
	function (scope, model) {
		return _Utils_eq(
			$author$project$Shell$capture(model.shell),
			$elm$core$Maybe$Just(scope)) && $author$project$Shell$available(model.shell);
	});
var $author$project$TaskbarShell$update = F2(
	function (message, model) {
		switch (message.$) {
			case 'OpenMenu':
				var provider = message.a;
				var menus = A2($author$project$MenuBridge$open, provider, model.menus);
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							menus: menus,
							picker: _Utils_eq(menus, model.menus) ? model.picker : $elm$core$Maybe$Nothing
						}),
					_List_Nil);
			case 'MenuEvent':
				var event = message.a;
				var result = A3($author$project$MenuBridge$menuEvent, event, model.shell, model.menus);
				var shell = result.shell;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							menus: result.bridge,
							picker: $elm$core$List$isEmpty(result.effects) ? model.picker : $elm$core$Maybe$Nothing,
							shell: _Utils_update(
								shell,
								{
									notice: A2($elm$core$Maybe$withDefault, shell.notice, result.error)
								})
						}),
					result.effects);
			case 'Native':
				var value = message.a;
				return A2($author$project$TaskbarShell$native, value, model);
			case 'Primary':
				var scope = message.a;
				var key = message.b;
				if (!A2($author$project$TaskbarShell$valid, scope, model)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v1 = $elm$core$List$head(
						A2(
							$elm$core$List$filter,
							function (group) {
								return _Utils_eq(group.key, key);
							},
							$author$project$TaskbarShell$groups(model)));
					if (_v1.$ === 'Nothing') {
						return _Utils_Tuple2(model, _List_Nil);
					} else {
						var group = _v1.a;
						var base = $author$project$TaskbarShell$dismissMenus(model);
						var _v2 = A2($author$project$Taskbar$primary, false, group.families);
						if (_v2.$ === 'Picker') {
							var _v3 = $author$project$UInt64$next(model.generation);
							if (_v3.$ === 'Just') {
								var generation = _v3.a;
								return _Utils_Tuple2(
									_Utils_update(
										base,
										{
											generation: generation,
											picker: $elm$core$Maybe$Just(
												{generation: generation, key: key, scope: scope})
										}),
									_List_Nil);
							} else {
								return _Utils_Tuple2(
									_Utils_update(
										base,
										{picker: $elm$core$Maybe$Nothing}),
									_List_Nil);
							}
						} else {
							var decision = _v2;
							return A3($author$project$TaskbarShell$apply, scope, decision, base);
						}
					}
				}
			case 'Choose':
				var scope = message.a;
				var generation = message.b;
				var root = message.c;
				var _v4 = model.picker;
				if (_v4.$ === 'Just') {
					var picker = _v4.a;
					return ((!A2($author$project$TaskbarShell$valid, scope, model)) || ((!_Utils_eq(picker.scope, scope)) || (!_Utils_eq(picker.generation, generation)))) ? _Utils_Tuple2(model, _List_Nil) : A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(model, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (family) {
								return A3(
									$author$project$TaskbarShell$apply,
									scope,
									$author$project$Taskbar$selection(family),
									model);
							},
							$elm$core$List$head(
								A2(
									$elm$core$List$filter,
									function (family) {
										return _Utils_eq(family.root, root);
									},
									A2(
										$elm$core$List$concatMap,
										function ($) {
											return $.families;
										},
										A2(
											$elm$core$List$filter,
											function (group) {
												return _Utils_eq(group.key, picker.key);
											},
											$author$project$TaskbarShell$groups(model)))))));
				} else {
					return _Utils_Tuple2(model, _List_Nil);
				}
			default:
				var scope = message.a;
				var generation = message.b;
				var _v5 = model.picker;
				if (_v5.$ === 'Just') {
					var picker = _v5.a;
					return (_Utils_eq(picker.scope, scope) && _Utils_eq(picker.generation, generation)) ? _Utils_Tuple2(
						_Utils_update(
							model,
							{picker: $elm$core$Maybe$Nothing}),
						_List_Nil) : _Utils_Tuple2(model, _List_Nil);
				} else {
					return _Utils_Tuple2(model, _List_Nil);
				}
		}
	});
var $author$project$BridgeReplay$transition = F2(
	function (message, state) {
		var _v0 = A2($author$project$TaskbarShell$update, message, state.model);
		var model = _v0.a;
		var effects = _v0.b;
		var sent = _Utils_ap(
			state.sent,
			A2(
				$elm$core$List$filterMap,
				function (effect) {
					if (effect.$ === 'Send') {
						var value = effect.a;
						return $elm$core$Maybe$Just(value);
					} else {
						return $elm$core$Maybe$Nothing;
					}
				},
				effects));
		var snapshot = $author$project$MenuBridge$menuSnapshot(model.menus);
		var ids = function () {
			var _v3 = snapshot.menu;
			if (_v3.$ === 'Nothing') {
				return state.ids;
			} else {
				var current = _v3.a;
				return A2($elm$core$List$member, current.id, state.ids) ? state.ids : _Utils_ap(
					state.ids,
					_List_fromArray(
						[current.id]));
			}
		}();
		var intents = function () {
			var _v1 = snapshot.lastOutcome;
			if (_v1.$ === 'Nothing') {
				return state.intents;
			} else {
				var _v2 = _v1.a;
				var intent = _v2.a;
				return A2($elm$core$List$member, intent, state.intents) ? state.intents : _Utils_ap(
					state.intents,
					_List_fromArray(
						[intent]));
			}
		}();
		return _Utils_update(
			state,
			{ids: ids, intents: intents, model: model, sent: sent});
	});
var $author$project$BridgeReplay$step = F2(
	function (value, state) {
		var production = A2(
			$elm$core$Result$andThen,
			function (_v15) {
				var scope = _v15.a;
				var incarnation = _v15.b;
				return A3($author$project$NativeProvider$fromShell, scope, incarnation, state.model.shell);
			},
			A2(
				$elm$core$Result$mapError,
				function (_v14) {
					return 'Invalid producer fixture';
				},
				A2(
					$elm$json$Json$Decode$decodeValue,
					A3(
						$elm$json$Json$Decode$map2,
						$elm$core$Tuple$pair,
						A2($elm$json$Json$Decode$field, 'scope', $author$project$BridgeReplay$scopeDecoder),
						A2($elm$json$Json$Decode$field, 'incarnation', $author$project$UInt64$decoder)),
					value)));
		var op = A2(
			$elm$json$Json$Decode$decodeValue,
			A2($elm$json$Json$Decode$field, 'op', $elm$json$Json$Decode$string),
			value);
		var expected = $elm$core$Result$toMaybe(
			A2(
				$elm$core$Result$andThen,
				$author$project$Provider$decode,
				A2(
					$elm$core$Result$mapError,
					function (_v13) {
						return 'No expected provider';
					},
					A2(
						$elm$json$Json$Decode$decodeValue,
						A2($elm$json$Json$Decode$field, 'expectedProvider', $elm$json$Json$Decode$value),
						value))));
		var finish = F3(
			function (next, error, producer) {
				return _Utils_update(
					next,
					{
						results: _Utils_ap(
							state.results,
							_List_fromArray(
								[
									A4($author$project$BridgeReplay$encode, next, error, producer, expected)
								]))
					});
			});
		var refuse = function (error) {
			return A3(
				finish,
				state,
				$elm$core$Maybe$Just(error),
				$elm$core$Maybe$Nothing);
		};
		var dispatch = function (event) {
			return A3(
				finish,
				A2($author$project$BridgeReplay$transition, event, state),
				$elm$core$Maybe$Nothing,
				$elm$core$Maybe$Nothing);
		};
		var current = $author$project$MenuBridge$menuSnapshot(state.model.menus).menu;
		_v0$12:
		while (true) {
			if (op.$ === 'Ok') {
				switch (op.a) {
					case 'frame':
						var _v1 = A2(
							$elm$json$Json$Decode$decodeValue,
							A2($elm$json$Json$Decode$field, 'frame', $elm$json$Json$Decode$value),
							value);
						if (_v1.$ === 'Ok') {
							var frame = _v1.a;
							return dispatch(
								$author$project$TaskbarShell$Native(
									$author$project$Shell$Incoming(frame)));
						} else {
							return refuse('Missing frame');
						}
					case 'reconnect':
						return dispatch(
							$author$project$TaskbarShell$Native($author$project$Shell$Reconnect));
					case 'refresh':
						return dispatch(
							$author$project$TaskbarShell$Native($author$project$Shell$Refresh));
					case 'open':
						var _v2 = A2(
							$elm$core$Result$andThen,
							$author$project$Provider$decode,
							A2(
								$elm$core$Result$mapError,
								function (_v3) {
									return 'Missing provider';
								},
								A2(
									$elm$json$Json$Decode$decodeValue,
									A2($elm$json$Json$Decode$field, 'provider', $elm$json$Json$Decode$value),
									value)));
						if (_v2.$ === 'Ok') {
							var provider = _v2.a;
							return dispatch(
								$author$project$TaskbarShell$OpenMenu(provider));
						} else {
							var error = _v2.a;
							return refuse(error);
						}
					case 'produce':
						if (production.$ === 'Ok') {
							var provider = production.a;
							return A3(
								finish,
								state,
								$elm$core$Maybe$Nothing,
								$elm$core$Maybe$Just(provider));
						} else {
							var error = production.a;
							return refuse(error);
						}
					case 'produceOpen':
						if (production.$ === 'Ok') {
							var provider = production.a;
							return A3(
								finish,
								A2(
									$author$project$BridgeReplay$transition,
									$author$project$TaskbarShell$OpenMenu(provider),
									state),
								$elm$core$Maybe$Nothing,
								$elm$core$Maybe$Just(provider));
						} else {
							var error = production.a;
							return refuse(error);
						}
					case 'activate':
						var _v6 = _Utils_Tuple2(
							current,
							A2(
								$elm$json$Json$Decode$decodeValue,
								A2($elm$json$Json$Decode$field, 'index', $elm$json$Json$Decode$int),
								value));
						if ((_v6.a.$ === 'Just') && (_v6.b.$ === 'Ok')) {
							var menu = _v6.a.a;
							var index = _v6.b.a;
							return dispatch(
								$author$project$TaskbarShell$MenuEvent(
									A3($author$project$Menu$Activate, menu.id, menu.binding, index)));
						} else {
							return refuse('No activation menu');
						}
					case 'staleDismiss':
						var _v7 = A2(
							$elm$core$Maybe$andThen,
							function (index) {
								return $elm$core$List$head(
									A2($elm$core$List$drop, index, state.ids));
							},
							$elm$core$Result$toMaybe(
								A2(
									$elm$json$Json$Decode$decodeValue,
									A2($elm$json$Json$Decode$field, 'menu', $elm$json$Json$Decode$int),
									value)));
						if (_v7.$ === 'Just') {
							var id = _v7.a;
							return dispatch(
								$author$project$TaskbarShell$MenuEvent(
									$author$project$Menu$Dismiss(id)));
						} else {
							return refuse('Missing historical menu');
						}
					case 'forgedReceipt':
						var _v8 = _Utils_Tuple2(
							$elm$core$List$head(state.intents),
							$author$project$MenuBridge$currentProvider(state.model.menus));
						if ((_v8.a.$ === 'Just') && (_v8.b.$ === 'Just')) {
							var intent = _v8.a.a;
							var provider = _v8.b.a;
							return dispatch(
								$author$project$TaskbarShell$MenuEvent(
									A3(
										$author$project$Menu$ReceiveFor,
										intent,
										$author$project$Provider$getBinding(provider),
										$author$project$Menu$Committed)));
						} else {
							return refuse('Missing forged-receipt fixture context');
						}
					case 'dismiss':
						if (current.$ === 'Just') {
							var menu = current.a;
							return dispatch(
								$author$project$TaskbarShell$MenuEvent(
									$author$project$Menu$Dismiss(menu.id)));
						} else {
							return A3(finish, state, $elm$core$Maybe$Nothing, $elm$core$Maybe$Nothing);
						}
					case 'taskbar':
						var _v10 = _Utils_Tuple2(
							A2($author$project$BridgeReplay$stampFor, value, state.model.shell),
							A2(
								$elm$json$Json$Decode$decodeValue,
								A3(
									$elm$json$Json$Decode$map2,
									$elm$core$Tuple$pair,
									A2($elm$json$Json$Decode$field, 'operation', $author$project$Effects$operationDecoder),
									A2($elm$json$Json$Decode$field, 'incarnation', $author$project$UInt64$decoder)),
								value));
						if ((_v10.a.$ === 'Just') && (_v10.b.$ === 'Ok')) {
							var stamp = _v10.a.a;
							var _v11 = _v10.b.a;
							var operation = _v11.a;
							var incarnation = _v11.b;
							return dispatch(
								$author$project$TaskbarShell$Native(
									A3($author$project$Shell$Act, stamp, operation, incarnation)));
						} else {
							return refuse('No taskbar scope');
						}
					case 'primary':
						var _v12 = _Utils_Tuple2(
							A2($author$project$BridgeReplay$stampFor, value, state.model.shell),
							A2(
								$elm$json$Json$Decode$decodeValue,
								A2($elm$json$Json$Decode$field, 'key', $elm$json$Json$Decode$string),
								value));
						if ((_v12.a.$ === 'Just') && (_v12.b.$ === 'Ok')) {
							var stamp = _v12.a.a;
							var key = _v12.b.a;
							return dispatch(
								A2($author$project$TaskbarShell$Primary, stamp, key));
						} else {
							return refuse('No taskbar primary scope');
						}
					default:
						break _v0$12;
				}
			} else {
				break _v0$12;
			}
		}
		return refuse('Unknown bridge fixture operation');
	});
var $author$project$BridgeReplay$run = function (value) {
	var _v0 = A2(
		$elm$json$Json$Decode$decodeValue,
		A2(
			$elm$json$Json$Decode$field,
			'steps',
			$elm$json$Json$Decode$list($elm$json$Json$Decode$value)),
		value);
	if (_v0.$ === 'Err') {
		return $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'passed',
					$elm$json$Json$Encode$bool(false)),
					_Utils_Tuple2(
					'error',
					$elm$json$Json$Encode$string('Missing steps'))
				]));
	} else {
		var steps = _v0.a;
		var state = A3($elm$core$List$foldl, $author$project$BridgeReplay$step, $author$project$BridgeReplay$initial, steps);
		return $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'passed',
					$elm$json$Json$Encode$bool(true)),
					_Utils_Tuple2(
					'steps',
					A2($elm$json$Json$Encode$list, $elm$core$Basics$identity, state.results))
				]));
	}
};
var $elm$core$Platform$worker = _Platform_worker;
var $author$project$BridgeReplay$main = $elm$core$Platform$worker(
	{
		init: function (_v0) {
			return _Utils_Tuple2(_Utils_Tuple0, $elm$core$Platform$Cmd$none);
		},
		subscriptions: function (_v1) {
			return $author$project$BridgeReplay$incoming($author$project$BridgeReplay$Run);
		},
		update: F2(
			function (_v2, _v3) {
				var value = _v2.a;
				return _Utils_Tuple2(
					_Utils_Tuple0,
					$author$project$BridgeReplay$outgoing(
						$author$project$BridgeReplay$run(value)));
			})
	});
_Platform_export({'BridgeReplay':{'init':$author$project$BridgeReplay$main(
	$elm$json$Json$Decode$succeed(_Utils_Tuple0))(0)}});}(this));