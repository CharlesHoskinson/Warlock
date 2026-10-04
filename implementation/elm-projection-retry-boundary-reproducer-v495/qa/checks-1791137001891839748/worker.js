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
var $elm$core$Basics$EQ = {$: 'EQ'};
var $elm$core$Basics$GT = {$: 'GT'};
var $elm$core$Basics$LT = {$: 'LT'};
var $elm$core$Basics$False = {$: 'False'};
var $author$project$Shell$Incoming = function (a) {
	return {$: 'Incoming', a: a};
};
var $elm$core$Maybe$Just = function (a) {
	return {$: 'Just', a: a};
};
var $author$project$Shell$Reconciling = {$: 'Reconciling'};
var $elm$core$Basics$identity = function (x) {
	return x;
};
var $author$project$TerminalProbe$Run = function (a) {
	return {$: 'Run', a: a};
};
var $elm$core$Basics$add = _Basics_add;
var $elm$core$Basics$apR = F2(
	function (x, f) {
		return f(x);
	});
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
var $elm$json$Json$Decode$field = _Json_decodeField;
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
var $elm$json$Json$Decode$at = F2(
	function (fields, decoder) {
		return A3($elm$core$List$foldr, $elm$json$Json$Decode$field, decoder, fields);
	});
var $elm$json$Json$Decode$bool = _Json_decodeBool;
var $elm$json$Json$Encode$bool = _Json_wrap;
var $elm$core$Basics$composeR = F3(
	function (f, g, x) {
		return g(
			f(x));
	});
var $elm$json$Json$Decode$decodeValue = _Json_run;
var $author$project$Binding$Binding = F3(
	function (a, b, c) {
		return {$: 'Binding', a: a, b: b, c: c};
	});
var $elm$json$Json$Decode$andThen = _Json_andThen;
var $elm$json$Json$Decode$fail = _Json_fail;
var $elm$json$Json$Decode$keyValuePairs = _Json_decodeKeyValuePairs;
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
var $author$project$UInt64$Counter = function (a) {
	return {$: 'Counter', a: a};
};
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
var $author$project$UInt64$zero = $author$project$UInt64$Counter('0');
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
var $elm$json$Json$Decode$value = _Json_decodeValue;
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
var $author$project$Shell$Ready = {$: 'Ready'};
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
	return (!model.transportRefused) && (_Utils_eq(model.phase, $author$project$Shell$Ready) && ((!model.attachNeeded) && ((!$author$project$Effects$pending(model.effects)) && (_Utils_eq(model.geometryAttachExpected, $elm$core$Maybe$Nothing) && ((!A2(
		$elm$core$Maybe$withDefault,
		false,
		A2(
			$elm$core$Maybe$map,
			function ($) {
				return $.effects;
			},
			model.geometryCaps))) || (_Utils_eq(model.geometryExpected, $elm$core$Maybe$Nothing) && (!_Utils_eq(model.geometry, $elm$core$Maybe$Nothing))))))));
};
var $elm$json$Json$Encode$string = _Json_wrap;
var $author$project$UInt64$string = function (_v0) {
	var value = _v0.a;
	return value;
};
var $author$project$Effects$counter = A2($elm$core$Basics$composeR, $author$project$UInt64$string, $elm$json$Json$Encode$string);
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
		case 'Activate':
			return 'activate';
		case 'Maximize':
			return 'maximize';
		default:
			return 'restore-geometry';
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
var $elm$json$Json$Encode$list = F2(
	function (func, entries) {
		return _Json_wrap(
			A3(
				$elm$core$List$foldl,
				_Json_addEntry(func),
				_Json_emptyArray(_Utils_Tuple0),
				entries));
	});
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
var $author$project$Shell$recoveryNotice = function (failure) {
	switch (failure.$) {
		case 'Unavailable':
			return 'Window recovery data is unavailable. Restore access, then reconnect.';
		case 'Full':
			return 'Window recovery storage is full. Free space, then reconnect.';
		case 'Busy':
			return 'Another shell is using window recovery data. Close it, then reconnect.';
		case 'Unverified':
			return 'Window recovery data could not be verified. Repair it, then reconnect.';
		default:
			return 'Previous window recovery data has no verified owner. Complete migration, then reconnect.';
	}
};
var $author$project$Shell$status = function (model) {
	if (model.transportRefused) {
		return 'Window transport is full or unavailable. Waiting for a verified output or capacity update.';
	} else {
		var _v0 = A2(
			$elm$core$Maybe$map,
			function ($) {
				return $.status;
			},
			model.effects.transaction);
		_v0$3:
		while (true) {
			if (_v0.$ === 'Just') {
				switch (_v0.a.$) {
					case 'Pending':
						var _v1 = _v0.a;
						return 'Applying window change…';
					case 'Unknown':
						var _v2 = _v0.a;
						return model.notice + ' The last request could not be confirmed.';
					case 'Refused':
						var _v3 = _v0.a;
						return model.notice + ' The window change was refused.';
					default:
						break _v0$3;
				}
			} else {
				break _v0$3;
			}
		}
		return model.notice;
	}
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
				'transportRefused',
				$elm$json$Json$Encode$bool(model.transportRefused)),
				_Utils_Tuple2(
				'notificationQueued',
				$elm$json$Json$Encode$bool(model.notificationQueued)),
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
				$author$project$Effects$encode(model.effects)),
				_Utils_Tuple2(
				'status',
				$elm$json$Json$Encode$string(
					$author$project$Shell$status(model))),
				_Utils_Tuple2(
				'recoveryFailure',
				A2(
					$elm$core$Maybe$withDefault,
					$elm$json$Json$Encode$null,
					A2(
						$elm$core$Maybe$map,
						A2($elm$core$Basics$composeR, $author$project$Shell$recoveryNotice, $elm$json$Json$Encode$string),
						model.recoveryFailure)))
			]));
};
var $author$project$TerminalProbe$incoming = _Platform_incomingPort('incoming', $elm$json$Json$Decode$value);
var $author$project$Shell$Detached = {$: 'Detached'};
var $author$project$Effects$empty = {connected: false, generation: $author$project$UInt64$zero, observed: $elm$core$Maybe$Nothing, request: $author$project$UInt64$zero, transaction: $elm$core$Maybe$Nothing, unresolved: _List_Nil};
var $author$project$Shell$initial = {attachNeeded: false, binding: $elm$core$Maybe$Nothing, deferNotifications: false, effects: $author$project$Effects$empty, expected: $elm$core$Maybe$Nothing, geometry: $elm$core$Maybe$Nothing, geometryAttachExpected: $elm$core$Maybe$Nothing, geometryCaps: $elm$core$Maybe$Nothing, geometryExpected: $elm$core$Maybe$Nothing, issued: _List_Nil, notice: 'Connecting…', notificationQueued: false, phase: $author$project$Shell$Detached, projectionRetryQueued: false, reconnecting: true, recoveryFailure: $elm$core$Maybe$Nothing, request: $author$project$UInt64$zero, transportRefused: false};
var $elm$json$Json$Decode$int = _Json_decodeInt;
var $elm$json$Json$Encode$int = _Json_wrap;
var $elm$json$Json$Decode$map2 = _Json_map2;
var $elm$core$Char$fromCode = _Char_fromCode;
var $elm$core$String$fromList = _String_fromList;
var $elm$core$String$foldr = _String_foldr;
var $elm$core$String$toList = function (string) {
	return A3($elm$core$String$foldr, $elm$core$List$cons, _List_Nil, string);
};
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
var $elm$core$Platform$Cmd$batch = _Platform_batch;
var $elm$core$Platform$Cmd$none = $elm$core$Platform$Cmd$batch(_List_Nil);
var $author$project$TerminalProbe$outgoing = _Platform_outgoingPort('outgoing', $elm$core$Basics$identity);
var $elm$core$Tuple$pair = F2(
	function (a, b) {
		return _Utils_Tuple2(a, b);
	});
var $author$project$Shell$Exhausted = {$: 'Exhausted'};
var $author$project$Shell$RestartBackend = {$: 'RestartBackend'};
var $author$project$Shell$Send = function (a) {
	return {$: 'Send', a: a};
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
var $author$project$Effects$Activate = {$: 'Activate'};
var $author$project$Effects$Maximize = {$: 'Maximize'};
var $author$project$Effects$Minimize = {$: 'Minimize'};
var $author$project$Effects$Restore = {$: 'Restore'};
var $author$project$Effects$RestoreGeometry = {$: 'RestoreGeometry'};
var $author$project$Effects$Unknown = {$: 'Unknown'};
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
var $elm$core$List$head = function (list) {
	if (list.b) {
		var x = list.a;
		var xs = list.b;
		return $elm$core$Maybe$Just(x);
	} else {
		return $elm$core$Maybe$Nothing;
	}
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
var $elm$core$List$member = F2(
	function (x, xs) {
		return A2(
			$elm$core$List$any,
			function (a) {
				return _Utils_eq(a, x);
			},
			xs);
	});
var $author$project$Effects$blocked = F3(
	function (lifetime, incarnation, model) {
		return A2(
			$elm$core$List$any,
			function (t) {
				return _Utils_eq(t.intent.context.lifetime, lifetime) && (_Utils_eq(t.intent.incarnation, incarnation) && A2(
					$elm$core$List$member,
					t.status,
					_List_fromArray(
						[$author$project$Effects$Pending, $author$project$Effects$Unknown])));
			},
			model.unresolved);
	});
var $elm$core$Basics$compare = _Utils_compare;
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
var $elm$json$Json$Decode$map4 = _Json_map4;
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
var $elm$json$Json$Decode$index = _Json_decodeIndex;
var $elm$json$Json$Decode$list = _Json_decodeList;
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
var $elm$json$Json$Decode$map = _Json_map1;
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
var $elm$core$Dict$RBEmpty_elm_builtin = {$: 'RBEmpty_elm_builtin'};
var $elm$core$Dict$empty = $elm$core$Dict$RBEmpty_elm_builtin;
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
var $elm$core$String$any = _String_any;
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
			case 'maximize':
				return $elm$json$Json$Decode$succeed($author$project$Effects$Maximize);
			case 'restore-geometry':
				return $elm$json$Json$Decode$succeed($author$project$Effects$RestoreGeometry);
			default:
				return $elm$json$Json$Decode$fail('Unsupported operation');
		}
	},
	$elm$json$Json$Decode$string);
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
var $author$project$Effects$protocol = function (operation) {
	return (_Utils_eq(operation, $author$project$Effects$Maximize) || _Utils_eq(operation, $author$project$Effects$RestoreGeometry)) ? 2 : 1;
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
				var _v11 = A2($elm$json$Json$Decode$decodeValue, decoder, value);
				if (_v11.$ === 'Err') {
					var error = _v11.a;
					return refuse(
						$elm$json$Json$Decode$errorToString(error));
				} else {
					var result = _v11.a;
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
										if ($elm$core$List$length(model.unresolved) >= 64) {
											return refuse('Unresolved operation capacity');
										} else {
											if (_Utils_eq(operation, $author$project$Effects$Maximize) || _Utils_eq(operation, $author$project$Effects$RestoreGeometry)) {
												return refuse('Geometry observation required');
											} else {
												if (A3($author$project$Effects$blocked, observed.context.lifetime, incarnation, model)) {
													return refuse('Unresolved native operation');
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
																				{effectProtocol: 1, intent: intent, status: $author$project$Effects$Pending}),
																			unresolved: A2(
																				$elm$core$List$cons,
																				{effectProtocol: 1, intent: intent, status: $author$project$Effects$Pending},
																				model.unresolved)
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
										}
									}
								}
							} else {
								return refuse('Disconnected or exhausted identity');
							}
						});
				case 'receipt':
					var receiptDecoder = $elm$json$Json$Decode$oneOf(
						_List_fromArray(
							[
								A2(
								$author$project$Effects$strict,
								_List_fromArray(
									['kind', 'intent', 'status']),
								A3(
									$elm$json$Json$Decode$map2,
									F2(
										function (intent, status) {
											return _Utils_Tuple3(1, intent, status);
										}),
									A2($elm$json$Json$Decode$field, 'intent', $author$project$Effects$intentDecoder),
									A2($elm$json$Json$Decode$field, 'status', $author$project$Effects$statusDecoder))),
								A2(
								$author$project$Effects$strict,
								_List_fromArray(
									['kind', 'intent', 'status', 'effectProtocol']),
								A4(
									$elm$json$Json$Decode$map3,
									F3(
										function (protocolId, intent, status) {
											return _Utils_Tuple3(protocolId, intent, status);
										}),
									A2($elm$json$Json$Decode$field, 'effectProtocol', $elm$json$Json$Decode$int),
									A2($elm$json$Json$Decode$field, 'intent', $author$project$Effects$intentDecoder),
									A2($elm$json$Json$Decode$field, 'status', $author$project$Effects$statusDecoder)))
							]));
					return A2(
						decoded,
						receiptDecoder,
						function (_v7) {
							var protocolId = _v7.a;
							var intent = _v7.b;
							var status = _v7.c;
							var exact = function (t) {
								return _Utils_eq(t.effectProtocol, protocolId) && _Utils_eq(t.intent, intent);
							};
							var found = A2($elm$core$List$any, exact, model.unresolved);
							var settled = function (t) {
								return exact(t) ? _Utils_update(
									t,
									{status: status}) : t;
							};
							var unresolved = _Utils_eq(status, $author$project$Effects$Unknown) ? A2($elm$core$List$map, settled, model.unresolved) : A2(
								$elm$core$List$filter,
								A2($elm$core$Basics$composeR, exact, $elm$core$Basics$not),
								model.unresolved);
							return ((!found) || ((!A2(
								$elm$core$List$member,
								protocolId,
								_List_fromArray(
									[1, 2]))) || (!_Utils_eq(
								$author$project$Effects$protocol(intent.operation),
								protocolId)))) ? refuse('Stale, mismatched or terminal receipt') : _Utils_Tuple3(
								_Utils_update(
									model,
									{
										transaction: A2(
											$elm$core$Maybe$map,
											function (t) {
												return A2(
													$elm$core$Maybe$withDefault,
													false,
													A2(
														$elm$core$Maybe$map,
														function (observed) {
															return A2($author$project$Effects$sameAuthority, observed.context, intent.context);
														},
														model.observed)) ? settled(t) : t;
											},
											model.transaction),
										unresolved: unresolved
									}),
								$elm$core$Maybe$Nothing,
								$elm$core$Maybe$Nothing);
						});
				case 'recover-watermarks':
					return A2(
						decoded,
						A2(
							$author$project$Effects$strict,
							_List_fromArray(
								['kind', 'request', 'generation']),
							A3(
								$elm$json$Json$Decode$map2,
								$elm$core$Tuple$pair,
								A2($elm$json$Json$Decode$field, 'request', $author$project$UInt64$decoder),
								A2($elm$json$Json$Decode$field, 'generation', $author$project$UInt64$decoder))),
						function (_v8) {
							var request = _v8.a;
							var generation = _v8.b;
							var maximum = F2(
								function (old, _new) {
									return _Utils_eq(
										A2($author$project$UInt64$compare, old, _new),
										$elm$core$Basics$LT) ? _new : old;
								});
							return _Utils_Tuple3(
								_Utils_update(
									model,
									{
										generation: A2(maximum, model.generation, generation),
										request: A2(maximum, model.request, request)
									}),
								$elm$core$Maybe$Nothing,
								$elm$core$Maybe$Nothing);
						});
				case 'recover':
					return A2(
						decoded,
						A2(
							$author$project$Effects$strict,
							_List_fromArray(
								['kind', 'intent', 'effectProtocol']),
							A3(
								$elm$json$Json$Decode$map2,
								$elm$core$Tuple$pair,
								A2($elm$json$Json$Decode$field, 'intent', $author$project$Effects$intentDecoder),
								A2($elm$json$Json$Decode$field, 'effectProtocol', $elm$json$Json$Decode$int))),
						function (_v9) {
							var intent = _v9.a;
							var protocolId = _v9.b;
							if ((!A2(
								$elm$core$List$member,
								protocolId,
								_List_fromArray(
									[1, 2]))) || (!_Utils_eq(
								$author$project$Effects$protocol(intent.operation),
								protocolId))) {
								return refuse('Recovery operation protocol');
							} else {
								if (A2(
									$elm$core$List$any,
									function (t) {
										return _Utils_eq(t.intent, intent) && _Utils_eq(t.effectProtocol, protocolId);
									},
									model.unresolved)) {
									return _Utils_Tuple3(model, $elm$core$Maybe$Nothing, $elm$core$Maybe$Nothing);
								} else {
									if ($elm$core$List$length(model.unresolved) >= 64) {
										return refuse('Unresolved operation capacity');
									} else {
										var transaction = {effectProtocol: protocolId, intent: intent, status: $author$project$Effects$Unknown};
										var maximum = F2(
											function (old, _new) {
												return _Utils_eq(
													A2($author$project$UInt64$compare, old, _new),
													$elm$core$Basics$LT) ? _new : old;
											});
										return _Utils_Tuple3(
											_Utils_update(
												model,
												{
													generation: A2(maximum, model.generation, intent.generation),
													request: A2(maximum, model.request, intent.request),
													transaction: $elm$core$Maybe$Just(transaction),
													unresolved: A2($elm$core$List$cons, transaction, model.unresolved)
												}),
											$elm$core$Maybe$Nothing,
											$elm$core$Maybe$Nothing);
									}
								}
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
						function (_v10) {
							return _Utils_Tuple3(
								_Utils_update(
									model,
									{
										connected: false,
										transaction: $author$project$Effects$unknown(model.transaction),
										unresolved: A2(
											$elm$core$List$map,
											function (t) {
												return _Utils_eq(t.status, $author$project$Effects$Pending) ? _Utils_update(
													t,
													{status: $author$project$Effects$Unknown}) : t;
											},
											model.unresolved)
									}),
								$elm$core$Maybe$Nothing,
								$elm$core$Maybe$Nothing);
						});
				default:
					return refuse('Unsupported message');
			}
		}
	});
var $author$project$GeometryProjection$Maximized = {$: 'Maximized'};
var $author$project$GeometryProjection$Ordinary = {$: 'Ordinary'};
var $author$project$ActionProjection$rootOf = F2(
	function (identity, _v0) {
		var cache = _v0.d;
		return A2(
			$elm$core$Dict$get,
			$author$project$UInt64$string(identity),
			cache);
	});
var $author$project$GeometryProjection$window = F2(
	function (incarnation, snapshot) {
		return $elm$core$List$head(
			A2(
				$elm$core$List$filter,
				function (row) {
					return _Utils_eq(row.incarnation, incarnation);
				},
				snapshot.windows));
	});
var $author$project$Effects$beginGeometry = F5(
	function (caps, observed, operation, incarnation, model) {
		var refuse = function (reason) {
			return _Utils_Tuple3(
				model,
				$elm$core$Maybe$Nothing,
				$elm$core$Maybe$Just(reason));
		};
		var legacyReady = A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (legacy) {
					return A2($author$project$ActionProjection$actionable, incarnation, legacy.scene) && _Utils_eq(
						A2($author$project$ActionProjection$rootOf, incarnation, legacy.scene),
						$elm$core$Maybe$Just(incarnation));
				},
				model.observed));
		var _v0 = _Utils_Tuple3(
			A2($author$project$GeometryProjection$window, incarnation, observed),
			$author$project$UInt64$next(model.request),
			$author$project$UInt64$next(model.generation));
		if (((_v0.a.$ === 'Just') && (_v0.b.$ === 'Just')) && (_v0.c.$ === 'Just')) {
			var window = _v0.a.a;
			var request = _v0.b.a;
			var generation = _v0.c.a;
			if ((!model.connected) || ((!legacyReady) || ($author$project$Effects$pending(model) || A3($author$project$Effects$blocked, observed.context.lifetime, incarnation, model)))) {
				return refuse('Unresolved or disconnected native operation');
			} else {
				if ($elm$core$List$length(model.unresolved) >= 64) {
					return refuse('Unresolved operation capacity');
				} else {
					if (($author$project$Effects$protocol(operation) !== 2) || ((!caps.effects) || (!A2(
						$elm$core$List$member,
						$author$project$Effects$operationName(operation),
						caps.operations)))) {
						return refuse('Geometry operation not negotiated');
					} else {
						if ((!window.eligible) || (window.minimized || window.fixedSize)) {
							return refuse('Geometry target ineligible');
						} else {
							if ((_Utils_eq(operation, $author$project$Effects$Maximize) && ((!window.maximize) || (!_Utils_eq(window.nativeMode, $author$project$GeometryProjection$Ordinary)))) || (_Utils_eq(operation, $author$project$Effects$RestoreGeometry) && ((!window.restoreGeometry) || ((!_Utils_eq(window.nativeMode, $author$project$GeometryProjection$Maximized)) || (!window.placementKnown))))) {
								return refuse('Geometry state/capability unavailable');
							} else {
								var intent = {context: observed.context, generation: generation, incarnation: incarnation, operation: operation, request: request};
								var transaction = {effectProtocol: 2, intent: intent, status: $author$project$Effects$Pending};
								return _Utils_Tuple3(
									_Utils_update(
										model,
										{
											generation: generation,
											request: request,
											transaction: $elm$core$Maybe$Just(transaction),
											unresolved: A2($elm$core$List$cons, transaction, model.unresolved)
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
													$elm$json$Json$Encode$int(2)),
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
			return refuse('Missing geometry target or exhausted identity');
		}
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
var $author$project$Effects$canProveUnsent = F3(
	function (protocolId, intent, model) {
		var exact = function (entry) {
			return _Utils_eq(entry.effectProtocol, protocolId) && _Utils_eq(entry.intent, intent);
		};
		var currentSafe = function () {
			var _v0 = model.transaction;
			if (_v0.$ === 'Just') {
				var entry = _v0.a;
				return (!exact(entry)) || _Utils_eq(entry.status, $author$project$Effects$Pending);
			} else {
				return true;
			}
		}();
		return _Utils_eq(
			$author$project$Effects$protocol(intent.operation),
			protocolId) && (currentSafe && A2(
			$elm$core$List$any,
			function (entry) {
				return exact(entry) && _Utils_eq(entry.status, $author$project$Effects$Pending);
			},
			model.unresolved));
	});
var $elm$core$List$isEmpty = function (xs) {
	if (!xs.b) {
		return true;
	} else {
		return false;
	}
};
var $author$project$Shell$canProveUnsent = F2(
	function (operations, model) {
		var unique = A3(
			$elm$core$List$foldl,
			F2(
				function (key, entries) {
					return A2($elm$core$List$member, key, entries) ? entries : A2($elm$core$List$cons, key, entries);
				}),
			_List_Nil,
			operations);
		var known = function (key) {
			return _Utils_eq(
				model.binding,
				$elm$core$Maybe$Just(key.binding)) && (A2(
				$elm$core$List$any,
				function (entry) {
					return _Utils_eq(entry.binding, key.binding) && (_Utils_eq(entry.protocol, key.protocol) && _Utils_eq(entry.intent, key.intent));
				},
				model.issued) && A3($author$project$Effects$canProveUnsent, key.protocol, key.intent, model.effects));
		};
		return (!$elm$core$List$isEmpty(operations)) && (($elm$core$List$length(operations) <= 16) && (_Utils_eq(
			$elm$core$List$length(unique),
			$elm$core$List$length(operations)) && ((!_Utils_eq(model.phase, $author$project$Shell$Detached)) && ((!_Utils_eq(model.phase, $author$project$Shell$Exhausted)) && A2($elm$core$List$all, known, operations)))));
	});
var $author$project$GeometryProjection$exact = F3(
	function (name, child, value) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (x) {
				return _Utils_eq(x, value) ? $elm$json$Json$Decode$succeed(_Utils_Tuple0) : $elm$json$Json$Decode$fail('Geometry version');
			},
			A2($elm$json$Json$Decode$field, name, child));
	});
var $author$project$GeometryProjection$strict = F2(
	function (fields, body) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? body : $elm$json$Json$Decode$fail('Geometry schema');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$GeometryProjection$capabilitiesDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (caps) {
		return (($elm$core$List$length(caps.operations) <= 2) && (A2(
			$elm$core$List$all,
			function (op) {
				return A2(
					$elm$core$List$member,
					op,
					_List_fromArray(
						['maximize', 'restore-geometry']));
			},
			caps.operations) && (_Utils_eq(
			$elm$core$List$length(caps.operations),
			$elm$core$List$length(
				A3(
					$elm$core$List$foldl,
					F2(
						function (x, xs) {
							return A2($elm$core$List$member, x, xs) ? xs : A2($elm$core$List$cons, x, xs);
						}),
					_List_Nil,
					caps.operations))) && _Utils_eq(
			caps.effects,
			!$elm$core$List$isEmpty(caps.operations))))) ? $elm$json$Json$Decode$succeed(caps) : $elm$json$Json$Decode$fail('Geometry capabilities');
	},
	A2(
		$author$project$GeometryProjection$strict,
		_List_fromArray(
			['observe', 'effects', 'effectProtocol', 'operations', 'placementCapacity', 'canonicalScene']),
		A7(
			$elm$json$Json$Decode$map6,
			F6(
				function (_v0, effects, _v1, operations, _v2, _v3) {
					return {effects: effects, operations: operations};
				}),
			A3($author$project$GeometryProjection$exact, 'observe', $elm$json$Json$Decode$bool, true),
			A2($elm$json$Json$Decode$field, 'effects', $elm$json$Json$Decode$bool),
			A3($author$project$GeometryProjection$exact, 'effectProtocol', $elm$json$Json$Decode$int, 2),
			A2(
				$elm$json$Json$Decode$field,
				'operations',
				$elm$json$Json$Decode$list($elm$json$Json$Decode$string)),
			A3($author$project$GeometryProjection$exact, 'placementCapacity', $elm$json$Json$Decode$int, 256),
			A3($author$project$GeometryProjection$exact, 'canonicalScene', $elm$json$Json$Decode$bool, false))));
var $author$project$Shell$Stamp = F3(
	function (a, b, c) {
		return {$: 'Stamp', a: a, b: b, c: c};
	});
var $author$project$Binding$matchesContext = F3(
	function (life, epoch, _v0) {
		var lifetime = _v0.a;
		var frontend = _v0.c;
		return _Utils_eq(life, lifetime) && _Utils_eq(epoch, frontend);
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
var $author$project$Shell$captureGeometry = function (model) {
	return A2(
		$elm$core$Maybe$map,
		function (observed) {
			return A3($author$project$Shell$Stamp, observed.binding, observed.context.output, observed.context.revision);
		},
		model.geometry);
};
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
var $elm$json$Json$Decode$map8 = _Json_map8;
var $author$project$GeometryProjection$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (x) {
		return _Utils_eq(x, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero geometry identity') : $elm$json$Json$Decode$succeed(x);
	},
	$author$project$UInt64$decoder);
var $author$project$GeometryProjection$Fullscreen = {$: 'Fullscreen'};
var $elm$core$Basics$min = F2(
	function (x, y) {
		return (_Utils_cmp(x, y) < 0) ? x : y;
	});
var $author$project$GeometrySizePolicy$fixed = function (inputs) {
	var axis = F4(
		function (rawLo, rawHi, layoutLo, layoutHi) {
			var upper = A2(
				$elm$core$Basics$min,
				2147483647,
				A2(
					$elm$core$Basics$min,
					(!rawHi) ? 2147483647 : $elm$core$Basics$floor(rawHi),
					$elm$core$Basics$floor(layoutHi)));
			var lower = A2(
				$elm$core$Basics$max,
				1,
				A2(
					$elm$core$Basics$max,
					$elm$core$Basics$ceiling(rawLo),
					$elm$core$Basics$floor(layoutLo)));
			return _Utils_cmp(lower, upper) > -1;
		});
	var _v0 = inputs.rawMaximum;
	var ux = _v0.a;
	var uy = _v0.b;
	var _v1 = inputs.rawMinimum;
	var rx = _v1.a;
	var ry = _v1.b;
	var _v2 = inputs.layoutMinimum;
	var lx = _v2.a;
	var ly = _v2.b;
	var _v3 = inputs.layoutMaximum;
	var hx = _v3.a;
	var hy = _v3.b;
	return A4(axis, rx, ux, lx, hx) || A4(axis, ry, uy, ly, hy);
};
var $author$project$GeometrySizePolicy$fromList = function (values) {
	if ((((values.b && values.b.b) && values.b.b.b) && values.b.b.b.b) && (!values.b.b.b.b.b)) {
		var x = values.a;
		var _v1 = values.b;
		var y = _v1.a;
		var _v2 = _v1.b;
		var w = _v2.a;
		var _v3 = _v2.b;
		var h = _v3.a;
		return $elm$core$Maybe$Just(
			{height: h, width: w, x: x, y: y});
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$GeometrySizePolicy$roundNative = function (x) {
	return (x >= 0) ? ($elm$core$Basics$floor(x) + (((x - $elm$core$Basics$floor(x)) >= 0.5) ? 1 : 0)) : ($elm$core$Basics$ceiling(x) - ((($elm$core$Basics$ceiling(x) - x) >= 0.5) ? 1 : 0));
};
var $author$project$GeometrySizePolicy$rounded = function (value) {
	return {
		height: $author$project$GeometrySizePolicy$roundNative(value.y + value.height) - $author$project$GeometrySizePolicy$roundNative(value.y),
		width: $author$project$GeometrySizePolicy$roundNative(value.x + value.width) - $author$project$GeometrySizePolicy$roundNative(value.x),
		x: $author$project$GeometrySizePolicy$roundNative(value.x),
		y: $author$project$GeometrySizePolicy$roundNative(value.y)
	};
};
var $author$project$GeometrySizePolicy$within = F2(
	function (inputs, projection) {
		var axis = F6(
			function (configured, real, rawLo, rawHi, lo, hi) {
				return (configured >= 1) && ((configured <= 2147483647) && ((_Utils_cmp(configured, rawLo) > -1) && (((!rawHi) || (_Utils_cmp(configured, rawHi) < 1)) && ((_Utils_cmp(real, lo) > -1) && (_Utils_cmp(real, hi) < 1)))));
			});
		var _v0 = inputs.rawMaximum;
		var ux = _v0.a;
		var uy = _v0.b;
		var _v1 = inputs.rawMinimum;
		var rx = _v1.a;
		var ry = _v1.b;
		var _v2 = inputs.layoutMinimum;
		var lx = _v2.a;
		var ly = _v2.b;
		var _v3 = inputs.layoutMaximum;
		var hx = _v3.a;
		var hy = _v3.b;
		var _v4 = projection.configure;
		var cx = _v4.a;
		var cy = _v4.b;
		return _Utils_eq(
			projection.configure,
			_Utils_Tuple2(
				$elm$core$Basics$floor(projection.real.width),
				$elm$core$Basics$floor(projection.real.height))) && (A6(axis, cx, projection.real.width, rx, ux, lx, hx) && A6(axis, cy, projection.real.height, ry, uy, ly, hy));
	});
var $author$project$GeometrySizePolicy$projectionValid = F4(
	function (maximize, workArea, inputs, projection) {
		var real = projection.real;
		var logical = projection.logical;
		var source = maximize ? A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				A2(
					$elm$core$Basics$composeR,
					$author$project$GeometrySizePolicy$rounded,
					$elm$core$Basics$eq(logical)),
				A2($elm$core$Maybe$andThen, $author$project$GeometrySizePolicy$fromList, workArea))) : _Utils_eq(
			projection.visual,
			$elm$core$Maybe$Just(real));
		var _v0 = inputs.topLeft;
		var tx = _v0.a;
		var ty = _v0.b;
		var _v1 = inputs.bottomRight;
		var bx = _v1.a;
		var by = _v1.b;
		var converted = maximize ? {height: logical.height - (ty + by), width: logical.width - (tx + bx), x: logical.x + tx, y: logical.y + ty} : logical;
		return _Utils_eq(
			logical,
			$author$project$GeometrySizePolicy$rounded(logical)) && (A2(
			$elm$core$Maybe$withDefault,
			true,
			A2(
				$elm$core$Maybe$map,
				function (v) {
					return _Utils_eq(
						v,
						$author$project$GeometrySizePolicy$rounded(v));
				},
				projection.visual)) && (_Utils_eq(real, converted) && (A2($author$project$GeometrySizePolicy$within, inputs, projection) && (source && ((!maximize) || _Utils_eq(projection.visual, $elm$core$Maybe$Nothing))))));
	});
var $author$project$GeometrySizePolicy$supported = function (policy) {
	var _v0 = policy.inputs;
	if (_v0.$ === 'Nothing') {
		return false;
	} else {
		var inputs = _v0.a;
		return _Utils_eq(
			inputs.origin,
			_Utils_Tuple2(0, 0)) && (!$author$project$GeometrySizePolicy$fixed(inputs));
	}
};
var $author$project$GeometrySizePolicy$coherent = F4(
	function (policy, workArea, constrained, fixedSize) {
		var _v0 = policy.inputs;
		if (_v0.$ === 'Nothing') {
			return _Utils_eq(policy.maximize, $elm$core$Maybe$Nothing) && _Utils_eq(policy.restoreGeometry, $elm$core$Maybe$Nothing);
		} else {
			var inputs = _v0.a;
			var values = function (_v1) {
				var x = _v1.a;
				var y = _v1.b;
				return _List_fromArray(
					[x, y]);
			};
			var valid = F2(
				function (maximize, projection) {
					return A2(
						$elm$core$Maybe$withDefault,
						true,
						A2(
							$elm$core$Maybe$map,
							function (p) {
								return $author$project$GeometrySizePolicy$supported(policy) && A4($author$project$GeometrySizePolicy$projectionValid, maximize, workArea, inputs, p);
							},
							projection));
				});
			var expected = A2(
				$elm$core$List$any,
				$elm$core$Basics$lt(1),
				_Utils_ap(
					values(inputs.rawMinimum),
					values(inputs.layoutMinimum))) || (A2(
				$elm$core$List$any,
				$elm$core$Basics$lt(0),
				values(inputs.rawMaximum)) || A2(
				$elm$core$List$any,
				$elm$core$Basics$gt(1.7976931348623157e308),
				values(inputs.layoutMaximum)));
			return _Utils_eq(constrained, expected) && (_Utils_eq(
				fixedSize,
				$author$project$GeometrySizePolicy$fixed(inputs)) && (A2(valid, true, policy.maximize) && A2(valid, false, policy.restoreGeometry)));
		}
	});
var $author$project$GeometrySizePolicy$permits = F2(
	function (maximize, policy) {
		return $author$project$GeometrySizePolicy$supported(policy) && (maximize ? (!_Utils_eq(policy.maximize, $elm$core$Maybe$Nothing)) : (!_Utils_eq(policy.restoreGeometry, $elm$core$Maybe$Nothing)));
	});
var $author$project$GeometryProjection$validRows = F3(
	function (caps, blocked, rows) {
		var walk = F2(
			function (visited, id) {
				walk:
				while (true) {
					if (A2($elm$core$List$member, id, visited)) {
						return false;
					} else {
						var _v0 = $elm$core$List$head(
							A2(
								$elm$core$List$filter,
								function (row) {
									return _Utils_eq(row.incarnation, id);
								},
								rows));
						if (_v0.$ === 'Nothing') {
							return false;
						} else {
							var row = _v0.a;
							var _v1 = row.owner;
							if (_v1.$ === 'Nothing') {
								return true;
							} else {
								var parent = _v1.a;
								var $temp$visited = A2($elm$core$List$cons, id, visited),
									$temp$id = parent;
								visited = $temp$visited;
								id = $temp$id;
								continue walk;
							}
						}
					}
				}
			});
		var rowValid = function (row) {
			var sizeValid = A2(
				$elm$core$Maybe$withDefault,
				true,
				A2(
					$elm$core$Maybe$map,
					function (p) {
						return A4($author$project$GeometrySizePolicy$coherent, p, row.workArea, row.constrainedSize, row.fixedSize) && (((!row.eligible) || $author$project$GeometrySizePolicy$supported(p)) && (((!row.maximize) || A2($author$project$GeometrySizePolicy$permits, true, p)) && ((!row.restoreGeometry) || A2($author$project$GeometrySizePolicy$permits, false, p))));
					},
					row.sizePolicy));
			var ownership = function () {
				var _v2 = row.owner;
				if (_v2.$ === 'Nothing') {
					return true;
				} else {
					return A2(walk, _List_Nil, row.incarnation);
				}
			}();
			var known = A2(
				$elm$core$List$map,
				$elm$core$Basics$identity,
				_List_fromArray(
					[
						!_Utils_eq(row.workspace, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.workspaceGeneration, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.monitor, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.outputOwnershipGeneration, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.workAreaRevision, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.workArea, $elm$core$Maybe$Nothing)
					]));
			var paired = A2(
				$elm$core$List$all,
				$elm$core$Basics$eq(true),
				known) || A2(
				$elm$core$List$all,
				$elm$core$Basics$eq(false),
				known);
			var eligible = (!row.eligible) || ((!_Utils_eq(row.workspace, $elm$core$Maybe$Nothing)) && ((!blocked) && ((!row.minimized) && ((!row.grouped) && ((!row.fixedSize) && (((!_Utils_eq(row.sizePolicy, $elm$core$Maybe$Nothing)) || (!row.constrainedSize)) && (row.floating && (_Utils_eq(row.owner, $elm$core$Maybe$Nothing) && (_Utils_eq(row.nativeMode, row.clientMode) && (!_Utils_eq(row.nativeMode, $author$project$GeometryProjection$Fullscreen)))))))))));
			var capabilityModes = ((!row.maximize) || (row.eligible && _Utils_eq(row.nativeMode, $author$project$GeometryProjection$Ordinary))) && ((!row.restoreGeometry) || (row.eligible && (_Utils_eq(row.nativeMode, $author$project$GeometryProjection$Maximized) && row.placementKnown)));
			return paired && (eligible && (ownership && (sizeValid && (capabilityModes && (((!row.maximize) || A2($elm$core$List$member, 'maximize', caps.operations)) && ((!row.restoreGeometry) || A2($elm$core$List$member, 'restore-geometry', caps.operations)))))));
		};
		var ids = A2(
			$elm$core$List$map,
			function ($) {
				return $.incarnation;
			},
			rows);
		var unique = _Utils_eq(
			$elm$core$List$length(ids),
			$elm$core$List$length(
				A3(
					$elm$core$List$foldl,
					F2(
						function (x, xs) {
							return A2($elm$core$List$member, x, xs) ? xs : A2($elm$core$List$cons, x, xs);
						}),
					_List_Nil,
					ids)));
		var coherent = F2(
			function (a, b) {
				return (_Utils_eq(a.outputOwnershipGeneration, $elm$core$Maybe$Nothing) || ((!_Utils_eq(a.outputOwnershipGeneration, b.outputOwnershipGeneration)) || _Utils_eq(a.monitor, b.monitor))) && (_Utils_eq(a.workspaceGeneration, $elm$core$Maybe$Nothing) || ((!_Utils_eq(a.workspaceGeneration, b.workspaceGeneration)) || (_Utils_eq(a.workspace, b.workspace) && (_Utils_eq(a.outputOwnershipGeneration, b.outputOwnershipGeneration) && (_Utils_eq(a.workAreaRevision, b.workAreaRevision) && _Utils_eq(a.workArea, b.workArea))))));
			});
		return ($elm$core$List$length(rows) <= 256) && (unique && (A2($elm$core$List$all, rowValid, rows) && A2(
			$elm$core$List$all,
			function (a) {
				return A2(
					$elm$core$List$all,
					coherent(a),
					rows);
			},
			rows)));
	});
var $author$project$GeometrySizePolicy$Policy = F3(
	function (inputs, maximize, restoreGeometry) {
		return {inputs: inputs, maximize: maximize, restoreGeometry: restoreGeometry};
	});
var $elm$core$Basics$isInfinite = _Basics_isInfinite;
var $elm$core$Basics$isNaN = _Basics_isNaN;
var $author$project$GeometrySizePolicy$finite = function (x) {
	return !($elm$core$Basics$isNaN(x) || $elm$core$Basics$isInfinite(x));
};
var $elm$json$Json$Decode$float = _Json_decodeFloat;
var $author$project$GeometrySizePolicy$interval = F3(
	function (raw, _v0, _v1) {
		var lx = _v0.a;
		var ly = _v0.b;
		var ux = _v1.a;
		var uy = _v1.b;
		var axis = F2(
			function (lo, hi) {
				return (raw && (!hi)) || ((hi > 0) && (_Utils_cmp(lo, hi) < 0));
			});
		return A2(axis, lx, ux) && A2(axis, ly, uy);
	});
var $author$project$GeometrySizePolicy$pair = function (nonnegative) {
	return A2(
		$elm$json$Json$Decode$andThen,
		function (values) {
			if ((values.b && values.b.b) && (!values.b.b.b)) {
				var x = values.a;
				var _v1 = values.b;
				var y = _v1.a;
				return ($author$project$GeometrySizePolicy$finite(x) && ($author$project$GeometrySizePolicy$finite(y) && ((!nonnegative) || ((x >= 0) && (y >= 0))))) ? $elm$json$Json$Decode$succeed(
					_Utils_Tuple2(x, y)) : $elm$json$Json$Decode$fail('Size vector');
			} else {
				return $elm$json$Json$Decode$fail('Size vector shape');
			}
		},
		$elm$json$Json$Decode$list($elm$json$Json$Decode$float));
};
var $author$project$GeometrySizePolicy$strict = F2(
	function (fields, body) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? body : $elm$json$Json$Decode$fail('Size policy schema');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$GeometrySizePolicy$inputsDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (inputs) {
		return ($author$project$GeometrySizePolicy$finite(inputs.scale) && ((inputs.scale > 0) && (A3($author$project$GeometrySizePolicy$interval, true, inputs.rawMinimum, inputs.rawMaximum) && A3($author$project$GeometrySizePolicy$interval, false, inputs.layoutMinimum, inputs.layoutMaximum)))) ? $elm$json$Json$Decode$succeed(inputs) : $elm$json$Json$Decode$fail('Size intervals');
	},
	A2(
		$author$project$GeometrySizePolicy$strict,
		_List_fromArray(
			['profile', 'rawMinimum', 'rawMaximum', 'layoutMinimum', 'layoutMaximum', 'geometryOrigin', 'reservedTopLeft', 'reservedBottomRight', 'monitorScale']),
		A3(
			$elm$json$Json$Decode$map2,
			F2(
				function (_v0, inputs) {
					return inputs;
				}),
			A2(
				$elm$json$Json$Decode$andThen,
				function (profile) {
					return (profile === 'wayland-zero-origin-v1') ? $elm$json$Json$Decode$succeed(_Utils_Tuple0) : $elm$json$Json$Decode$fail('Conversion profile');
				},
				A2($elm$json$Json$Decode$field, 'profile', $elm$json$Json$Decode$string)),
			A9(
				$elm$json$Json$Decode$map8,
				F8(
					function (rawMin, rawMax, layoutMin, layoutMax, origin, tl, br, scale) {
						return {bottomRight: br, layoutMaximum: layoutMax, layoutMinimum: layoutMin, origin: origin, rawMaximum: rawMax, rawMinimum: rawMin, scale: scale, topLeft: tl};
					}),
				A2(
					$elm$json$Json$Decode$field,
					'rawMinimum',
					$author$project$GeometrySizePolicy$pair(true)),
				A2(
					$elm$json$Json$Decode$field,
					'rawMaximum',
					$author$project$GeometrySizePolicy$pair(true)),
				A2(
					$elm$json$Json$Decode$field,
					'layoutMinimum',
					$author$project$GeometrySizePolicy$pair(true)),
				A2(
					$elm$json$Json$Decode$field,
					'layoutMaximum',
					$author$project$GeometrySizePolicy$pair(true)),
				A2(
					$elm$json$Json$Decode$field,
					'geometryOrigin',
					$author$project$GeometrySizePolicy$pair(false)),
				A2(
					$elm$json$Json$Decode$field,
					'reservedTopLeft',
					$author$project$GeometrySizePolicy$pair(true)),
				A2(
					$elm$json$Json$Decode$field,
					'reservedBottomRight',
					$author$project$GeometrySizePolicy$pair(true)),
				A2($elm$json$Json$Decode$field, 'monitorScale', $elm$json$Json$Decode$float)))));
var $author$project$GeometrySizePolicy$Projection = F4(
	function (logical, visual, real, configure) {
		return {configure: configure, logical: logical, real: real, visual: visual};
	});
var $elm$core$Basics$negate = function (n) {
	return -n;
};
var $elm$core$Basics$abs = function (n) {
	return (n < 0) ? (-n) : n;
};
var $author$project$GeometrySizePolicy$box = A2(
	$elm$json$Json$Decode$andThen,
	function (values) {
		if ((((values.b && values.b.b) && values.b.b.b) && values.b.b.b.b) && (!values.b.b.b.b.b)) {
			var x = values.a;
			var _v1 = values.b;
			var y = _v1.a;
			var _v2 = _v1.b;
			var w = _v2.a;
			var _v3 = _v2.b;
			var h = _v3.a;
			return (A2($elm$core$List$all, $author$project$GeometrySizePolicy$finite, values) && (A2(
				$elm$core$List$all,
				function (v) {
					return $elm$core$Basics$abs(v) <= 2147483647;
				},
				values) && ((w > 0) && (h > 0)))) ? $elm$json$Json$Decode$succeed(
				{height: h, width: w, x: x, y: y}) : $elm$json$Json$Decode$fail('Prospective box');
		} else {
			return $elm$json$Json$Decode$fail('Prospective box shape');
		}
	},
	$elm$json$Json$Decode$list($elm$json$Json$Decode$float));
var $author$project$GeometrySizePolicy$projectionDecoder = A2(
	$author$project$GeometrySizePolicy$strict,
	_List_fromArray(
		['logical', 'visual', 'real', 'configure']),
	A5(
		$elm$json$Json$Decode$map4,
		$author$project$GeometrySizePolicy$Projection,
		A2($elm$json$Json$Decode$field, 'logical', $author$project$GeometrySizePolicy$box),
		A2(
			$elm$json$Json$Decode$field,
			'visual',
			$elm$json$Json$Decode$nullable($author$project$GeometrySizePolicy$box)),
		A2($elm$json$Json$Decode$field, 'real', $author$project$GeometrySizePolicy$box),
		A2(
			$elm$json$Json$Decode$field,
			'configure',
			$author$project$GeometrySizePolicy$pair(true))));
var $author$project$GeometrySizePolicy$decoder = A2(
	$author$project$GeometrySizePolicy$strict,
	_List_fromArray(
		['inputs', 'maximize', 'restoreGeometry']),
	A4(
		$elm$json$Json$Decode$map3,
		$author$project$GeometrySizePolicy$Policy,
		A2(
			$elm$json$Json$Decode$field,
			'inputs',
			$elm$json$Json$Decode$nullable($author$project$GeometrySizePolicy$inputsDecoder)),
		A2(
			$elm$json$Json$Decode$field,
			'maximize',
			$elm$json$Json$Decode$nullable($author$project$GeometrySizePolicy$projectionDecoder)),
		A2(
			$elm$json$Json$Decode$field,
			'restoreGeometry',
			$elm$json$Json$Decode$nullable($author$project$GeometrySizePolicy$projectionDecoder))));
var $author$project$GeometryProjection$modeDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (x) {
		switch (x) {
			case 'ordinary':
				return $elm$json$Json$Decode$succeed($author$project$GeometryProjection$Ordinary);
			case 'maximized':
				return $elm$json$Json$Decode$succeed($author$project$GeometryProjection$Maximized);
			case 'fullscreen':
				return $elm$json$Json$Decode$succeed($author$project$GeometryProjection$Fullscreen);
			default:
				return $elm$json$Json$Decode$fail('Geometry mode');
		}
	},
	$elm$json$Json$Decode$string);
var $author$project$GeometryProjection$rect = A2(
	$elm$json$Json$Decode$andThen,
	function (xs) {
		if ((((xs.b && xs.b.b) && xs.b.b.b) && xs.b.b.b.b) && (!xs.b.b.b.b.b)) {
			var x = xs.a;
			var _v1 = xs.b;
			var y = _v1.a;
			var _v2 = _v1.b;
			var w = _v2.a;
			var _v3 = _v2.b;
			var h = _v3.a;
			return (A2(
				$elm$core$List$all,
				function (n) {
					return !($elm$core$Basics$isNaN(n) || $elm$core$Basics$isInfinite(n));
				},
				_List_fromArray(
					[x, y, w, h, x + w, y + h])) && ((w > 0) && (h > 0))) ? $elm$json$Json$Decode$succeed(xs) : $elm$json$Json$Decode$fail('Geometry rectangle');
		} else {
			return $elm$json$Json$Decode$fail('Geometry rectangle shape');
		}
	},
	$elm$json$Json$Decode$list($elm$json$Json$Decode$float));
var $elm$core$Tuple$second = function (_v0) {
	var y = _v0.b;
	return y;
};
var $elm$core$String$slice = _String_slice;
var $elm$core$String$dropLeft = F2(
	function (n, string) {
		return (n < 1) ? string : A3(
			$elm$core$String$slice,
			n,
			$elm$core$String$length(string),
			string);
	});
var $author$project$GeometryProjection$workspace = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		var negative = A2($elm$core$String$startsWith, '-', value);
		var limit = negative ? '9223372036854775808' : '9223372036854775807';
		var digits = negative ? A2($elm$core$String$dropLeft, 1, value) : value;
		var valid = (!$elm$core$String$isEmpty(digits)) && (A2($elm$core$String$all, $elm$core$Char$isDigit, digits) && (((digits === '0') || (!A2($elm$core$String$startsWith, '0', digits))) && ((!(negative && (digits === '0'))) && (($elm$core$String$length(digits) < 19) || (($elm$core$String$length(digits) === 19) && (_Utils_cmp(digits, limit) < 1))))));
		return valid ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Workspace identity');
	},
	$elm$json$Json$Decode$string);
var $author$project$GeometryProjection$windowDecoder = function (protocol) {
	var state = A9(
		$elm$json$Json$Decode$map8,
		F8(
			function (logical, visual, _native, client, minimized, floating, grouped, fixed) {
				return {client: client, fixed: fixed, floating: floating, grouped: grouped, logical: logical, minimized: minimized, _native: _native, visual: visual};
			}),
		A2($elm$json$Json$Decode$field, 'logicalGeometry', $author$project$GeometryProjection$rect),
		A2($elm$json$Json$Decode$field, 'visualGeometry', $author$project$GeometryProjection$rect),
		A2($elm$json$Json$Decode$field, 'nativeMode', $author$project$GeometryProjection$modeDecoder),
		A2($elm$json$Json$Decode$field, 'clientMode', $author$project$GeometryProjection$modeDecoder),
		A2($elm$json$Json$Decode$field, 'minimized', $elm$json$Json$Decode$bool),
		A2($elm$json$Json$Decode$field, 'floating', $elm$json$Json$Decode$bool),
		A2($elm$json$Json$Decode$field, 'grouped', $elm$json$Json$Decode$bool),
		A2($elm$json$Json$Decode$field, 'fixedSize', $elm$json$Json$Decode$bool));
	var policy = A6(
		$elm$json$Json$Decode$map5,
		F5(
			function (constrained, eligible, known, caps, size) {
				return {caps: caps, constrained: constrained, eligible: eligible, known: known, size: size};
			}),
		A2($elm$json$Json$Decode$field, 'constrainedSize', $elm$json$Json$Decode$bool),
		A2($elm$json$Json$Decode$field, 'geometryEligible', $elm$json$Json$Decode$bool),
		A2($elm$json$Json$Decode$field, 'ordinaryPlacementKnown', $elm$json$Json$Decode$bool),
		A2(
			$elm$json$Json$Decode$field,
			'capabilities',
			A2(
				$author$project$GeometryProjection$strict,
				_List_fromArray(
					['maximize', 'restoreGeometry']),
				A3(
					$elm$json$Json$Decode$map2,
					$elm$core$Tuple$pair,
					A2($elm$json$Json$Decode$field, 'maximize', $elm$json$Json$Decode$bool),
					A2($elm$json$Json$Decode$field, 'restoreGeometry', $elm$json$Json$Decode$bool)))),
		(protocol === 2) ? A2(
			$elm$json$Json$Decode$map,
			$elm$core$Maybe$Just,
			A2($elm$json$Json$Decode$field, 'sizePolicy', $author$project$GeometrySizePolicy$decoder)) : $elm$json$Json$Decode$succeed($elm$core$Maybe$Nothing));
	var identities = A9(
		$elm$json$Json$Decode$map8,
		F8(
			function (inc, owner, ws, wg, mon, og, wr, wa) {
				return {inc: inc, mon: mon, og: og, owner: owner, wa: wa, wg: wg, wr: wr, ws: ws};
			}),
		A2($elm$json$Json$Decode$field, 'incarnation', $author$project$GeometryProjection$positive),
		A2(
			$elm$json$Json$Decode$field,
			'owner',
			$elm$json$Json$Decode$nullable($author$project$GeometryProjection$positive)),
		A2(
			$elm$json$Json$Decode$field,
			'workspace',
			$elm$json$Json$Decode$nullable($author$project$GeometryProjection$workspace)),
		A2(
			$elm$json$Json$Decode$field,
			'workspaceGeneration',
			$elm$json$Json$Decode$nullable($author$project$GeometryProjection$positive)),
		A2(
			$elm$json$Json$Decode$field,
			'monitor',
			$elm$json$Json$Decode$nullable($author$project$UInt64$decoder)),
		A2(
			$elm$json$Json$Decode$field,
			'outputOwnershipGeneration',
			$elm$json$Json$Decode$nullable($author$project$GeometryProjection$positive)),
		A2(
			$elm$json$Json$Decode$field,
			'workAreaRevision',
			$elm$json$Json$Decode$nullable($author$project$GeometryProjection$positive)),
		A2(
			$elm$json$Json$Decode$field,
			'workArea',
			$elm$json$Json$Decode$nullable($author$project$GeometryProjection$rect)));
	return A2(
		$author$project$GeometryProjection$strict,
		_Utils_ap(
			_List_fromArray(
				['incarnation', 'owner', 'workspace', 'workspaceGeneration', 'monitor', 'outputOwnershipGeneration', 'workAreaRevision', 'workArea', 'logicalGeometry', 'visualGeometry', 'nativeMode', 'clientMode', 'minimized', 'floating', 'grouped', 'fixedSize', 'constrainedSize', 'geometryEligible', 'ordinaryPlacementKnown', 'capabilities']),
			(protocol === 2) ? _List_fromArray(
				['sizePolicy']) : _List_Nil),
		A4(
			$elm$json$Json$Decode$map3,
			F3(
				function (i, s, p) {
					return {clientMode: s.client, constrainedSize: p.constrained, eligible: p.eligible, fixedSize: s.fixed, floating: s.floating, grouped: s.grouped, incarnation: i.inc, logicalGeometry: s.logical, maximize: p.caps.a, minimized: s.minimized, monitor: i.mon, nativeMode: s._native, outputOwnershipGeneration: i.og, owner: i.owner, placementKnown: p.known, restoreGeometry: p.caps.b, sizePolicy: p.size, visualGeometry: s.visual, workArea: i.wa, workAreaRevision: i.wr, workspace: i.ws, workspaceGeneration: i.wg};
				}),
			identities,
			state,
			policy));
};
var $author$project$GeometryProjection$decoder = F2(
	function (protocol, caps) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (snapshot) {
				return (A3($author$project$GeometryProjection$validRows, caps, snapshot.blocked, snapshot.windows) && A2(
					$elm$core$Maybe$withDefault,
					true,
					A2(
						$elm$core$Maybe$map,
						function (id) {
							return A2(
								$elm$core$List$any,
								function (row) {
									return _Utils_eq(row.incarnation, id);
								},
								snapshot.windows);
						},
						snapshot.focused))) ? $elm$json$Json$Decode$succeed(snapshot) : $elm$json$Json$Decode$fail('Geometry facts coherence');
			},
			A2(
				$author$project$GeometryProjection$strict,
				_List_fromArray(
					['protocolVersion', 'kind', 'geometryProtocol', 'binding', 'requestId', 'sequence', 'revision', 'outputGeneration', 'facts']),
				A9(
					$elm$json$Json$Decode$map8,
					F8(
						function (_v0, _v1, _v2, binding, request, sequence, revision, rest) {
							var _v3 = rest;
							var output = _v3.a;
							var facts = _v3.b;
							var context = function () {
								var _v4 = A2(
									$elm$json$Json$Decode$decodeValue,
									A3(
										$elm$json$Json$Decode$map2,
										$elm$core$Tuple$pair,
										A2($elm$json$Json$Decode$field, 'lifetime', $author$project$GeometryProjection$positive),
										A2($elm$json$Json$Decode$field, 'frontend', $author$project$GeometryProjection$positive)),
									$author$project$Binding$encode(binding));
								if (_v4.$ === 'Ok') {
									var _v5 = _v4.a;
									var life = _v5.a;
									var epoch = _v5.b;
									return {epoch: epoch, lifetime: life, output: output, revision: revision};
								} else {
									return {epoch: $author$project$UInt64$zero, lifetime: $author$project$UInt64$zero, output: output, revision: revision};
								}
							}();
							return {binding: binding, blocked: facts.blocked, context: context, focused: facts.focused, request: request, sequence: sequence, windows: facts.windows};
						}),
					A3($author$project$GeometryProjection$exact, 'protocolVersion', $elm$json$Json$Decode$int, 3),
					A3($author$project$GeometryProjection$exact, 'kind', $elm$json$Json$Decode$string, 'geometry-facts'),
					A3($author$project$GeometryProjection$exact, 'geometryProtocol', $elm$json$Json$Decode$int, protocol),
					A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
					A2($elm$json$Json$Decode$field, 'requestId', $author$project$GeometryProjection$positive),
					A2($elm$json$Json$Decode$field, 'sequence', $author$project$GeometryProjection$positive),
					A2($elm$json$Json$Decode$field, 'revision', $author$project$GeometryProjection$positive),
					A3(
						$elm$json$Json$Decode$map2,
						$elm$core$Tuple$pair,
						A2($elm$json$Json$Decode$field, 'outputGeneration', $author$project$GeometryProjection$positive),
						A2(
							$elm$json$Json$Decode$field,
							'facts',
							A2(
								$author$project$GeometryProjection$strict,
								_List_fromArray(
									['focused', 'inputBlocked', 'windows']),
								A4(
									$elm$json$Json$Decode$map3,
									F3(
										function (focus, blocked, rows) {
											return {blocked: blocked, focused: focus, windows: rows};
										}),
									A2(
										$elm$json$Json$Decode$field,
										'focused',
										$elm$json$Json$Decode$nullable($author$project$GeometryProjection$positive)),
									A2($elm$json$Json$Decode$field, 'inputBlocked', $elm$json$Json$Decode$bool),
									A2(
										$elm$json$Json$Decode$field,
										'windows',
										$elm$json$Json$Decode$list(
											$author$project$GeometryProjection$windowDecoder(protocol))))))))));
	});
var $author$project$GeometryProjection$decode = F2(
	function (caps, raw) {
		return A2(
			$elm$core$Result$mapError,
			function (_v0) {
				return 'Invalid geometry projection';
			},
			A2(
				$elm$json$Json$Decode$decodeValue,
				A2($author$project$GeometryProjection$decoder, 2, caps),
				raw));
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
		{
			attachNeeded: false,
			deferNotifications: false,
			effects: effects,
			expected: $elm$core$Maybe$Nothing,
			geometry: $elm$core$Maybe$Nothing,
			geometryAttachExpected: $elm$core$Maybe$Nothing,
			geometryCaps: $elm$core$Maybe$Nothing,
			geometryExpected: $elm$core$Maybe$Nothing,
			notice: A2(
				$elm$core$Maybe$withDefault,
				'Connection lost. Reconnect to continue.',
				A2($elm$core$Maybe$map, $author$project$Shell$recoveryNotice, model.recoveryFailure)),
			notificationQueued: false,
			phase: $author$project$Shell$Detached,
			projectionRetryQueued: false,
			reconnecting: false,
			transportRefused: false
		});
};
var $author$project$Shell$refresh = function (model) {
	var _v0 = _Utils_Tuple2(
		model.binding,
		$author$project$UInt64$next(model.request));
	if ((_v0.a.$ === 'Just') && (_v0.b.$ === 'Just')) {
		var binding = _v0.a.a;
		var request = _v0.b.a;
		return (_Utils_eq(model.phase, $author$project$Shell$Detached) || model.transportRefused) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
			_Utils_update(
				model,
				{
					expected: $elm$core$Maybe$Just(request),
					phase: $author$project$Shell$Reconciling,
					projectionRetryQueued: false,
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
var $author$project$Shell$geometryRequest = F2(
	function (attach, model) {
		if (model.transportRefused) {
			return _Utils_Tuple2(model, _List_Nil);
		} else {
			var _v0 = _Utils_Tuple2(
				model.binding,
				$author$project$UInt64$next(model.request));
			if ((_v0.a.$ === 'Just') && (_v0.b.$ === 'Just')) {
				var binding = _v0.a.a;
				var request = _v0.b.a;
				if (_Utils_eq(model.phase, $author$project$Shell$Detached) || ((attach && (!_Utils_eq(model.geometryAttachExpected, $elm$core$Maybe$Nothing))) || ((!attach) && (_Utils_eq(model.geometryCaps, $elm$core$Maybe$Nothing) || (!_Utils_eq(model.geometryExpected, $elm$core$Maybe$Nothing)))))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var common = _List_fromArray(
						[
							_Utils_Tuple2(
							'protocolVersion',
							$elm$json$Json$Encode$int(3)),
							_Utils_Tuple2(
							'kind',
							$elm$json$Json$Encode$string(
								attach ? 'geometry-attach' : 'geometry-facts-request')),
							_Utils_Tuple2(
							'geometryProtocol',
							$elm$json$Json$Encode$int(2)),
							_Utils_Tuple2(
							'binding',
							$author$project$Binding$encode(binding)),
							_Utils_Tuple2(
							'requestId',
							$elm$json$Json$Encode$string(
								$author$project$UInt64$string(request)))
						]);
					var payload = attach ? common : _Utils_ap(
						common,
						_List_fromArray(
							[
								_Utils_Tuple2(
								'minimumWatermark',
								$elm$json$Json$Encode$string(
									A2(
										$elm$core$Maybe$withDefault,
										'0',
										A2(
											$elm$core$Maybe$map,
											A2(
												$elm$core$Basics$composeR,
												function ($) {
													return $.sequence;
												},
												$author$project$UInt64$string),
											model.geometry))))
							]));
					return _Utils_Tuple2(
						_Utils_update(
							model,
							{
								attachNeeded: attach || model.attachNeeded,
								geometryAttachExpected: attach ? $elm$core$Maybe$Just(request) : model.geometryAttachExpected,
								geometryExpected: attach ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(request),
								request: request
							}),
						_List_fromArray(
							[
								$author$project$Shell$Send(
								$elm$json$Json$Encode$object(payload))
							]));
				}
			} else {
				return _Utils_Tuple2(model, _List_Nil);
			}
		}
	});
var $author$project$Shell$geometrySupported = function (model) {
	return A2(
		$elm$core$Maybe$withDefault,
		false,
		A2(
			$elm$core$Maybe$map,
			function ($) {
				return $.effects;
			},
			model.geometryCaps));
};
var $author$project$Shell$refreshObservations = function (model) {
	if (model.transportRefused) {
		return _Utils_Tuple2(model, _List_Nil);
	} else {
		var _v0 = $author$project$Shell$refresh(
			_Utils_update(
				model,
				{notificationQueued: false}));
		var legacy = _v0.a;
		var commands = _v0.b;
		if (legacy.attachNeeded) {
			var _v1 = A2($author$project$Shell$geometryRequest, true, legacy);
			var attached = _v1.a;
			var attachCommands = _v1.b;
			return _Utils_Tuple2(
				attached,
				_Utils_ap(commands, attachCommands));
		} else {
			if ($author$project$Shell$geometrySupported(legacy)) {
				var _v2 = A2($author$project$Shell$geometryRequest, false, legacy);
				var geometry = _v2.a;
				var geometryCommands = _v2.b;
				return _Utils_Tuple2(
					geometry,
					_Utils_ap(commands, geometryCommands));
			} else {
				return _Utils_Tuple2(legacy, commands);
			}
		}
	}
};
var $author$project$Shell$drainNotifications = function (model) {
	return model.projectionRetryQueued ? ((_Utils_eq(model.phase, $author$project$Shell$Detached) || (_Utils_eq(model.phase, $author$project$Shell$Exhausted) || _Utils_eq(model.binding, $elm$core$Maybe$Nothing))) ? _Utils_Tuple2(
		_Utils_update(
			model,
			{projectionRetryQueued: false}),
		_List_Nil) : ((model.transportRefused || (model.deferNotifications || ($author$project$Effects$pending(model.effects) || ((!_Utils_eq(model.expected, $elm$core$Maybe$Nothing)) || (!_Utils_eq(model.geometryAttachExpected, $elm$core$Maybe$Nothing)))))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$refresh(model))) : (((!model.transportRefused) && ((!model.deferNotifications) && (model.notificationQueued && (_Utils_eq(model.phase, $author$project$Shell$Ready) && ((!$author$project$Effects$pending(model.effects)) && (_Utils_eq(model.expected, $elm$core$Maybe$Nothing) && (_Utils_eq(model.geometryExpected, $elm$core$Maybe$Nothing) && _Utils_eq(model.geometryAttachExpected, $elm$core$Maybe$Nothing)))))))) ? $author$project$Shell$refreshObservations(model) : _Utils_Tuple2(model, _List_Nil));
};
var $author$project$Effects$locallyRefuseUnsent = F3(
	function (protocolId, intent, model) {
		var exact = function (entry) {
			return _Utils_eq(entry.effectProtocol, protocolId) && _Utils_eq(entry.intent, intent);
		};
		return (!A3($author$project$Effects$canProveUnsent, protocolId, intent, model)) ? model : _Utils_update(
			model,
			{
				transaction: A2(
					$elm$core$Maybe$map,
					function (entry) {
						return exact(entry) ? _Utils_update(
							entry,
							{status: $author$project$Effects$Refused}) : entry;
					},
					model.transaction),
				unresolved: A2(
					$elm$core$List$filter,
					A2($elm$core$Basics$composeR, exact, $elm$core$Basics$not),
					model.unresolved)
			});
	});
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
var $author$project$Shell$matchesUnsent = F2(
	function (observations, model) {
		var slot = function (kind) {
			switch (kind) {
				case 'projection-request':
					return model.expected;
				case 'geometry-facts-request':
					return model.geometryExpected;
				case 'geometry-attach':
					return model.geometryAttachExpected;
				default:
					return $elm$core$Maybe$Nothing;
			}
		};
		return (!$elm$core$List$isEmpty(observations)) && A2(
			$elm$core$List$all,
			function (_v0) {
				var kind = _v0.a;
				var request = _v0.b;
				return _Utils_eq(
					slot(kind),
					$elm$core$Maybe$Just(request));
			},
			observations);
	});
var $author$project$Shell$notificationRefresh = function (model) {
	return (_Utils_eq(model.phase, $author$project$Shell$Detached) || (_Utils_eq(model.phase, $author$project$Shell$Exhausted) || model.transportRefused)) ? _Utils_Tuple2(model, _List_Nil) : ((model.deferNotifications || ($author$project$Effects$pending(model.effects) || ((!_Utils_eq(model.expected, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(model.geometryExpected, $elm$core$Maybe$Nothing)) || (!_Utils_eq(model.geometryAttachExpected, $elm$core$Maybe$Nothing)))))) ? _Utils_Tuple2(
		_Utils_update(
			model,
			{notificationQueued: true}),
		_List_Nil) : $author$project$Shell$refreshObservations(model));
};
var $author$project$Shell$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (!_Utils_eq(value, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Zero displayed scope');
	},
	$author$project$UInt64$decoder);
var $author$project$Shell$Busy = {$: 'Busy'};
var $author$project$Shell$Full = {$: 'Full'};
var $author$project$Shell$LegacyOwner = {$: 'LegacyOwner'};
var $author$project$Shell$Unavailable = {$: 'Unavailable'};
var $author$project$Shell$Unverified = {$: 'Unverified'};
var $author$project$Shell$recoveryDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (reason) {
		switch (reason) {
			case 'unavailable':
				return $elm$json$Json$Decode$succeed($author$project$Shell$Unavailable);
			case 'full':
				return $elm$json$Json$Decode$succeed($author$project$Shell$Full);
			case 'busy':
				return $elm$json$Json$Decode$succeed($author$project$Shell$Busy);
			case 'unverified':
				return $elm$json$Json$Decode$succeed($author$project$Shell$Unverified);
			case 'legacy-owner':
				return $elm$json$Json$Decode$succeed($author$project$Shell$LegacyOwner);
			default:
				return $elm$json$Json$Decode$fail('Recovery reason');
		}
	},
	$elm$json$Json$Decode$string);
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
var $author$project$Shell$resumeNotifications = function (model) {
	return $author$project$Shell$drainNotifications(
		_Utils_update(
			model,
			{deferNotifications: false}));
};
var $author$project$Binding$sameLifetime = F2(
	function (life, _v0) {
		var lifetime = _v0.a;
		return _Utils_eq(life, lifetime);
	});
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
var $elm$core$Result$toMaybe = function (result) {
	if (result.$ === 'Ok') {
		var v = result.a;
		return $elm$core$Maybe$Just(v);
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
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
var $author$project$NativeOutcome$intent = function (protocolId) {
	return A2(
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
						(protocolId === 1) ? _List_fromArray(
							['minimize', 'restore', 'activate']) : _List_fromArray(
							['maximize', 'restore-geometry'])) ? $elm$json$Json$Decode$succeed(_Utils_Tuple0) : $elm$json$Json$Decode$fail('Outcome operation');
				},
				A2($elm$json$Json$Decode$field, 'operation', $elm$json$Json$Decode$string)),
			A2($elm$json$Json$Decode$field, 'context', $author$project$NativeOutcome$context)));
};
var $author$project$NativeOutcome$decoderBody = function (protocolId) {
	return A2(
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
			A3($author$project$NativeOutcome$exact, 'effectProtocol', $elm$json$Json$Decode$int, protocolId),
			A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
			A2(
				$elm$json$Json$Decode$field,
				'intent',
				$author$project$NativeOutcome$intent(protocolId)),
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
};
var $author$project$NativeOutcome$decoder = A2(
	$elm$json$Json$Decode$andThen,
	function (protocolId) {
		return A2(
			$elm$core$List$member,
			protocolId,
			_List_fromArray(
				[1, 2])) ? $author$project$NativeOutcome$decoderBody(protocolId) : $elm$json$Json$Decode$fail('Effect protocol');
	},
	A2($elm$json$Json$Decode$field, 'effectProtocol', $elm$json$Json$Decode$int));
var $author$project$NativeOutcome$valid = function (value) {
	var _v0 = A2($elm$json$Json$Decode$decodeValue, $author$project$NativeOutcome$decoder, value);
	if (_v0.$ === 'Ok') {
		return true;
	} else {
		return false;
	}
};
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
				return (_Utils_eq(model.phase, $author$project$Shell$Detached) || $author$project$Effects$pending(model.effects)) ? _Utils_Tuple2(model, _List_Nil) : ($author$project$Shell$geometrySupported(model) ? $author$project$Shell$notificationRefresh(model) : $author$project$Shell$refresh(model));
			case 'Reconnect':
				return (_Utils_eq(model.phase, $author$project$Shell$Detached) && (!model.reconnecting)) ? _Utils_Tuple2(
					_Utils_update(
						model,
						{notice: 'Reconnecting…', reconnecting: true}),
					_List_fromArray(
						[$author$project$Shell$RestartBackend])) : _Utils_Tuple2(model, _List_Nil);
			case 'SupersedeObservations':
				var reissue = msg.a;
				if (_Utils_eq(model.phase, $author$project$Shell$Detached) || (_Utils_eq(model.phase, $author$project$Shell$Exhausted) || _Utils_eq(model.binding, $elm$core$Maybe$Nothing))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var retired = _Utils_update(
						model,
						{deferNotifications: false, expected: $elm$core$Maybe$Nothing, geometryAttachExpected: $elm$core$Maybe$Nothing, geometryExpected: $elm$core$Maybe$Nothing, notificationQueued: true, phase: $author$project$Shell$Reconciling, projectionRetryQueued: false});
					var attach = model.attachNeeded || (!_Utils_eq(model.geometryAttachExpected, $elm$core$Maybe$Nothing));
					if (!reissue) {
						return _Utils_Tuple2(retired, _List_Nil);
					} else {
						var _v1 = $author$project$Shell$refreshObservations(retired);
						var fresh = _v1.a;
						var commands = _v1.b;
						var _v2 = attach ? A2($author$project$Shell$geometryRequest, true, fresh) : _Utils_Tuple2(fresh, _List_Nil);
						var attached = _v2.a;
						var attachCommands = _v2.b;
						return _Utils_Tuple2(
							attached,
							_Utils_ap(commands, attachCommands));
					}
				}
			case 'RegistrationRefused':
				var operations = msg.a;
				var observations = msg.b;
				var matches = F2(
					function (key, entry) {
						return _Utils_eq(entry.binding, key.binding) && (_Utils_eq(entry.protocol, key.protocol) && _Utils_eq(entry.intent, key.intent));
					});
				var keys = A3(
					$elm$core$List$foldl,
					F2(
						function (key, unique) {
							return A2($elm$core$List$member, key, unique) ? unique : A2($elm$core$List$cons, key, unique);
						}),
					_List_Nil,
					operations);
				var proven = A2(
					$elm$core$List$filter,
					function (key) {
						return A2(
							$author$project$Shell$canProveUnsent,
							_List_fromArray(
								[key]),
							model);
					},
					keys);
				var has = F2(
					function (kind, slot) {
						return A2(
							$elm$core$List$any,
							function (_v3) {
								var name = _v3.a;
								var id = _v3.b;
								return _Utils_eq(name, kind) && _Utils_eq(
									slot,
									$elm$core$Maybe$Just(id));
							},
							observations);
					});
				var effects = A3(
					$elm$core$List$foldl,
					F2(
						function (key, state) {
							return A3($author$project$Effects$locallyRefuseUnsent, key.protocol, key.intent, state);
						}),
					model.effects,
					proven);
				var retired = _Utils_update(
					model,
					{
						attachNeeded: model.attachNeeded || A2(has, 'geometry-attach', model.geometryAttachExpected),
						deferNotifications: false,
						effects: effects,
						expected: A2(has, 'projection-request', model.expected) ? $elm$core$Maybe$Nothing : model.expected,
						geometryAttachExpected: A2(has, 'geometry-attach', model.geometryAttachExpected) ? $elm$core$Maybe$Nothing : model.geometryAttachExpected,
						geometryExpected: A2(has, 'geometry-facts-request', model.geometryExpected) ? $elm$core$Maybe$Nothing : model.geometryExpected,
						issued: A2(
							$elm$core$List$filter,
							function (entry) {
								return !A2(
									$elm$core$List$any,
									function (key) {
										return A2(matches, key, entry);
									},
									proven);
							},
							model.issued),
						notice: 'The request was not sent. Waiting for window transport recovery.',
						notificationQueued: true,
						phase: (_Utils_eq(model.phase, $author$project$Shell$Detached) || _Utils_eq(model.phase, $author$project$Shell$Exhausted)) ? model.phase : $author$project$Shell$Reconciling,
						transportRefused: true
					});
				return _Utils_Tuple2(retired, _List_Nil);
			case 'RegistrationAvailable':
				var reissue = msg.a;
				if (!model.transportRefused) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var recovered = _Utils_update(
						model,
						{transportRefused: false});
					return ((!reissue) || (_Utils_eq(recovered.phase, $author$project$Shell$Detached) || (_Utils_eq(recovered.phase, $author$project$Shell$Exhausted) || ($author$project$Effects$pending(recovered.effects) || ((!_Utils_eq(recovered.expected, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(recovered.geometryExpected, $elm$core$Maybe$Nothing)) || (!_Utils_eq(recovered.geometryAttachExpected, $elm$core$Maybe$Nothing)))))))) ? _Utils_Tuple2(recovered, _List_Nil) : $author$project$Shell$refreshObservations(recovered);
				}
			case 'UnsentOperations':
				var operations = msg.a;
				if (!A2($author$project$Shell$canProveUnsent, operations, model)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var matches = F2(
						function (key, entry) {
							return _Utils_eq(entry.binding, key.binding) && (_Utils_eq(entry.protocol, key.protocol) && _Utils_eq(entry.intent, key.intent));
						});
					var effects = A3(
						$elm$core$List$foldl,
						F2(
							function (key, state) {
								return A3($author$project$Effects$locallyRefuseUnsent, key.protocol, key.intent, state);
							}),
						model.effects,
						operations);
					var updated = _Utils_update(
						model,
						{
							effects: effects,
							issued: A2(
								$elm$core$List$filter,
								function (entry) {
									return !A2(
										$elm$core$List$any,
										function (key) {
											return A2(matches, key, entry);
										},
										operations);
								},
								model.issued),
							notice: 'The request was not sent. Choose again.'
						});
					return $author$project$Shell$resumeNotifications(updated);
				}
			case 'UnsentObservations':
				var observations = msg.a;
				var valid = A2($author$project$Shell$matchesUnsent, observations, model);
				var contains = function (kind) {
					return A2(
						$elm$core$List$any,
						function (_v6) {
							var name = _v6.a;
							return _Utils_eq(name, kind);
						},
						observations);
				};
				var cleared = _Utils_update(
					model,
					{
						expected: contains('projection-request') ? $elm$core$Maybe$Nothing : model.expected,
						geometryAttachExpected: contains('geometry-attach') ? $elm$core$Maybe$Nothing : model.geometryAttachExpected,
						geometryExpected: contains('geometry-facts-request') ? $elm$core$Maybe$Nothing : model.geometryExpected,
						notificationQueued: true
					});
				if ((!valid) || (_Utils_eq(model.phase, $author$project$Shell$Detached) || _Utils_eq(model.phase, $author$project$Shell$Exhausted))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					if ($author$project$Effects$pending(model.effects) || (model.deferNotifications || ((!_Utils_eq(cleared.expected, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(cleared.geometryExpected, $elm$core$Maybe$Nothing)) || (!_Utils_eq(cleared.geometryAttachExpected, $elm$core$Maybe$Nothing)))))) {
						return _Utils_Tuple2(cleared, _List_Nil);
					} else {
						var _v4 = $author$project$Shell$refreshObservations(cleared);
						var fresh = _v4.a;
						var commands = _v4.b;
						var _v5 = contains('geometry-attach') ? A2($author$project$Shell$geometryRequest, true, fresh) : _Utils_Tuple2(fresh, _List_Nil);
						var attached = _v5.a;
						var attachCommands = _v5.b;
						return _Utils_Tuple2(
							attached,
							_Utils_ap(commands, attachCommands));
					}
				}
			case 'Ignore':
				return _Utils_Tuple2(model, _List_Nil);
			case 'GeometryAttach':
				return A2($author$project$Shell$geometryRequest, true, model);
			case 'GeometryRefresh':
				return A2($author$project$Shell$geometryRequest, false, model);
			case 'Act':
				var stamp = msg.a;
				var operation = msg.b;
				var incarnation = msg.c;
				if (!$author$project$Shell$available(model)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					if (!_Utils_eq(
						($author$project$Effects$protocol(operation) === 2) ? $author$project$Shell$captureGeometry(model) : $author$project$Shell$capture(model),
						$elm$core$Maybe$Just(stamp))) {
						return _Utils_Tuple2(
							_Utils_update(
								model,
								{notice: 'Window list changed. Choose again.'}),
							_List_Nil);
					} else {
						var _v7 = function () {
							if ($author$project$Effects$protocol(operation) === 2) {
								var _v8 = _Utils_Tuple2(model.geometryCaps, model.geometry);
								if ((_v8.a.$ === 'Just') && (_v8.b.$ === 'Just')) {
									var caps = _v8.a.a;
									var observed = _v8.b.a;
									return ((!_Utils_eq(model.geometryExpected, $elm$core$Maybe$Nothing)) || (!_Utils_eq(model.geometryAttachExpected, $elm$core$Maybe$Nothing))) ? _Utils_Tuple3(
										model.effects,
										$elm$core$Maybe$Nothing,
										$elm$core$Maybe$Just('Geometry refresh pending')) : A5($author$project$Effects$beginGeometry, caps, observed, operation, incarnation, model.effects);
								} else {
									return _Utils_Tuple3(
										model.effects,
										$elm$core$Maybe$Nothing,
										$elm$core$Maybe$Just('Geometry observation unavailable'));
								}
							} else {
								return A2(
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
							}
						}();
						var effects = _v7.a;
						var command = _v7.b;
						var error = _v7.c;
						var commands = function () {
							var _v10 = _Utils_Tuple2(command, model.binding);
							if ((_v10.a.$ === 'Just') && (_v10.b.$ === 'Just')) {
								var value = _v10.a.a;
								var binding = _v10.b.a;
								var _v11 = A2(
									$elm$json$Json$Decode$decodeValue,
									A2($elm$json$Json$Decode$field, 'intent', $elm$json$Json$Decode$value),
									value);
								if (_v11.$ === 'Ok') {
									var intent = _v11.a;
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
														$elm$json$Json$Encode$int(
															$author$project$Effects$protocol(operation))),
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
									issued: function () {
										var _v9 = _Utils_Tuple3(command, model.binding, effects.transaction);
										if (((_v9.a.$ === 'Just') && (_v9.b.$ === 'Just')) && (_v9.c.$ === 'Just')) {
											var binding = _v9.b.a;
											var transaction = _v9.c.a;
											return A2(
												$elm$core$List$cons,
												{binding: binding, intent: transaction.intent, protocol: transaction.effectProtocol},
												model.issued);
										} else {
											return model.issued;
										}
									}(),
									notice: A2($elm$core$Maybe$withDefault, model.notice, error)
								}),
							commands);
					}
				}
			default:
				var raw = msg.a;
				var _v12 = A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
					raw);
				_v12$13:
				while (true) {
					if (_v12.$ === 'Ok') {
						switch (_v12.a) {
							case 'host-recovery-failed':
								var _v13 = A2(
									$elm$json$Json$Decode$decodeValue,
									A2(
										$author$project$Shell$strict,
										_List_fromArray(
											['protocolVersion', 'kind', 'reason']),
										A3(
											$elm$json$Json$Decode$map2,
											F2(
												function (_v14, reason) {
													return reason;
												}),
											$author$project$Shell$version,
											A2($elm$json$Json$Decode$field, 'reason', $author$project$Shell$recoveryDecoder))),
									raw);
								if (_v13.$ === 'Ok') {
									var reason = _v13.a;
									var detached = $author$project$Shell$disconnect(model);
									return _Utils_Tuple2(
										_Utils_update(
											detached,
											{
												notice: $author$project$Shell$recoveryNotice(reason),
												recoveryFailure: $elm$core$Maybe$Just(reason)
											}),
										_List_Nil);
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'host-disconnected':
								return _Utils_Tuple2(
									$author$project$Shell$disconnect(model),
									_List_Nil);
							case 'host-refresh':
								var _v15 = A2(
									$elm$json$Json$Decode$decodeValue,
									A2(
										$author$project$Shell$strict,
										_List_fromArray(
											['protocolVersion', 'kind']),
										$author$project$Shell$version),
									raw);
								if (_v15.$ === 'Ok') {
									return $author$project$Shell$notificationRefresh(model);
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'attached':
								var _v16 = A2(
									$elm$json$Json$Decode$decodeValue,
									A3(
										$elm$json$Json$Decode$map2,
										F2(
											function (_v17, binding) {
												return binding;
											}),
										$author$project$Shell$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder)),
									raw);
								if (_v16.$ === 'Ok') {
									var binding = _v16.a;
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
													reconnecting: false,
													recoveryFailure: $elm$core$Maybe$Nothing
												}));
									}
								} else {
									return _Utils_Tuple2(
										$author$project$Shell$disconnect(model),
										_List_Nil);
								}
							case 'projection-unavailable':
								var decoder = A2(
									$author$project$Shell$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'reason']),
									A5(
										$elm$json$Json$Decode$map4,
										F4(
											function (_v20, binding, request, _v21) {
												return _Utils_Tuple2(binding, request);
											}),
										$author$project$Shell$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$Shell$positive),
										A2(
											$elm$json$Json$Decode$andThen,
											function (reason) {
												return (reason === 'scene-changed') ? $elm$json$Json$Decode$succeed(_Utils_Tuple0) : $elm$json$Json$Decode$fail('Projection terminal reason');
											},
											A2($elm$json$Json$Decode$field, 'reason', $elm$json$Json$Decode$string))));
								var _v18 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (_v18.$ === 'Err') {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var _v19 = _v18.a;
									var binding = _v19.a;
									var request = _v19.b;
									return (_Utils_eq(model.phase, $author$project$Shell$Detached) || (_Utils_eq(model.phase, $author$project$Shell$Exhausted) || ((!_Utils_eq(
										model.binding,
										$elm$core$Maybe$Just(binding))) || (!_Utils_eq(
										model.expected,
										$elm$core$Maybe$Just(request)))))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$drainNotifications(
										_Utils_update(
											model,
											{expected: $elm$core$Maybe$Nothing, notificationQueued: true, phase: $author$project$Shell$Reconciling, projectionRetryQueued: true}));
								}
							case 'action-projection':
								var decoder = A2(
									$author$project$Shell$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'context', 'scene']),
									A6(
										$elm$json$Json$Decode$map5,
										F5(
											function (_v27, binding, request, life, epoch) {
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
								var _v22 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (_v22.$ === 'Ok') {
									var _v23 = _v22.a;
									var binding = _v23.a;
									var request = _v23.b;
									var _v24 = _v23.c;
									var life = _v24.a;
									var epoch = _v24.b;
									if (_Utils_eq(model.phase, $author$project$Shell$Detached) || ((!_Utils_eq(
										model.binding,
										$elm$core$Maybe$Just(binding))) || ((!_Utils_eq(
										model.expected,
										$elm$core$Maybe$Just(request))) || (!A3($author$project$Binding$matchesContext, life, epoch, binding))))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var _v25 = A2(
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
										if (_v25.$ === 'Ok') {
											var snapshot = _v25.a;
											var _v26 = A2($author$project$Effects$apply, snapshot, model.effects);
											var effects = _v26.a;
											var error = _v26.c;
											return $author$project$Shell$drainNotifications(
												_Utils_update(
													model,
													{
														effects: effects,
														expected: _Utils_eq(error, $elm$core$Maybe$Nothing) ? $elm$core$Maybe$Nothing : model.expected,
														notice: _Utils_eq(error, $elm$core$Maybe$Nothing) ? 'Connected' : 'Window information could not be verified.',
														phase: _Utils_eq(error, $elm$core$Maybe$Nothing) ? $author$project$Shell$Ready : $author$project$Shell$Reconciling
													}));
										} else {
											return _Utils_Tuple2(model, _List_Nil);
										}
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'host-geometry-negotiate':
								var _v28 = A2(
									$elm$json$Json$Decode$decodeValue,
									A2(
										$author$project$Shell$strict,
										_List_fromArray(
											['protocolVersion', 'kind']),
										$author$project$Shell$version),
									raw);
								if (_v28.$ === 'Err') {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									return ((!_Utils_eq(model.geometryCaps, $elm$core$Maybe$Nothing)) || (!_Utils_eq(model.geometryAttachExpected, $elm$core$Maybe$Nothing))) ? _Utils_Tuple2(model, _List_Nil) : A2($author$project$Shell$geometryRequest, true, model);
								}
							case 'geometry-unavailable':
								var decoder = A2(
									$author$project$Shell$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'reason']),
									A5(
										$elm$json$Json$Decode$map4,
										F4(
											function (_v30, binding, request, reason) {
												return {binding: binding, reason: reason, request: request};
											}),
										$author$project$Shell$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$Shell$positive),
										A2(
											$elm$json$Json$Decode$andThen,
											function (reason) {
												return ($elm$core$String$length(reason) <= 256) ? $elm$json$Json$Decode$succeed(reason) : $elm$json$Json$Decode$fail('Geometry refusal reason');
											},
											A2($elm$json$Json$Decode$field, 'reason', $elm$json$Json$Decode$string))));
								var _v29 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (_v29.$ === 'Err') {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var refusal = _v29.a;
									return ((!_Utils_eq(
										model.binding,
										$elm$core$Maybe$Just(refusal.binding))) || (!_Utils_eq(
										model.geometryAttachExpected,
										$elm$core$Maybe$Just(refusal.request)))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$drainNotifications(
										_Utils_update(
											model,
											{
												attachNeeded: false,
												geometry: $elm$core$Maybe$Nothing,
												geometryAttachExpected: $elm$core$Maybe$Nothing,
												geometryCaps: $elm$core$Maybe$Just(
													{effects: false, operations: _List_Nil}),
												geometryExpected: $elm$core$Maybe$Nothing
											}));
								}
							case 'geometry-attached':
								var decoder = A2(
									$author$project$Shell$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'geometryProtocol', 'binding', 'requestId', 'capabilities']),
									A6(
										$elm$json$Json$Decode$map5,
										F5(
											function (_v32, _v33, binding, request, caps) {
												return {binding: binding, caps: caps, request: request};
											}),
										$author$project$Shell$version,
										A2(
											$elm$json$Json$Decode$andThen,
											function (v) {
												return (v === 2) ? $elm$json$Json$Decode$succeed(_Utils_Tuple0) : $elm$json$Json$Decode$fail('Geometry protocol');
											},
											A2($elm$json$Json$Decode$field, 'geometryProtocol', $elm$json$Json$Decode$int)),
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$Shell$positive),
										A2($elm$json$Json$Decode$field, 'capabilities', $author$project$GeometryProjection$capabilitiesDecoder)));
								var _v31 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (_v31.$ === 'Ok') {
									var value = _v31.a;
									return ((!_Utils_eq(
										model.binding,
										$elm$core$Maybe$Just(value.binding))) || ((!_Utils_eq(
										model.geometryAttachExpected,
										$elm$core$Maybe$Just(value.request))) || _Utils_eq(model.phase, $author$project$Shell$Detached))) ? _Utils_Tuple2(model, _List_Nil) : A2(
										$author$project$Shell$geometryRequest,
										false,
										_Utils_update(
											model,
											{
												attachNeeded: false,
												geometry: $elm$core$Maybe$Nothing,
												geometryAttachExpected: $elm$core$Maybe$Nothing,
												geometryCaps: $elm$core$Maybe$Just(value.caps)
											}));
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'geometry-facts':
								var _v34 = model.geometryCaps;
								if (_v34.$ === 'Nothing') {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var caps = _v34.a;
									var _v35 = A2($author$project$GeometryProjection$decode, caps, raw);
									if (_v35.$ === 'Err') {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var observed = _v35.a;
										var newer = function () {
											var _v36 = model.geometry;
											if (_v36.$ === 'Nothing') {
												return true;
											} else {
												var old = _v36.a;
												return (_Utils_eq(old.context.lifetime, observed.context.lifetime) && _Utils_eq(old.context.epoch, observed.context.epoch)) ? ((!_Utils_eq(
													A2($author$project$UInt64$compare, observed.context.output, old.context.output),
													$elm$core$Basics$LT)) && ((!_Utils_eq(
													A2($author$project$UInt64$compare, observed.sequence, old.sequence),
													$elm$core$Basics$LT)) && ((!_Utils_eq(
													A2($author$project$UInt64$compare, observed.context.revision, old.context.revision),
													$elm$core$Basics$LT)) && ((!_Utils_eq(observed.context.revision, old.context.revision)) || _Utils_eq(
													observed,
													_Utils_update(
														old,
														{request: observed.request, sequence: observed.sequence})))))) : true;
											}
										}();
										return ((!_Utils_eq(
											model.binding,
											$elm$core$Maybe$Just(observed.binding))) || ((!_Utils_eq(
											model.geometryExpected,
											$elm$core$Maybe$Just(observed.request))) || (_Utils_eq(model.phase, $author$project$Shell$Detached) || (!newer)))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$drainNotifications(
											_Utils_update(
												model,
												{
													geometry: $elm$core$Maybe$Just(observed),
													geometryExpected: $elm$core$Maybe$Nothing
												}));
									}
								}
							case 'host-recovery-watermarks':
								var decoder = A2(
									$author$project$Shell$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'request', 'generation']),
									A5(
										$elm$json$Json$Decode$map4,
										F4(
											function (_v40, binding, request, generation) {
												return _Utils_Tuple3(binding, request, generation);
											}),
										$author$project$Shell$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'request', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'generation', $author$project$UInt64$decoder)));
								var _v37 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (_v37.$ === 'Ok') {
									var _v38 = _v37.a;
									var binding = _v38.a;
									var request = _v38.b;
									var generation = _v38.c;
									if ((!_Utils_eq(model.phase, $author$project$Shell$Reconciling)) || (!_Utils_eq(
										model.binding,
										$elm$core$Maybe$Just(binding)))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var _v39 = A2(
											$author$project$Effects$apply,
											$elm$json$Json$Encode$object(
												_List_fromArray(
													[
														_Utils_Tuple2(
														'kind',
														$elm$json$Json$Encode$string('recover-watermarks')),
														_Utils_Tuple2(
														'request',
														$elm$json$Json$Encode$string(
															$author$project$UInt64$string(request))),
														_Utils_Tuple2(
														'generation',
														$elm$json$Json$Encode$string(
															$author$project$UInt64$string(generation)))
													])),
											model.effects);
										var effects = _v39.a;
										return _Utils_Tuple2(
											_Utils_update(
												model,
												{effects: effects}),
											_List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'host-uncertain':
								var decoder = $elm$json$Json$Decode$oneOf(
									_List_fromArray(
										[
											A2(
											$author$project$Shell$strict,
											_List_fromArray(
												['protocolVersion', 'kind', 'binding', 'intent']),
											A4(
												$elm$json$Json$Decode$map3,
												F3(
													function (_v44, binding, intent) {
														return _Utils_Tuple3(binding, intent, 1);
													}),
												$author$project$Shell$version,
												A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
												A2($elm$json$Json$Decode$field, 'intent', $elm$json$Json$Decode$value))),
											A2(
											$author$project$Shell$strict,
											_List_fromArray(
												['protocolVersion', 'kind', 'binding', 'intent', 'effectProtocol']),
											A5(
												$elm$json$Json$Decode$map4,
												F4(
													function (_v45, binding, intent, protocolId) {
														return _Utils_Tuple3(binding, intent, protocolId);
													}),
												$author$project$Shell$version,
												A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
												A2($elm$json$Json$Decode$field, 'intent', $elm$json$Json$Decode$value),
												A2($elm$json$Json$Decode$field, 'effectProtocol', $elm$json$Json$Decode$int)))
										]));
								var _v41 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (_v41.$ === 'Ok') {
									var _v42 = _v41.a;
									var binding = _v42.a;
									var intent = _v42.b;
									var protocolId = _v42.c;
									if ((!_Utils_eq(
										model.binding,
										$elm$core$Maybe$Just(binding))) || ((!_Utils_eq(model.phase, $author$project$Shell$Reconciling)) || (!_Utils_eq(
										A2(
											$elm$core$Result$map,
											function (life) {
												return A2($author$project$Binding$sameLifetime, life, binding);
											},
											A2(
												$elm$json$Json$Decode$decodeValue,
												A2(
													$elm$json$Json$Decode$at,
													_List_fromArray(
														['context', 'lifetime']),
													$author$project$Shell$positive),
												intent)),
										$elm$core$Result$Ok(true))))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var _v43 = A2(
											$author$project$Effects$apply,
											$elm$json$Json$Encode$object(
												_List_fromArray(
													[
														_Utils_Tuple2(
														'kind',
														$elm$json$Json$Encode$string('recover')),
														_Utils_Tuple2('intent', intent),
														_Utils_Tuple2(
														'effectProtocol',
														$elm$json$Json$Encode$int(protocolId))
													])),
											model.effects);
										var effects = _v43.a;
										var error = _v43.c;
										return (!_Utils_eq(error, $elm$core$Maybe$Nothing)) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
											_Utils_update(
												model,
												{effects: effects, notice: 'The previous window change could not be confirmed.'}),
											_List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'effect-outcome':
								if (!$author$project$NativeOutcome$valid(raw)) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var _v46 = A2(
										$elm$json$Json$Decode$decodeValue,
										A5(
											$elm$json$Json$Decode$map4,
											F4(
												function (_v47, binding, protocolId, receipt) {
													return _Utils_Tuple3(binding, protocolId, receipt);
												}),
											$author$project$Shell$version,
											A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
											A2($elm$json$Json$Decode$field, 'effectProtocol', $elm$json$Json$Decode$int),
											A4(
												$elm$json$Json$Decode$map3,
												F3(
													function (intent, outcome, protocolId) {
														return $elm$json$Json$Encode$object(
															_List_fromArray(
																[
																	_Utils_Tuple2(
																	'kind',
																	$elm$json$Json$Encode$string('receipt')),
																	_Utils_Tuple2('intent', intent),
																	_Utils_Tuple2('status', outcome),
																	_Utils_Tuple2('effectProtocol', protocolId)
																]));
													}),
												A2($elm$json$Json$Decode$field, 'intent', $elm$json$Json$Decode$value),
												A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$value),
												A2($elm$json$Json$Decode$field, 'effectProtocol', $elm$json$Json$Decode$value))),
										raw);
									if (_v46.$ === 'Ok') {
										var _v48 = _v46.a;
										var binding = _v48.a;
										var protocolId = _v48.b;
										var receipt = _v48.c;
										var receivedIntent = $elm$core$Result$toMaybe(
											A2(
												$elm$json$Json$Decode$decodeValue,
												A2($elm$json$Json$Decode$field, 'intent', $author$project$Effects$intentDecoder),
												raw));
										var exact = function (entry) {
											return _Utils_eq(entry.binding, binding) && (_Utils_eq(entry.protocol, protocolId) && _Utils_eq(
												$elm$core$Maybe$Just(entry.intent),
												receivedIntent));
										};
										var known = A2($elm$core$List$any, exact, model.issued);
										if (!known) {
											return _Utils_Tuple2(model, _List_Nil);
										} else {
											var retained = _Utils_eq(
												A2(
													$elm$json$Json$Decode$decodeValue,
													A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string),
													raw),
												$elm$core$Result$Ok('Unknown')) ? model.issued : A2(
												$elm$core$List$filter,
												A2($elm$core$Basics$composeR, exact, $elm$core$Basics$not),
												model.issued);
											var _v49 = A2($author$project$Effects$apply, receipt, model.effects);
											var effects = _v49.a;
											var error = _v49.c;
											if (!_Utils_eq(error, $elm$core$Maybe$Nothing)) {
												return _Utils_Tuple2(model, _List_Nil);
											} else {
												var current = function () {
													var _v50 = model.effects.transaction;
													if (_v50.$ === 'Nothing') {
														return false;
													} else {
														var transaction = _v50.a;
														return _Utils_eq(transaction.effectProtocol, protocolId) && _Utils_eq(
															$elm$core$Maybe$Just(transaction.intent),
															receivedIntent);
													}
												}();
												return ((!current) || (_Utils_eq(model.phase, $author$project$Shell$Detached) || (!_Utils_eq(
													model.binding,
													$elm$core$Maybe$Just(binding))))) ? _Utils_Tuple2(
													_Utils_update(
														model,
														{effects: effects, issued: retained}),
													_List_Nil) : $author$project$Shell$refreshObservations(
													_Utils_update(
														model,
														{effects: effects, issued: retained}));
											}
										}
									} else {
										return _Utils_Tuple2(model, _List_Nil);
									}
								}
							default:
								break _v12$13;
						}
					} else {
						break _v12$13;
					}
				}
				return _Utils_Tuple2(model, _List_Nil);
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
var $elm$core$Platform$worker = _Platform_worker;
var $author$project$TerminalProbe$main = $elm$core$Platform$worker(
	{
		init: function (_v0) {
			return _Utils_Tuple2(_Utils_Tuple0, $elm$core$Platform$Cmd$none);
		},
		subscriptions: function (_v1) {
			return $author$project$TerminalProbe$incoming($author$project$TerminalProbe$Run);
		},
		update: F2(
			function (_v2, _v3) {
				var raw = _v2.a;
				var decoded = A2(
					$elm$json$Json$Decode$decodeValue,
					A3(
						$elm$json$Json$Decode$map2,
						$elm$core$Tuple$pair,
						A2(
							$elm$json$Json$Decode$at,
							_List_fromArray(
								['request', 'binding']),
							$author$project$Binding$decoder),
						A2(
							$elm$json$Json$Decode$at,
							_List_fromArray(
								['request', 'requestId']),
							$author$project$UInt64$decoder)),
					raw);
				if (decoded.$ === 'Err') {
					return _Utils_Tuple2(
						_Utils_Tuple0,
						$author$project$TerminalProbe$outgoing($elm$json$Json$Encode$null));
				} else {
					var _v5 = decoded.a;
					var binding = _v5.a;
					var request = _v5.b;
					var notice = A2(
						$elm$core$Result$withDefault,
						$elm$json$Json$Encode$null,
						A2(
							$elm$json$Json$Decode$decodeValue,
							A2($elm$json$Json$Decode$field, 'frame', $elm$json$Json$Decode$value),
							raw));
					var current = A2(
						$elm$core$Result$withDefault,
						A2(
							$elm$core$Maybe$withDefault,
							request,
							$author$project$UInt64$next(request)),
						A2(
							$elm$json$Json$Decode$decodeValue,
							A2($elm$json$Json$Decode$field, 'counter', $author$project$UInt64$decoder),
							raw));
					var bool = function (name) {
						return A2(
							$elm$core$Result$withDefault,
							false,
							A2(
								$elm$json$Json$Decode$decodeValue,
								A2($elm$json$Json$Decode$field, name, $elm$json$Json$Decode$bool),
								raw));
					};
					var base = $author$project$Shell$initial;
					var pending = _Utils_update(
						base,
						{
							binding: $elm$core$Maybe$Just(binding),
							deferNotifications: bool('defer'),
							expected: $elm$core$Maybe$Just(request),
							geometryExpected: $elm$core$Maybe$Just(current),
							phase: $author$project$Shell$Reconciling,
							reconnecting: false,
							request: current,
							transportRefused: bool('transport')
						});
					var apply = F2(
						function (_v9, _v10) {
							var model = _v10.a;
							var count = _v10.b;
							var _v8 = A2(
								$author$project$Shell$update,
								$author$project$Shell$Incoming(notice),
								model);
							var next = _v8.a;
							var stepCommands = _v8.b;
							return _Utils_Tuple2(
								next,
								count + $elm$core$List$length(stepCommands));
						});
					var _v6 = A3(
						$elm$core$List$foldl,
						apply,
						_Utils_Tuple2(pending, 0),
						A2(
							$elm$core$List$range,
							1,
							A2(
								$elm$core$Result$withDefault,
								100,
								A2(
									$elm$json$Json$Decode$decodeValue,
									A2($elm$json$Json$Decode$field, 'repetitions', $elm$json$Json$Decode$int),
									raw))));
					var _final = _v6.a;
					var commands = _v6.b;
					return _Utils_Tuple2(
						_Utils_Tuple0,
						$author$project$TerminalProbe$outgoing(
							$elm$json$Json$Encode$object(
								_List_fromArray(
									[
										_Utils_Tuple2(
										'phase',
										$elm$json$Json$Encode$string(
											function () {
												var _v7 = _final.phase;
												switch (_v7.$) {
													case 'Detached':
														return 'detached';
													case 'Reconciling':
														return 'reconciling';
													case 'Ready':
														return 'ready';
													default:
														return 'exhausted';
												}
											}())),
										_Utils_Tuple2(
										'model',
										$author$project$Shell$encode(_final)),
										_Utils_Tuple2(
										'expected',
										A2(
											$elm$core$Maybe$withDefault,
											$elm$json$Json$Encode$null,
											A2(
												$elm$core$Maybe$map,
												A2($elm$core$Basics$composeR, $author$project$UInt64$string, $elm$json$Json$Encode$string),
												_final.expected))),
										_Utils_Tuple2(
										'geometryExpected',
										A2(
											$elm$core$Maybe$withDefault,
											$elm$json$Json$Encode$null,
											A2(
												$elm$core$Maybe$map,
												A2($elm$core$Basics$composeR, $author$project$UInt64$string, $elm$json$Json$Encode$string),
												_final.geometryExpected))),
										_Utils_Tuple2(
										'retry',
										$elm$json$Json$Encode$bool(_final.projectionRetryQueued)),
										_Utils_Tuple2(
										'effectsPreserved',
										$elm$json$Json$Encode$bool(
											_Utils_eq(_final.effects, pending.effects))),
										_Utils_Tuple2(
										'commands',
										$elm$json$Json$Encode$int(commands))
									]))));
				}
			})
	});
_Platform_export({'TerminalProbe':{'init':$author$project$TerminalProbe$main(
	$elm$json$Json$Decode$succeed(_Utils_Tuple0))(0)}});}(this));