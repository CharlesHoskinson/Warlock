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

var _Debug_log = F2(function(tag, value)
{
	return value;
});

var _Debug_log_UNUSED = F2(function(tag, value)
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

function _Debug_toString(value)
{
	return '<internals>';
}

function _Debug_toString_UNUSED(value)
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


function _Debug_crash(identifier)
{
	throw new Error('https://github.com/elm/core/blob/1.0.0/hints/' + identifier + '.md');
}


function _Debug_crash_UNUSED(identifier, fact1, fact2, fact3, fact4)
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
	if (region.bp.aO === region.bz.aO)
	{
		return 'on line ' + region.bp.aO;
	}
	return 'on lines ' + region.bp.aO + ' through ' + region.bz.aO;
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

	/**_UNUSED/
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

	/**/
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

	/**_UNUSED/
	if (x instanceof String)
	{
		var a = x.valueOf();
		var b = y.valueOf();
		return a === b ? 0 : a < b ? -1 : 1;
	}
	//*/

	/**/
	if (typeof x.$ === 'undefined')
	//*/
	/**_UNUSED/
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

var _Utils_Tuple0 = 0;
var _Utils_Tuple0_UNUSED = { $: '#0' };

function _Utils_Tuple2(a, b) { return { a: a, b: b }; }
function _Utils_Tuple2_UNUSED(a, b) { return { $: '#2', a: a, b: b }; }

function _Utils_Tuple3(a, b, c) { return { a: a, b: b, c: c }; }
function _Utils_Tuple3_UNUSED(a, b, c) { return { $: '#3', a: a, b: b, c: c }; }

function _Utils_chr(c) { return c; }
function _Utils_chr_UNUSED(c) { return new String(c); }


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



var _List_Nil = { $: 0 };
var _List_Nil_UNUSED = { $: '[]' };

function _List_Cons(hd, tl) { return { $: 1, a: hd, b: tl }; }
function _List_Cons_UNUSED(hd, tl) { return { $: '::', a: hd, b: tl }; }


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



/**_UNUSED/
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

function _Json_wrap_UNUSED(value) { return { $: 0, a: value }; }
function _Json_unwrap_UNUSED(value) { return value.a; }

function _Json_wrap(value) { return value; }
function _Json_unwrap(value) { return value; }

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
		impl.cE,
		impl.cR,
		impl.cQ,
		function() { return function() {} }
	);
});



// INITIALIZE A PROGRAM


function _Platform_initialize(flagDecoder, args, init, update, subscriptions, stepperBuilder)
{
	var result = A2(_Json_run, flagDecoder, _Json_wrap(args ? args['flags'] : undefined));
	$elm$core$Result$isOk(result) || _Debug_crash(2 /**_UNUSED/, _Json_errorToString(result.a) /**/);
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


function _Platform_export(exports)
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


function _Platform_export_UNUSED(exports)
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
				if (!node.$) {
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
			if (t.$ === -2) {
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
	var dict = _v0;
	return $elm$core$Dict$keys(dict);
};
var $elm$core$Basics$EQ = 1;
var $elm$core$Basics$GT = 2;
var $elm$core$Basics$LT = 0;
var $elm$core$Basics$identity = function (x) {
	return x;
};
var $author$project$MenuSurfaceReplay$Run = $elm$core$Basics$identity;
var $elm$core$Basics$apR = F2(
	function (x, f) {
		return f(x);
	});
var $author$project$Desktop$ChoiceDeadline = function (a) {
	return {$: 8, a: a};
};
var $elm$core$Basics$False = 1;
var $author$project$Shell$GeometryAttach = {$: 4};
var $author$project$Shell$GeometryRefresh = {$: 5};
var $author$project$Desktop$Incoming = function (a) {
	return {$: 3, a: a};
};
var $author$project$SurfaceController$Interaction = function (a) {
	return {$: 0, a: a};
};
var $elm$core$Maybe$Just = function (a) {
	return {$: 0, a: a};
};
var $author$project$TaskbarShell$Native = function (a) {
	return {$: 0, a: a};
};
var $author$project$SurfaceController$NativeDismiss = function (a) {
	return {$: 2, a: a};
};
var $author$project$SurfaceController$NativeReflow = function (a) {
	return {$: 3, a: a};
};
var $elm$core$Maybe$Nothing = {$: 1};
var $author$project$Desktop$OpenApplications = function (a) {
	return {$: 4, a: a};
};
var $author$project$Desktop$OwnerScope = function (a) {
	return {$: 2, a: a};
};
var $author$project$SurfaceController$Renderer = function (a) {
	return {$: 1, a: a};
};
var $elm$core$Basics$True = 0;
var $author$project$Desktop$Window = function (a) {
	return {$: 0, a: a};
};
var $elm$core$Result$Err = function (a) {
	return {$: 1, a: a};
};
var $elm$json$Json$Decode$Failure = F2(
	function (a, b) {
		return {$: 3, a: a, b: b};
	});
var $elm$json$Json$Decode$Field = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $elm$json$Json$Decode$Index = F2(
	function (a, b) {
		return {$: 1, a: a, b: b};
	});
var $elm$core$Result$Ok = function (a) {
	return {$: 0, a: a};
};
var $elm$json$Json$Decode$OneOf = function (a) {
	return {$: 2, a: a};
};
var $elm$core$Basics$add = _Basics_add;
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
				case 0:
					var f = error.a;
					var err = error.b;
					var isSimple = function () {
						var _v1 = $elm$core$String$uncons(f);
						if (_v1.$ === 1) {
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
				case 1:
					var i = error.a;
					var err = error.b;
					var indexName = '[' + ($elm$core$String$fromInt(i) + ']');
					var $temp$error = err,
						$temp$context = A2($elm$core$List$cons, indexName, context);
					error = $temp$error;
					context = $temp$context;
					continue errorToStringHelp;
				case 2:
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
		return {$: 0, a: a, b: b, c: c, d: d};
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
	return {$: 1, a: a};
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
	return {$: 0, a: a};
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
		if (!builder.e) {
			return A4(
				$elm$core$Array$Array_elm_builtin,
				$elm$core$Elm$JsArray$length(builder.g),
				$elm$core$Array$shiftStep,
				$elm$core$Elm$JsArray$empty,
				builder.g);
		} else {
			var treeLen = builder.e * $elm$core$Array$branchFactor;
			var depth = $elm$core$Basics$floor(
				A2($elm$core$Basics$logBase, $elm$core$Array$branchFactor, treeLen - 1));
			var correctNodeList = reverseNodeList ? $elm$core$List$reverse(builder.i) : builder.i;
			var tree = A2($elm$core$Array$treeFromBuilder, correctNodeList, builder.e);
			return A4(
				$elm$core$Array$Array_elm_builtin,
				$elm$core$Elm$JsArray$length(builder.g) + treeLen,
				A2($elm$core$Basics$max, 5, depth * $elm$core$Array$shiftStep),
				tree,
				builder.g);
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
					{i: nodeList, e: (len / $elm$core$Array$branchFactor) | 0, g: tail});
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
var $elm$core$Result$isOk = function (result) {
	if (!result.$) {
		return true;
	} else {
		return false;
	}
};
var $elm$json$Json$Encode$bool = _Json_wrap;
var $author$project$Desktop$ViewStamp = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $elm$core$Maybe$map = F2(
	function (f, maybe) {
		if (!maybe.$) {
			var value = maybe.a;
			return $elm$core$Maybe$Just(
				f(value));
		} else {
			return $elm$core$Maybe$Nothing;
		}
	});
var $author$project$Desktop$capture = function (model) {
	return A2(
		$elm$core$Maybe$map,
		$author$project$Desktop$ViewStamp(model.a.b.c),
		model.X);
};
var $author$project$Desktop$choiceToken = function (model) {
	return A2(
		$elm$core$Maybe$map,
		function ($) {
			return $.ba;
		},
		model.s);
};
var $elm$core$Basics$composeR = F3(
	function (f, g, x) {
		return g(
			f(x));
	});
var $author$project$MenuBridge$currentProvider = function (_v0) {
	var state = _v0;
	return A2(
		$elm$core$Maybe$map,
		function ($) {
			return $.aw;
		},
		state.at);
};
var $author$project$SurfaceRenderer$Snapshot = $elm$core$Basics$identity;
var $elm$core$Result$andThen = F2(
	function (callback, result) {
		if (!result.$) {
			var value = result.a;
			return callback(value);
		} else {
			var msg = result.a;
			return $elm$core$Result$Err(msg);
		}
	});
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
var $elm$json$Json$Decode$andThen = _Json_andThen;
var $elm$core$String$any = _String_any;
var $elm$json$Json$Decode$fail = _Json_fail;
var $elm$core$String$length = _String_length;
var $elm$core$Basics$not = _Basics_not;
var $elm$json$Json$Decode$string = _Json_decodeString;
var $elm$json$Json$Decode$succeed = _Json_succeed;
var $author$project$SurfaceRenderer$bounded = function (limit) {
	return A2(
		$elm$json$Json$Decode$andThen,
		function (value) {
			return ((_Utils_cmp(
				$elm$core$String$length(value),
				limit) < 1) && (!A2(
				$elm$core$String$any,
				function (c) {
					return $elm$core$Char$toCode(c) < 32;
				},
				value))) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Presentation text');
		},
		$elm$json$Json$Decode$string);
};
var $author$project$SurfaceRenderer$Control = F6(
	function (identity, domId, label, ariaLabel, detail, enabled) {
		return {o: ariaLabel, p: detail, q: domId, aF: enabled, bK: identity, bP: label};
	});
var $elm$json$Json$Decode$bool = _Json_decodeBool;
var $elm$json$Json$Decode$field = _Json_decodeField;
var $elm$json$Json$Decode$list = _Json_decodeList;
var $elm$json$Json$Decode$map6 = _Json_map6;
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
var $elm$core$List$sortBy = _List_sortBy;
var $elm$core$List$sort = function (xs) {
	return A2($elm$core$List$sortBy, $elm$core$Basics$identity, xs);
};
var $elm$json$Json$Decode$value = _Json_decodeValue;
var $author$project$SurfaceRenderer$strict = F2(
	function (names, decoder) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (fields) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, fields)),
					$elm$core$List$sort(names)) ? decoder : $elm$json$Json$Decode$fail('Presentation fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$SurfaceRenderer$controls = function (maximum) {
	return A2(
		$elm$json$Json$Decode$andThen,
		function (values) {
			return (_Utils_cmp(
				$elm$core$List$length(values),
				maximum) > 0) ? $elm$json$Json$Decode$fail('Presentation capacity') : $elm$json$Json$Decode$list(
				A2(
					$author$project$SurfaceRenderer$strict,
					_List_fromArray(
						['id', 'domId', 'label', 'ariaLabel', 'detail', 'enabled']),
					A7(
						$elm$json$Json$Decode$map6,
						$author$project$SurfaceRenderer$Control,
						A2(
							$elm$json$Json$Decode$field,
							'id',
							$author$project$SurfaceRenderer$bounded(512)),
						A2(
							$elm$json$Json$Decode$field,
							'domId',
							$author$project$SurfaceRenderer$bounded(1024)),
						A2(
							$elm$json$Json$Decode$field,
							'label',
							$author$project$SurfaceRenderer$bounded(1024)),
						A2(
							$elm$json$Json$Decode$field,
							'ariaLabel',
							$author$project$SurfaceRenderer$bounded(1024)),
						A2(
							$elm$json$Json$Decode$field,
							'detail',
							$author$project$SurfaceRenderer$bounded(128)),
						A2($elm$json$Json$Decode$field, 'enabled', $elm$json$Json$Decode$bool))));
		},
		$elm$json$Json$Decode$list($elm$json$Json$Decode$value));
};
var $elm$json$Json$Decode$decodeValue = _Json_run;
var $author$project$UInt64$Counter = $elm$core$Basics$identity;
var $elm$core$Basics$ge = _Utils_ge;
var $elm$core$String$isEmpty = function (string) {
	return string === '';
};
var $elm$core$String$startsWith = _String_startsWith;
var $author$project$UInt64$decoder = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return ((!$elm$core$String$isEmpty(value)) && (A2(
			$elm$core$String$all,
			function (c) {
				return (c >= '0') && (c <= '9');
			},
			value) && (((value === '0') || (!A2($elm$core$String$startsWith, '0', value))) && (($elm$core$String$length(value) <= 20) && (($elm$core$String$length(value) < 20) || (value <= '18446744073709551615')))))) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Expected canonical uint64 string');
	},
	$elm$json$Json$Decode$string);
var $elm$core$Set$Set_elm_builtin = $elm$core$Basics$identity;
var $elm$core$Dict$RBEmpty_elm_builtin = {$: -2};
var $elm$core$Dict$empty = $elm$core$Dict$RBEmpty_elm_builtin;
var $elm$core$Set$empty = $elm$core$Dict$empty;
var $elm$core$Dict$Black = 1;
var $elm$core$Dict$RBNode_elm_builtin = F5(
	function (a, b, c, d, e) {
		return {$: -1, a: a, b: b, c: c, d: d, e: e};
	});
var $elm$core$Dict$Red = 0;
var $elm$core$Dict$balance = F5(
	function (color, key, value, left, right) {
		if ((right.$ === -1) && (!right.a)) {
			var _v1 = right.a;
			var rK = right.b;
			var rV = right.c;
			var rLeft = right.d;
			var rRight = right.e;
			if ((left.$ === -1) && (!left.a)) {
				var _v3 = left.a;
				var lK = left.b;
				var lV = left.c;
				var lLeft = left.d;
				var lRight = left.e;
				return A5(
					$elm$core$Dict$RBNode_elm_builtin,
					0,
					key,
					value,
					A5($elm$core$Dict$RBNode_elm_builtin, 1, lK, lV, lLeft, lRight),
					A5($elm$core$Dict$RBNode_elm_builtin, 1, rK, rV, rLeft, rRight));
			} else {
				return A5(
					$elm$core$Dict$RBNode_elm_builtin,
					color,
					rK,
					rV,
					A5($elm$core$Dict$RBNode_elm_builtin, 0, key, value, left, rLeft),
					rRight);
			}
		} else {
			if ((((left.$ === -1) && (!left.a)) && (left.d.$ === -1)) && (!left.d.a)) {
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
					0,
					lK,
					lV,
					A5($elm$core$Dict$RBNode_elm_builtin, 1, llK, llV, llLeft, llRight),
					A5($elm$core$Dict$RBNode_elm_builtin, 1, key, value, lRight, right));
			} else {
				return A5($elm$core$Dict$RBNode_elm_builtin, color, key, value, left, right);
			}
		}
	});
var $elm$core$Basics$compare = _Utils_compare;
var $elm$core$Dict$insertHelp = F3(
	function (key, value, dict) {
		if (dict.$ === -2) {
			return A5($elm$core$Dict$RBNode_elm_builtin, 0, key, value, $elm$core$Dict$RBEmpty_elm_builtin, $elm$core$Dict$RBEmpty_elm_builtin);
		} else {
			var nColor = dict.a;
			var nKey = dict.b;
			var nValue = dict.c;
			var nLeft = dict.d;
			var nRight = dict.e;
			var _v1 = A2($elm$core$Basics$compare, key, nKey);
			switch (_v1) {
				case 0:
					return A5(
						$elm$core$Dict$balance,
						nColor,
						nKey,
						nValue,
						A3($elm$core$Dict$insertHelp, key, value, nLeft),
						nRight);
				case 1:
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
		if ((_v0.$ === -1) && (!_v0.a)) {
			var _v1 = _v0.a;
			var k = _v0.b;
			var v = _v0.c;
			var l = _v0.d;
			var r = _v0.e;
			return A5($elm$core$Dict$RBNode_elm_builtin, 1, k, v, l, r);
		} else {
			var x = _v0;
			return x;
		}
	});
var $elm$core$Set$insert = F2(
	function (key, _v0) {
		var dict = _v0;
		return A3($elm$core$Dict$insert, key, 0, dict);
	});
var $elm$core$Set$fromList = function (list) {
	return A3($elm$core$List$foldl, $elm$core$Set$insert, $elm$core$Set$empty, list);
};
var $elm$json$Json$Decode$int = _Json_decodeInt;
var $elm$core$List$isEmpty = function (xs) {
	if (!xs.b) {
		return true;
	} else {
		return false;
	}
};
var $elm$json$Json$Decode$map7 = _Json_map7;
var $elm$core$Result$mapError = F2(
	function (f, result) {
		if (!result.$) {
			var v = result.a;
			return $elm$core$Result$Ok(v);
		} else {
			var e = result.a;
			return $elm$core$Result$Err(
				f(e));
		}
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
var $elm$core$Basics$neq = _Utils_notEqual;
var $elm$core$Dict$sizeHelp = F2(
	function (n, dict) {
		sizeHelp:
		while (true) {
			if (dict.$ === -2) {
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
	var dict = _v0;
	return $elm$core$Dict$size(dict);
};
var $author$project$UInt64$zero = '0';
var $author$project$SurfaceRenderer$decode = function (raw) {
	var decoder = A2(
		$author$project$SurfaceRenderer$strict,
		_List_fromArray(
			['surfaceProtocol', 'publication', 'lease', 'mode', 'status', 'bar', 'popup']),
		A8(
			$elm$json$Json$Decode$map7,
			F7(
				function (version, shown, scoped, current, notice, bar, popup) {
					return {al: bar, aD: current, n: notice, af: popup, b4: scoped, b6: shown, ca: version};
				}),
			A2($elm$json$Json$Decode$field, 'surfaceProtocol', $elm$json$Json$Decode$int),
			A2($elm$json$Json$Decode$field, 'publication', $author$project$UInt64$decoder),
			A2($elm$json$Json$Decode$field, 'lease', $author$project$UInt64$decoder),
			A2(
				$elm$json$Json$Decode$field,
				'mode',
				$author$project$SurfaceRenderer$bounded(16)),
			A2(
				$elm$json$Json$Decode$field,
				'status',
				$author$project$SurfaceRenderer$bounded(1024)),
			A2(
				$elm$json$Json$Decode$field,
				'bar',
				$author$project$SurfaceRenderer$controls(257)),
			A2(
				$elm$json$Json$Decode$field,
				'popup',
				$author$project$SurfaceRenderer$controls(2051))));
	return A2(
		$elm$core$Result$andThen,
		function (record) {
			var unique = function (names) {
				return _Utils_eq(
					$elm$core$List$length(names),
					$elm$core$Set$size(
						$elm$core$Set$fromList(names)));
			};
			var all = _Utils_ap(record.al, record.af);
			var identities = A2(
				$elm$core$List$map,
				function ($) {
					return $.bK;
				},
				all);
			return ((record.ca !== 2) || (_Utils_eq(record.b6, $author$project$UInt64$zero) || ((!A2(
				$elm$core$List$member,
				record.aD,
				_List_fromArray(
					['closed', 'picker', 'applications', 'menu']))) || (((record.aD !== 'closed') && _Utils_eq(record.b4, $author$project$UInt64$zero)) || (((record.aD === 'closed') && (!$elm$core$List$isEmpty(record.af))) || ((!unique(identities)) || ((!unique(
				A2(
					$elm$core$List$map,
					function ($) {
						return $.q;
					},
					all))) || A2(
				$elm$core$List$any,
				function (control) {
					return $elm$core$String$isEmpty(control.bK) || $elm$core$String$isEmpty(control.q);
				},
				all)))))))) ? $elm$core$Result$Err('Invalid presentation scope/identities') : $elm$core$Result$Ok(
				{al: record.al, I: record.b4, U: record.aD, af: record.af, ag: record.b6, x: record.n});
		},
		A2(
			$elm$core$Result$mapError,
			$elm$json$Json$Decode$errorToString,
			A2($elm$json$Json$Decode$decodeValue, decoder, raw)));
};
var $author$project$SurfaceController$desktop = function (_v0) {
	var model = _v0;
	return model.h;
};
var $author$project$Shell$Ready = 2;
var $author$project$Effects$Pending = 0;
var $elm$core$Maybe$withDefault = F2(
	function (_default, maybe) {
		if (!maybe.$) {
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
				return !transaction.x;
			},
			model.r));
};
var $author$project$Shell$available = function (model) {
	return (model.aU === 2) && ((!$author$project$Effects$pending(model.aE)) && (_Utils_eq(model.cy, $elm$core$Maybe$Nothing) && ((!A2(
		$elm$core$Maybe$withDefault,
		false,
		A2(
			$elm$core$Maybe$map,
			function ($) {
				return $.aE;
			},
			model.cz))) || (_Utils_eq(model.cA, $elm$core$Maybe$Nothing) && (!_Utils_eq(model.bG, $elm$core$Maybe$Nothing))))));
};
var $elm$json$Json$Encode$string = _Json_wrap;
var $author$project$UInt64$string = function (_v0) {
	var value = _v0;
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
			_Json_emptyObject(0),
			pairs));
};
var $author$project$Effects$encodeContext = function (context) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'lifetime',
				$author$project$Effects$counter(context.cF)),
				_Utils_Tuple2(
				'epoch',
				$author$project$Effects$counter(context.a4)),
				_Utils_Tuple2(
				'output',
				$author$project$Effects$counter(context.v)),
				_Utils_Tuple2(
				'revision',
				$author$project$Effects$counter(context.cP))
			]));
};
var $author$project$Effects$operationName = function (operation) {
	switch (operation) {
		case 0:
			return 'minimize';
		case 1:
			return 'restore';
		case 2:
			return 'activate';
		case 3:
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
				$author$project$Effects$counter(intent.a6)),
				_Utils_Tuple2(
				'generation',
				$author$project$Effects$counter(intent.cx)),
				_Utils_Tuple2(
				'incarnation',
				$author$project$Effects$counter(intent.A)),
				_Utils_Tuple2(
				'operation',
				$elm$json$Json$Encode$string(
					$author$project$Effects$operationName(intent.ar))),
				_Utils_Tuple2(
				'context',
				$author$project$Effects$encodeContext(intent.am))
			]));
};
var $elm$json$Json$Encode$list = F2(
	function (func, entries) {
		return _Json_wrap(
			A3(
				$elm$core$List$foldl,
				_Json_addEntry(func),
				_Json_emptyArray(0),
				entries));
	});
var $elm$json$Json$Encode$null = _Json_encodeNull;
var $author$project$Effects$statusName = function (status) {
	switch (status) {
		case 0:
			return 'Pending';
		case 1:
			return 'Committed';
		case 2:
			return 'Refused';
		case 3:
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
								return $.N;
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
													$author$project$Effects$counter(w.A)),
													_Utils_Tuple2(
													'minimized',
													$elm$json$Json$Encode$bool(w.aq))
												]));
									}))),
						model.aS))),
				_Utils_Tuple2(
				'connected',
				$elm$json$Json$Encode$bool(model.R)),
				_Utils_Tuple2(
				'request',
				$author$project$Effects$counter(model.a6)),
				_Utils_Tuple2(
				'generation',
				$author$project$Effects$counter(model.cx)),
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
										$author$project$Effects$encodeIntent(transaction.G)),
										_Utils_Tuple2(
										'status',
										$elm$json$Json$Encode$string(
											$author$project$Effects$statusName(transaction.x)))
									]));
						},
						model.r)))
			]));
};
var $author$project$Shell$recoveryNotice = function (failure) {
	switch (failure) {
		case 0:
			return 'Window recovery data is unavailable. Restore access, then reconnect.';
		case 1:
			return 'Window recovery storage is full. Free space, then reconnect.';
		case 2:
			return 'Another shell is using window recovery data. Close it, then reconnect.';
		case 3:
			return 'Window recovery data could not be verified. Repair it, then reconnect.';
		default:
			return 'Previous window recovery data has no verified owner. Complete migration, then reconnect.';
	}
};
var $author$project$Shell$status = function (model) {
	var _v0 = A2(
		$elm$core$Maybe$map,
		function ($) {
			return $.x;
		},
		model.aE.r);
	_v0$3:
	while (true) {
		if (!_v0.$) {
			switch (_v0.a) {
				case 0:
					var _v1 = _v0.a;
					return 'Applying window change…';
				case 4:
					var _v2 = _v0.a;
					return model.n + ' The last request could not be confirmed.';
				case 2:
					var _v3 = _v0.a;
					return model.n + ' The window change was refused.';
				default:
					break _v0$3;
			}
		} else {
			break _v0$3;
		}
	}
	return model.n;
};
var $author$project$Shell$encode = function (model) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'phase',
				$elm$json$Json$Encode$string(
					function () {
						var _v0 = model.aU;
						switch (_v0) {
							case 0:
								return 'Detached';
							case 1:
								return 'Reconciling';
							case 2:
								return 'Ready';
							default:
								return 'Exhausted';
						}
					}())),
				_Utils_Tuple2(
				'notificationQueued',
				$elm$json$Json$Encode$bool(model.ad)),
				_Utils_Tuple2(
				'request',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(model.a6))),
				_Utils_Tuple2(
				'available',
				$elm$json$Json$Encode$bool(
					$author$project$Shell$available(model))),
				_Utils_Tuple2(
				'reconnecting',
				$elm$json$Json$Encode$bool(model.Y)),
				_Utils_Tuple2(
				'effects',
				$author$project$Effects$encode(model.aE)),
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
						model.au)))
			]));
};
var $elm$core$List$maybeCons = F3(
	function (f, mx, xs) {
		var _v0 = f(mx);
		if (!_v0.$) {
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
var $author$project$Shell$Detached = 0;
var $author$project$TaskbarShell$Primary = F2(
	function (a, b) {
		return {$: 1, a: a, b: b};
	});
var $author$project$Shell$Reconnect = {$: 2};
var $author$project$Desktop$RetryWindows = {$: 9};
var $author$project$Taskbar$Unavailable = {$: 3};
var $author$project$Shell$Stamp = F3(
	function (a, b, c) {
		return {$: 0, a: a, b: b, c: c};
	});
var $author$project$Binding$matchesContext = F3(
	function (life, epoch, _v0) {
		var lifetime = _v0.a;
		var frontend = _v0.c;
		return _Utils_eq(life, lifetime) && _Utils_eq(epoch, frontend);
	});
var $author$project$Shell$capture = function (model) {
	var _v0 = _Utils_Tuple2(model.c, model.aE.aS);
	if ((!_v0.a.$) && (!_v0.b.$)) {
		var binding = _v0.a.a;
		var observed = _v0.b.a;
		return A3($author$project$Binding$matchesContext, observed.am.cF, observed.am.a4, binding) ? $elm$core$Maybe$Just(
			A3($author$project$Shell$Stamp, binding, observed.am.v, observed.am.cP)) : $elm$core$Maybe$Nothing;
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
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
var $elm$core$Maybe$andThen = F2(
	function (callback, maybeValue) {
		if (!maybeValue.$) {
			var value = maybeValue.a;
			return callback(value);
		} else {
			return $elm$core$Maybe$Nothing;
		}
	});
var $author$project$UInt64$compare = F2(
	function (_v0, _v1) {
		var left = _v0;
		var right = _v1;
		var _v2 = A2(
			$elm$core$Basics$compare,
			$elm$core$String$length(left),
			$elm$core$String$length(right));
		if (_v2 === 1) {
			return A2($elm$core$Basics$compare, left, right);
		} else {
			var order = _v2;
			return order;
		}
	});
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
var $author$project$ActionProjection$focused = function (_v0) {
	var focus = _v0.b;
	return focus;
};
var $elm$core$Dict$get = F2(
	function (targetKey, dict) {
		get:
		while (true) {
			if (dict.$ === -2) {
				return $elm$core$Maybe$Nothing;
			} else {
				var key = dict.b;
				var value = dict.c;
				var left = dict.d;
				var right = dict.e;
				var _v1 = A2($elm$core$Basics$compare, targetKey, key);
				switch (_v1) {
					case 0:
						var $temp$targetKey = targetKey,
							$temp$dict = left;
						targetKey = $temp$targetKey;
						dict = $temp$dict;
						continue get;
					case 1:
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
var $elm$core$List$sortWith = _List_sortWith;
var $author$project$Taskbar$groups = function (projection) {
	var rows = $author$project$ActionProjection$windows(projection);
	var add = F2(
		function (_v0, accumulated) {
			var key = _v0.a;
			var entry = _v0.b;
			return A2(
				$elm$core$List$any,
				function (g) {
					return _Utils_eq(g.t, key);
				},
				accumulated) ? A2(
				$elm$core$List$map,
				function (g) {
					return _Utils_eq(g.t, key) ? _Utils_update(
						g,
						{
							aH: _Utils_ap(
								g.aH,
								_List_fromArray(
									[entry]))
						}) : g;
				},
				accumulated) : _Utils_ap(
				accumulated,
				_List_fromArray(
					[
						{
						aH: _List_fromArray(
							[entry]),
						t: key
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
					A2($author$project$ActionProjection$rootOf, w.A, projection),
					$elm$core$Maybe$Just(root.A));
			},
			rows);
		var key = $elm$core$String$isEmpty(root.bb) ? ('window:' + $author$project$UInt64$string(root.A)) : ('application:' + root.bb);
		return _Utils_Tuple2(
			key,
			{
				a2: _Utils_eq(
					activeRoot,
					$elm$core$Maybe$Just(root.A)),
				bb: root.bb,
				bc: A2(
					$elm$core$List$all,
					function ($) {
						return $.bc;
					},
					members),
				bP: root.bP,
				aq: root.aq,
				ai: root.A
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
						return A2($author$project$UInt64$compare, a.A, b.A);
					}),
				A2(
					$elm$core$List$filter,
					function (w) {
						return _Utils_eq(w.bj, $elm$core$Maybe$Nothing);
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
					return $.N;
				},
				$author$project$Taskbar$groups),
			model.b.aE.aS));
};
var $elm$core$List$head = function (list) {
	if (list.b) {
		var x = list.a;
		var xs = list.b;
		return $elm$core$Maybe$Just(x);
	} else {
		return $elm$core$Maybe$Nothing;
	}
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
var $author$project$Desktop$host = function (binding) {
	return A2(
		$elm$json$Json$Encode$encode,
		0,
		$author$project$Binding$encode(binding));
};
var $author$project$Desktop$key = F2(
	function (model, suffix) {
		return 'applications:' + (A2(
			$elm$core$Maybe$withDefault,
			'detached',
			A2($elm$core$Maybe$map, $author$project$Desktop$host, model.a.b.c)) + (':' + (A2(
			$elm$core$Maybe$withDefault,
			'exhausted',
			A2($elm$core$Maybe$map, $author$project$UInt64$string, model.X)) + (':' + suffix))));
	});
var $author$project$Effects$Activate = 2;
var $author$project$Taskbar$Apply = F2(
	function (a, b) {
		return {$: 2, a: a, b: b};
	});
var $author$project$Taskbar$Launch = {$: 0};
var $author$project$Effects$Minimize = 0;
var $author$project$Taskbar$Picker = {$: 1};
var $author$project$Effects$Restore = 1;
var $author$project$Taskbar$primary = F2(
	function (pinned, families) {
		if (!families.b) {
			return pinned ? $author$project$Taskbar$Launch : $author$project$Taskbar$Unavailable;
		} else {
			if (!families.b.b) {
				var entry = families.a;
				return (!entry.bc) ? $author$project$Taskbar$Unavailable : (entry.aq ? A2($author$project$Taskbar$Apply, 1, entry.ai) : (entry.a2 ? A2($author$project$Taskbar$Apply, 0, entry.ai) : A2($author$project$Taskbar$Apply, 2, entry.ai)));
			} else {
				return $author$project$Taskbar$Picker;
			}
		}
	});
var $author$project$Shell$stampKey = function (_v0) {
	var binding = _v0.a;
	var output = _v0.b;
	var revision = _v0.c;
	return A2(
		$elm$json$Json$Encode$encode,
		0,
		$author$project$Binding$encode(binding)) + (':' + ($author$project$UInt64$string(output) + (':' + $author$project$UInt64$string(revision))));
};
var $author$project$Surface$barControls = function (model) {
	var retry = {
		o: 'Refresh windows',
		p: '',
		q: A2($author$project$Desktop$key, model, 'refresh-windows'),
		aF: _Utils_eq(model.s, $elm$core$Maybe$Nothing),
		bJ: 'bar:refresh-windows',
		bP: 'Refresh windows',
		m: $elm$core$Maybe$Just($author$project$Desktop$RetryWindows)
	};
	var reconnect = {
		o: 'Reconnect to the window system',
		p: '',
		q: 'reconnect',
		aF: !model.a.b.Y,
		bJ: 'bar:reconnect',
		bP: 'Reconnect',
		m: $elm$core$Maybe$Just(
			$author$project$Desktop$Window(
				$author$project$TaskbarShell$Native($author$project$Shell$Reconnect)))
	};
	var groupControl = function (group) {
		var scoped = $author$project$Shell$capture(model.a.b);
		var ready = $author$project$Shell$available(model.a.b) && (!_Utils_eq(
			A2($author$project$Taskbar$primary, false, group.aH),
			$author$project$Taskbar$Unavailable));
		var operation = function () {
			var _v0 = A2($author$project$Taskbar$primary, false, group.aH);
			_v0$4:
			while (true) {
				switch (_v0.$) {
					case 2:
						switch (_v0.a) {
							case 0:
								var _v1 = _v0.a;
								return 'Minimize ';
							case 1:
								var _v2 = _v0.a;
								return 'Restore ';
							case 2:
								var _v3 = _v0.a;
								return 'Activate ';
							default:
								break _v0$4;
						}
					case 1:
						return 'Choose a window from ';
					default:
						break _v0$4;
				}
			}
			return 'Unavailable ';
		}();
		var label = A2(
			$elm$core$Maybe$withDefault,
			'Windows',
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.bP;
				},
				$elm$core$List$head(group.aH)));
		return {
			o: _Utils_ap(operation, label),
			p: $elm$core$String$fromInt(
				$elm$core$List$length(group.aH)),
			q: A2(
				$elm$core$Maybe$withDefault,
				'detached-group',
				A2(
					$elm$core$Maybe$map,
					function (stamp) {
						return 'group:' + ($author$project$Shell$stampKey(stamp) + (':' + group.t));
					},
					scoped)),
			aF: ready,
			bJ: 'bar:group:' + group.t,
			bP: label,
			m: ready ? A2(
				$elm$core$Maybe$map,
				function (stamp) {
					return $author$project$Desktop$Window(
						A2($author$project$TaskbarShell$Primary, stamp, group.t));
				},
				scoped) : $elm$core$Maybe$Nothing
		};
	};
	var application = {
		o: 'Open applications',
		p: '',
		q: A2($author$project$Desktop$key, model, 'control:opener'),
		aF: !(!model.a.b.aU),
		bJ: 'bar:applications',
		bP: 'Applications',
		m: A2(
			$elm$core$Maybe$map,
			$author$project$Desktop$OpenApplications,
			$author$project$Desktop$capture(model))
	};
	return A2(
		$elm$core$List$cons,
		(!model.a.b.aU) ? reconnect : application,
		_Utils_ap(
			A2(
				$elm$core$List$map,
				groupControl,
				$author$project$TaskbarShell$groups(model.a)),
			((!$elm$core$String$isEmpty(model.E)) && (!(!model.a.b.aU))) ? _List_fromArray(
				[retry]) : _List_Nil));
};
var $author$project$Desktop$Acknowledge = function (a) {
	return {$: 10, a: a};
};
var $author$project$Menu$Activate = F3(
	function (a, b, c) {
		return {$: 3, a: a, b: b, c: c};
	});
var $author$project$TaskbarShell$Choose = F3(
	function (a, b, c) {
		return {$: 2, a: a, b: b, c: c};
	});
var $author$project$TaskbarShell$Close = F2(
	function (a, b) {
		return {$: 3, a: a, b: b};
	});
var $author$project$Desktop$CloseApplications = function (a) {
	return {$: 5, a: a};
};
var $author$project$Menu$Dismiss = function (a) {
	return {$: 5, a: a};
};
var $author$project$TaskbarShell$MenuEvent = function (a) {
	return {$: 5, a: a};
};
var $author$project$Menu$Ready = {$: 0};
var $author$project$Desktop$Start = function (a) {
	return {$: 6, a: a};
};
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
var $elm$core$Dict$values = function (dict) {
	return A3(
		$elm$core$Dict$foldr,
		F3(
			function (key, value, valueList) {
				return A2($elm$core$List$cons, value, valueList);
			}),
		_List_Nil,
		dict);
};
var $author$project$Catalog$entries = function (_v0) {
	var values = _v0.c;
	return $elm$core$Dict$values(values);
};
var $author$project$Catalog$id = function (_v0) {
	var value = _v0;
	return value;
};
var $author$project$Menu$menuNumber = function (_v0) {
	var number = _v0;
	return number;
};
var $author$project$Menu$snapshot = function (_v0) {
	var state = _v0;
	return {
		F: state.F,
		bM: $elm$core$List$length(state.T),
		aN: state.aN,
		ap: state.ap,
		j: $elm$core$List$length(state.j),
		b3: $elm$core$List$length(state.Z)
	};
};
var $author$project$MenuBridge$menuSnapshot = function (_v0) {
	var state = _v0;
	return $author$project$Menu$snapshot(state.ap);
};
var $author$project$Launch$Selection = F5(
	function (a, b, c, d, e) {
		return {$: 0, a: a, b: b, c: c, d: d, e: e};
	});
var $author$project$Launch$identityFunction = function (value) {
	return value;
};
var $author$project$Catalog$lookup = F2(
	function (value, _v0) {
		var values = _v0.c;
		return A2($elm$core$Dict$get, value, values);
	});
var $elm$core$Maybe$map2 = F3(
	function (func, ma, mb) {
		if (ma.$ === 1) {
			return $elm$core$Maybe$Nothing;
		} else {
			var a = ma.a;
			if (mb.$ === 1) {
				return $elm$core$Maybe$Nothing;
			} else {
				var b = mb.a;
				return $elm$core$Maybe$Just(
					A2(func, a, b));
			}
		}
	});
var $author$project$Catalog$scope = function (_v0) {
	var lifetime = _v0.a;
	var generation = _v0.b;
	return {cx: generation, cF: lifetime};
};
var $author$project$Launch$select = F2(
	function (identity, _v0) {
		var model = _v0;
		return A2(
			$elm$core$Maybe$andThen,
			$author$project$Launch$identityFunction,
			A3(
				$elm$core$Maybe$map2,
				F2(
					function (host, snapshot) {
						return A2(
							$elm$core$Maybe$map,
							function (entry) {
								var scope = $author$project$Catalog$scope(snapshot);
								return A5($author$project$Launch$Selection, host, model.cP, scope.cF, scope.cx, entry.bK);
							},
							A2($author$project$Catalog$lookup, identity, snapshot));
					}),
				model.S,
				model.aw));
	});
var $elm$core$List$singleton = function (value) {
	return _List_fromArray(
		[value]);
};
var $author$project$Launch$status = function (_v0) {
	var model = _v0;
	var _v1 = model.aU;
	switch (_v1.$) {
		case 0:
			return 'Idle';
		case 1:
			return 'Pending';
		default:
			switch (_v1.b) {
				case 0:
					var _v2 = _v1.b;
					return 'Submitted';
				case 1:
					var _v3 = _v1.b;
					return 'Refused';
				default:
					var _v4 = _v1.b;
					return 'Unknown';
			}
	}
};
var $author$project$Launch$Acknowledgement = $elm$core$Basics$identity;
var $author$project$Launch$uncertain = function (_v0) {
	var model = _v0;
	var _v1 = model.aU;
	if ((_v1.$ === 2) && (_v1.b === 2)) {
		var intent = _v1.a;
		var _v2 = _v1.b;
		return $elm$core$Maybe$Just(intent);
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$Surface$controls = function (model) {
	if (model.C) {
		var scoped = function (build) {
			return A2(
				$elm$core$Maybe$map,
				build,
				$author$project$Desktop$capture(model));
		};
		var ready = !A2(
			$elm$core$List$member,
			$author$project$Launch$status(model.d),
			_List_fromArray(
				['Pending', 'Unknown']));
		var entryControl = function (entry) {
			var choice = ready ? A2(
				$elm$core$Maybe$map,
				$author$project$Desktop$Start,
				A2(
					$author$project$Launch$select,
					$author$project$Catalog$id(entry.bK),
					model.d)) : $elm$core$Maybe$Nothing;
			return {
				o: 'Open ' + entry.cH,
				p: '',
				q: A2(
					$author$project$Desktop$key,
					model,
					'entry:' + $author$project$Catalog$id(entry.bK)),
				aF: !_Utils_eq(choice, $elm$core$Maybe$Nothing),
				bJ: 'entry:' + $author$project$Catalog$id(entry.bK),
				bP: 'Open ' + entry.cH,
				m: choice
			};
		};
		var entries = A2(
			$elm$core$Maybe$withDefault,
			_List_Nil,
			A2($elm$core$Maybe$map, $author$project$Catalog$entries, model.P));
		var acknowledge = A2(
			$elm$core$Maybe$withDefault,
			_List_Nil,
			A2(
				$elm$core$Maybe$map,
				$elm$core$List$singleton,
				A2(
					$elm$core$Maybe$map,
					function (token) {
						return {
							o: 'I checked; allow another launch',
							p: '',
							q: A2($author$project$Desktop$key, model, 'control:acknowledge'),
							aF: true,
							bJ: 'control:acknowledge',
							bP: 'I checked; allow another launch',
							m: $elm$core$Maybe$Just(
								$author$project$Desktop$Acknowledge(token))
						};
					},
					$author$project$Launch$uncertain(model.d))));
		return _Utils_ap(
			_List_fromArray(
				[
					{
					o: 'Close applications and return to windows',
					p: '',
					q: A2($author$project$Desktop$key, model, 'control:close'),
					aF: true,
					bJ: 'control:close',
					bP: 'Windows',
					m: scoped($author$project$Desktop$CloseApplications)
				},
					{
					o: 'Refresh applications',
					p: '',
					q: A2($author$project$Desktop$key, model, 'control:refresh'),
					aF: true,
					bJ: 'control:refresh',
					bP: 'Refresh',
					m: scoped($author$project$Desktop$OpenApplications)
				}
				]),
			_Utils_ap(
				acknowledge,
				A2($elm$core$List$map, entryControl, entries)));
	} else {
		if (!_Utils_eq(
			$author$project$MenuBridge$menuSnapshot(model.a.ac).ap,
			$elm$core$Maybe$Nothing)) {
			var _v0 = $author$project$MenuBridge$menuSnapshot(model.a.ac).ap;
			if (_v0.$ === 1) {
				return _List_Nil;
			} else {
				var menu = _v0.a;
				var ready = $author$project$Shell$available(model.a.b) && _Utils_eq(menu.x, $author$project$Menu$Ready);
				var prefix = 'menu:' + ($elm$core$String$fromInt(
					$author$project$Menu$menuNumber(menu.bJ)) + ':');
				var row = F2(
					function (index, item) {
						return {
							o: item.bP,
							p: _Utils_eq(
								menu.aj,
								$elm$core$Maybe$Just(index)) ? 'Selected' : '',
							q: _Utils_ap(
								prefix,
								$elm$core$String$fromInt(index)),
							aF: ready && item.aF,
							bJ: _Utils_ap(
								prefix,
								$elm$core$String$fromInt(index)),
							bP: item.bP,
							m: (ready && item.aF) ? $elm$core$Maybe$Just(
								$author$project$Desktop$Window(
									$author$project$TaskbarShell$MenuEvent(
										A3($author$project$Menu$Activate, menu.bJ, menu.c, index)))) : $elm$core$Maybe$Nothing
						};
					});
				return A2(
					$elm$core$List$cons,
					{
						o: 'Close window actions',
						p: '',
						q: prefix + 'close',
						aF: true,
						bJ: 'control:menu-close',
						bP: 'Close',
						m: $elm$core$Maybe$Just(
							$author$project$Desktop$Window(
								$author$project$TaskbarShell$MenuEvent(
									$author$project$Menu$Dismiss(menu.bJ))))
					},
					A2($elm$core$List$indexedMap, row, menu.aM));
			}
		} else {
			var _v1 = model.a.D;
			if (!_v1.$) {
				var picker = _v1.a;
				var familyControl = function (family) {
					var ready = $author$project$Shell$available(model.a.b) && (family.bc && _Utils_eq(
						$author$project$Shell$capture(model.a.b),
						$elm$core$Maybe$Just(picker.a7)));
					return {
						o: _Utils_ap(
							family.aq ? 'Restore ' : 'Activate ',
							family.bP),
						p: family.aq ? 'Minimized' : 'Open',
						q: 'picker:' + ($author$project$Shell$stampKey(picker.a7) + (':' + ($author$project$UInt64$string(picker.cx) + (':' + $author$project$UInt64$string(family.ai))))),
						aF: ready,
						bJ: 'family:' + $author$project$UInt64$string(family.ai),
						bP: _Utils_ap(
							family.aq ? 'Restore ' : 'Activate ',
							family.bP),
						m: ready ? $elm$core$Maybe$Just(
							$author$project$Desktop$Window(
								A3($author$project$TaskbarShell$Choose, picker.a7, picker.cx, family.ai))) : $elm$core$Maybe$Nothing
					};
				};
				var families = A2(
					$elm$core$List$concatMap,
					function ($) {
						return $.aH;
					},
					A2(
						$elm$core$List$filter,
						function (group) {
							return _Utils_eq(group.t, picker.t);
						},
						$author$project$TaskbarShell$groups(model.a)));
				return A2(
					$elm$core$List$cons,
					{
						o: 'Close window picker',
						p: '',
						q: 'picker-close:' + ($author$project$Shell$stampKey(picker.a7) + (':' + $author$project$UInt64$string(picker.cx))),
						aF: true,
						bJ: 'control:close',
						bP: 'Close',
						m: $elm$core$Maybe$Just(
							$author$project$Desktop$Window(
								A2($author$project$TaskbarShell$Close, picker.a7, picker.cx)))
					},
					A2($elm$core$List$map, familyControl, families));
			} else {
				return _List_Nil;
			}
		}
	}
};
var $elm$json$Json$Encode$int = _Json_wrap;
var $author$project$Surface$mode = function (model) {
	return model.C ? 'applications' : ((!_Utils_eq(
		$author$project$MenuBridge$menuSnapshot(model.a.ac).ap,
		$elm$core$Maybe$Nothing)) ? 'menu' : ((!_Utils_eq(model.a.D, $elm$core$Maybe$Nothing)) ? 'picker' : 'closed'));
};
var $author$project$Surface$notice = function (model) {
	if ($author$project$Surface$mode(model) === 'menu') {
		var _v0 = A2(
			$elm$core$Maybe$map,
			function ($) {
				return $.x;
			},
			$author$project$MenuBridge$menuSnapshot(model.a.ac).ap);
		_v0$3:
		while (true) {
			if (!_v0.$) {
				switch (_v0.a.$) {
					case 2:
						var reason = _v0.a.a;
						return reason;
					case 4:
						return 'The operation could not be confirmed.';
					case 1:
						return 'Working…';
					default:
						break _v0$3;
				}
			} else {
				break _v0$3;
			}
		}
		return 'Window actions';
	} else {
		if (!_Utils_eq(model.s, $elm$core$Maybe$Nothing)) {
			return 'Updating your window choice…';
		} else {
			if (!$elm$core$String$isEmpty(model.E)) {
				return model.E;
			} else {
				var _v1 = $author$project$Launch$status(model.d);
				switch (_v1) {
					case 'Pending':
						return 'Opening application…';
					case 'Unknown':
						return 'The launch could not be confirmed. Check your windows before opening it again.';
					case 'Submitted':
						return 'Launch submitted.';
					case 'Refused':
						return 'The application changed or could not be launched. Refresh and choose again.';
					default:
						return model.C ? ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) ? 'Loading applications…' : (_Utils_eq(model.P, $elm$core$Maybe$Nothing) ? 'Application list unavailable. Refresh to try again.' : 'Choose an application.')) : $author$project$Shell$status(model.a.b);
				}
			}
		}
	}
};
var $author$project$Surface$packet = F3(
	function (publication, lease, model) {
		var encode = function (control) {
			return $elm$json$Json$Encode$object(
				_List_fromArray(
					[
						_Utils_Tuple2(
						'id',
						$elm$json$Json$Encode$string(control.bJ)),
						_Utils_Tuple2(
						'domId',
						$elm$json$Json$Encode$string(control.q)),
						_Utils_Tuple2(
						'label',
						$elm$json$Json$Encode$string(control.bP)),
						_Utils_Tuple2(
						'ariaLabel',
						$elm$json$Json$Encode$string(control.o)),
						_Utils_Tuple2(
						'detail',
						$elm$json$Json$Encode$string(control.p)),
						_Utils_Tuple2(
						'enabled',
						$elm$json$Json$Encode$bool(
							control.aF && (!_Utils_eq(control.m, $elm$core$Maybe$Nothing))))
					]));
		};
		return $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'surfaceProtocol',
					$elm$json$Json$Encode$int(2)),
					_Utils_Tuple2(
					'publication',
					$elm$json$Json$Encode$string(
						$author$project$UInt64$string(publication))),
					_Utils_Tuple2(
					'lease',
					$elm$json$Json$Encode$string(
						$author$project$UInt64$string(lease))),
					_Utils_Tuple2(
					'mode',
					$elm$json$Json$Encode$string(
						$author$project$Surface$mode(model))),
					_Utils_Tuple2(
					'status',
					$elm$json$Json$Encode$string(
						$author$project$Surface$notice(model))),
					_Utils_Tuple2(
					'bar',
					A2(
						$elm$json$Json$Encode$list,
						encode,
						$author$project$Surface$barControls(model))),
					_Utils_Tuple2(
					'popup',
					A2(
						$elm$json$Json$Encode$list,
						encode,
						$author$project$Surface$controls(model)))
				]));
	});
var $author$project$SurfaceController$frame = function (_v0) {
	var model = _v0;
	return A3($author$project$Surface$packet, model.ag, model.I, model.h);
};
var $elm$core$Result$map = F2(
	function (func, ra) {
		if (!ra.$) {
			var a = ra.a;
			return $elm$core$Result$Ok(
				func(a));
		} else {
			var e = ra.a;
			return $elm$core$Result$Err(e);
		}
	});
var $author$project$GeometryProjection$modeName = function (mode) {
	switch (mode) {
		case 0:
			return 'ordinary';
		case 1:
			return 'maximized';
		default:
			return 'fullscreen';
	}
};
var $author$project$Provider$presentationScope = function (_v0) {
	var value = _v0;
	return {bi: value.am.bi, bm: value.bm};
};
var $author$project$ReceiptRouter$count = function (_v0) {
	var entries = _v0;
	return $elm$core$List$length(entries);
};
var $author$project$MenuBridge$receiptCount = function (_v0) {
	var state = _v0;
	return $author$project$ReceiptRouter$count(state.av);
};
var $elm$core$Result$toMaybe = function (result) {
	if (!result.$) {
		var v = result.a;
		return $elm$core$Maybe$Just(v);
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$SurfaceController$Model = $elm$core$Basics$identity;
var $author$project$SurfaceController$Publish = function (a) {
	return {$: 1, a: a};
};
var $author$project$Shell$Refresh = {$: 1};
var $author$project$SurfaceController$DesktopEffect = function (a) {
	return {$: 0, a: a};
};
var $elm$core$Char$fromCode = _Char_fromCode;
var $elm$core$String$fromList = _String_fromList;
var $elm$core$String$foldr = _String_foldr;
var $elm$core$String$toList = function (string) {
	return A3($elm$core$String$foldr, $elm$core$List$cons, _List_Nil, string);
};
var $author$project$UInt64$next = function (_v0) {
	var value = _v0;
	var add = function (digits) {
		if (!digits.b) {
			return _List_fromArray(
				['1']);
		} else {
			if ('9' === digits.a) {
				var rest = digits.b;
				return A2(
					$elm$core$List$cons,
					'0',
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
		$elm$core$String$fromList(
			$elm$core$List$reverse(
				add(
					$elm$core$List$reverse(
						$elm$core$String$toList(value))))));
};
var $author$project$Desktop$Arm = function (a) {
	return {$: 2, a: a};
};
var $author$project$Desktop$Focus = function (a) {
	return {$: 4, a: a};
};
var $author$project$Shell$Incoming = function (a) {
	return {$: 0, a: a};
};
var $author$project$Menu$Invalidate = function (a) {
	return {$: 6, a: a};
};
var $author$project$TaskbarShell$OpenMenu = function (a) {
	return {$: 4, a: a};
};
var $author$project$Desktop$Send = function (a) {
	return {$: 1, a: a};
};
var $author$project$Launch$Idle = {$: 0};
var $author$project$Launch$Model = $elm$core$Basics$identity;
var $author$project$Launch$advance = function (_v0) {
	var model = _v0;
	var _v1 = $author$project$UInt64$next(model.cP);
	if (!_v1.$) {
		var revision = _v1.a;
		return _Utils_update(
			model,
			{cP: revision});
	} else {
		return _Utils_update(
			model,
			{S: $elm$core$Maybe$Nothing, aw: $elm$core$Maybe$Nothing});
	}
};
var $author$project$Launch$acknowledgeUnknown = F2(
	function (_v0, current) {
		var intent = _v0;
		var model = current;
		var _v1 = model.aU;
		if ((_v1.$ === 2) && (_v1.b === 2)) {
			var active = _v1.a;
			var _v2 = _v1.b;
			return _Utils_eq(active, intent) ? $author$project$Launch$advance(
				_Utils_update(
					model,
					{aU: $author$project$Launch$Idle})) : current;
		} else {
			return current;
		}
	});
var $author$project$Desktop$advance = function (model) {
	var _v0 = A2($elm$core$Maybe$andThen, $author$project$UInt64$next, model.X);
	if (!_v0.$) {
		var value = _v0.a;
		return _Utils_update(
			model,
			{
				X: $elm$core$Maybe$Just(value)
			});
	} else {
		return _Utils_update(
			model,
			{P: $elm$core$Maybe$Nothing, k: $elm$core$Maybe$Nothing, C: false, X: $elm$core$Maybe$Nothing});
	}
};
var $author$project$Catalog$Snapshot = F3(
	function (a, b, c) {
		return {$: 0, a: a, b: b, c: c};
	});
var $author$project$Catalog$Entry = F4(
	function (identity, name, iconHint, wmclass) {
		return {cC: iconHint, bK: identity, cH: name, cS: wmclass};
	});
var $author$project$Catalog$EntryId = $elm$core$Basics$identity;
var $elm$json$Json$Decode$map = _Json_map1;
var $elm$json$Json$Decode$map4 = _Json_map4;
var $author$project$Catalog$strict = F2(
	function (names, decoder) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (fields) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, fields)),
					$elm$core$List$sort(names)) ? decoder : $elm$json$Json$Decode$fail('Unexpected catalog fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$Catalog$text = F2(
	function (limit, nonempty) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (value) {
				return ((_Utils_cmp(
					$elm$core$String$length(value),
					limit) < 1) && (((!nonempty) || (!$elm$core$String$isEmpty(value))) && (!A2(
					$elm$core$String$any,
					function (c) {
						return $elm$core$Char$toCode(c) < 32;
					},
					value)))) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Catalog text');
			},
			$elm$json$Json$Decode$string);
	});
var $author$project$Catalog$entryDecoder = A2(
	$author$project$Catalog$strict,
	_List_fromArray(
		['id', 'name', 'iconHint', 'wmclass']),
	A5(
		$elm$json$Json$Decode$map4,
		$author$project$Catalog$Entry,
		A2(
			$elm$json$Json$Decode$field,
			'id',
			A2(
				$elm$json$Json$Decode$map,
				$elm$core$Basics$identity,
				A2($author$project$Catalog$text, 256, true))),
		A2(
			$elm$json$Json$Decode$field,
			'name',
			A2($author$project$Catalog$text, 512, false)),
		A2(
			$elm$json$Json$Decode$field,
			'iconHint',
			A2($author$project$Catalog$text, 512, false)),
		A2(
			$elm$json$Json$Decode$field,
			'wmclass',
			A2($author$project$Catalog$text, 512, false))));
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
var $author$project$Catalog$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (!_Utils_eq(value, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Zero catalog authority');
	},
	$author$project$UInt64$decoder);
var $author$project$Catalog$decode = function (raw) {
	var protocol = A2(
		$elm$json$Json$Decode$andThen,
		function (value) {
			return (value === 1) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Catalog version');
		},
		A2($elm$json$Json$Decode$field, 'catalogProtocol', $elm$json$Json$Decode$int));
	var entryList = A2(
		$elm$json$Json$Decode$andThen,
		function (values) {
			return ($elm$core$List$length(values) <= 2048) ? $elm$json$Json$Decode$list($author$project$Catalog$entryDecoder) : $elm$json$Json$Decode$fail('Catalog capacity');
		},
		$elm$json$Json$Decode$list($elm$json$Json$Decode$value));
	var decoder = A2(
		$author$project$Catalog$strict,
		_List_fromArray(
			['catalogProtocol', 'lifetime', 'generation', 'entries']),
		A5(
			$elm$json$Json$Decode$map4,
			F4(
				function (_v1, lifetime, generation, values) {
					return _Utils_Tuple3(lifetime, generation, values);
				}),
			protocol,
			A2($elm$json$Json$Decode$field, 'lifetime', $author$project$Catalog$positive),
			A2($elm$json$Json$Decode$field, 'generation', $author$project$Catalog$positive),
			A2($elm$json$Json$Decode$field, 'entries', entryList)));
	return A2(
		$elm$core$Result$andThen,
		function (_v0) {
			var lifetime = _v0.a;
			var generation = _v0.b;
			var values = _v0.c;
			var dict = $elm$core$Dict$fromList(
				A2(
					$elm$core$List$map,
					function (entry) {
						return _Utils_Tuple2(
							$author$project$Catalog$id(entry.bK),
							entry);
					},
					values));
			return (!_Utils_eq(
				$elm$core$Dict$size(dict),
				$elm$core$List$length(values))) ? $elm$core$Result$Err('Duplicate desktop identity') : $elm$core$Result$Ok(
				A3($author$project$Catalog$Snapshot, lifetime, generation, dict));
		},
		A2(
			$elm$core$Result$mapError,
			$elm$json$Json$Decode$errorToString,
			A2($elm$json$Json$Decode$decodeValue, decoder, raw)));
};
var $author$project$Launch$catalog = F2(
	function (raw, _v0) {
		var model = _v0;
		return $author$project$Launch$advance(
			_Utils_update(
				model,
				{
					aw: $elm$core$Result$toMaybe(
						$author$project$Catalog$decode(raw))
				}));
	});
var $author$project$Binding$Binding = F3(
	function (a, b, c) {
		return {$: 0, a: a, b: b, c: c};
	});
var $elm$json$Json$Decode$map3 = _Json_map3;
var $author$project$Binding$nonzero = A2(
	$elm$json$Json$Decode$andThen,
	function (v) {
		return _Utils_eq(v, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero identity') : $elm$json$Json$Decode$succeed(v);
	},
	$author$project$UInt64$decoder);
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
var $author$project$Provider$incarnation = function (_v0) {
	var value = _v0;
	return value.A;
};
var $author$project$NativeProvider$counter = A2($elm$core$Basics$composeR, $author$project$UInt64$string, $elm$json$Json$Encode$string);
var $author$project$Provider$Raw = F7(
	function (provider, capabilitiesGeneration, context, target, heading, capabilities, entries) {
		return {a3: capabilities, bd: capabilitiesGeneration, am: context, aG: entries, bH: heading, at: provider, br: target};
	});
var $author$project$Provider$Snapshot = $elm$core$Basics$identity;
var $author$project$Menu$Window = function (a) {
	return {$: 0, a: a};
};
var $author$project$Binding$authorityIdentity = function (_v0) {
	var lifetime = _v0.a;
	return $author$project$UInt64$string(lifetime);
};
var $author$project$Menu$Binding = $elm$core$Basics$identity;
var $author$project$Menu$binding = $elm$core$Basics$identity;
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
				if (!_v0.$) {
					return $elm$json$Json$Decode$fail('Provider array bound');
				} else {
					return $elm$json$Json$Decode$list(body);
				}
			},
			$elm$json$Json$Decode$value);
	});
var $author$project$Provider$Context = F7(
	function (_native, lifetime, session, frontend, revision, outputId, outputGeneration) {
		return {bF: frontend, cF: lifetime, bU: _native, cL: outputGeneration, bi: outputId, cP: revision, a8: session};
	});
var $author$project$Provider$nonzero = A2(
	$elm$json$Json$Decode$andThen,
	function (counter) {
		return _Utils_eq(counter, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero provider identity') : $elm$json$Json$Decode$succeed(counter);
	},
	$author$project$UInt64$decoder);
var $author$project$Provider$nativeDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		var _v0 = A2($elm$json$Json$Decode$decodeValue, $author$project$Binding$decoder, value);
		if (!_v0.$) {
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
var $author$project$Menu$AlwaysOnTop = function (a) {
	return {$: 8, a: a};
};
var $author$project$Menu$Close = {$: 6};
var $author$project$Menu$ExitFullscreen = {$: 7};
var $author$project$Menu$Maximize = {$: 5};
var $author$project$Menu$Minimize = {$: 4};
var $author$project$Menu$Move = {$: 2};
var $author$project$Menu$Restore = {$: 0};
var $author$project$Menu$Size = {$: 3};
var $author$project$Provider$actionKinds = _List_fromArray(
	['Restore', 'Minimize', 'Move', 'Size', 'Maximize', 'Close', 'ExitFullscreen', 'AlwaysOnTop']);
var $author$project$Provider$kindDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (kind) {
		return A2($elm$core$List$member, kind, $author$project$Provider$actionKinds) ? $elm$json$Json$Decode$succeed(kind) : $elm$json$Json$Decode$fail('Unsupported window action');
	},
	$elm$json$Json$Decode$string);
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
		if (_v0.$ === 1) {
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
						if (!_v2.$) {
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
					bJ: $author$project$UInt64$string(identity),
					aL: {a1: action, aF: enabled, bP: label},
					bN: kind
				};
			}),
		A2($elm$json$Json$Decode$field, 'id', $author$project$Provider$nonzero),
		A2($elm$json$Json$Decode$field, 'label', $author$project$Provider$textDecoder),
		A2($elm$json$Json$Decode$field, 'enabled', $elm$json$Json$Decode$bool),
		A2($elm$json$Json$Decode$field, 'action', $author$project$Provider$actionDecoder)));
var $elm$json$Json$Decode$map2 = _Json_map2;
var $author$project$Menu$OutputId = $elm$core$Basics$identity;
var $author$project$Menu$outputId = $elm$core$Basics$identity;
var $author$project$Provider$Target = F3(
	function (lifetime, session, incarnation) {
		return {A: incarnation, cF: lifetime, a8: session};
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
		return {$: 0, a: a, b: b};
	});
var $author$project$Menu$windowId = $author$project$Menu$WindowId;
var $author$project$Provider$envelopeDecoder = function () {
	var version = A2(
		$elm$json$Json$Decode$andThen,
		function (number) {
			return (number === 1) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Provider protocol version');
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
					return entry.aL.aF && (!A2($elm$core$List$member, entry.bN, raw.a3));
				},
				raw.aG);
			var identities = A2(
				$elm$core$List$map,
				function ($) {
					return $.bJ;
				},
				raw.aG);
			var duplicateIds = !_Utils_eq(
				$elm$core$List$length(identities),
				$elm$core$Set$size(
					$elm$core$Set$fromList(identities)));
			var duplicateCapabilities = !_Utils_eq(
				$elm$core$List$length(raw.a3),
				$elm$core$Set$size(
					$elm$core$Set$fromList(raw.a3)));
			var coherent = _Utils_eq(raw.br.cF, raw.am.cF) && _Utils_eq(raw.br.a8, raw.am.a8);
			var authority = A2(
				$elm$json$Json$Encode$encode,
				0,
				A2(
					$elm$json$Json$Encode$list,
					$elm$core$Basics$identity,
					_List_fromArray(
						[
							$author$project$Binding$encode(raw.am.bU),
							$elm$json$Json$Encode$string(
							$author$project$UInt64$string(raw.at)),
							$elm$json$Json$Encode$string(
							$author$project$UInt64$string(raw.bd))
						])));
			var actions = A2(
				$elm$core$List$map,
				A2(
					$elm$core$Basics$composeR,
					function ($) {
						return $.aL;
					},
					function ($) {
						return $.a1;
					}),
				raw.aG);
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
				{
					c: $author$project$Menu$binding(
						{
							bt: authority,
							v: $author$project$Menu$outputId(
								$author$project$UInt64$string(raw.am.bi)),
							cL: $author$project$UInt64$string(raw.am.cL),
							cP: $author$project$UInt64$string(raw.am.cP),
							br: $author$project$Menu$Window(
								A2(
									$author$project$Menu$windowId,
									$author$project$Binding$authorityIdentity(raw.am.bU),
									$author$project$UInt64$string(raw.br.A)))
						}),
					cp: raw.bd,
					am: raw.am,
					bG: $elm$core$Maybe$Nothing,
					A: raw.br.A,
					aM: A2(
						$elm$core$List$map,
						function ($) {
							return $.aL;
						},
						raw.aG),
					bm: raw.at,
					b9: raw.bH
				});
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
		case 0:
			var field = error.a;
			var nested = error.b;
			return 'Provider field ' + (field + (': ' + $author$project$Provider$errorSummary(nested)));
		case 1:
			var index = error.a;
			var nested = error.b;
			return 'Provider index ' + ($elm$core$String$fromInt(index) + (': ' + $author$project$Provider$errorSummary(nested)));
		case 2:
			return 'Provider alternatives rejected';
		default:
			var reason = error.a;
			return A2($elm$core$String$left, 256, reason);
	}
};
var $author$project$Provider$decode = function (value) {
	return A2(
		$elm$core$Result$mapError,
		$author$project$Provider$errorSummary,
		A2($elm$json$Json$Decode$decodeValue, $author$project$Provider$decoder, value));
};
var $author$project$NativeProvider$legacyFromShell = F3(
	function (scope, incarnation, shell) {
		if (_Utils_eq(scope.bi, $author$project$UInt64$zero) || (_Utils_eq(scope.bm, $author$project$UInt64$zero) || _Utils_eq(scope.cp, $author$project$UInt64$zero))) {
			return $elm$core$Result$Err('Missing registered provider/output identity');
		} else {
			if (shell.aU !== 2) {
				return $elm$core$Result$Err('Native window facts are not ready');
			} else {
				var _v0 = _Utils_Tuple2(shell.c, shell.aE.aS);
				if ((!_v0.a.$) && (!_v0.b.$)) {
					var binding = _v0.a.a;
					var observed = _v0.b.a;
					if (!A3($author$project$Binding$matchesContext, observed.am.cF, observed.am.a4, binding)) {
						return $elm$core$Result$Err('Native observation binding mismatch');
					} else {
						var _v1 = A2(
							$elm$core$Maybe$andThen,
							function (root) {
								return $elm$core$List$head(
									A2(
										$elm$core$List$filter,
										function (window) {
											return _Utils_eq(window.A, root);
										},
										$author$project$ActionProjection$windows(observed.N)));
							},
							A2($author$project$ActionProjection$rootOf, incarnation, observed.N));
						if (_v1.$ === 1) {
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
							if (identities.$ === 1) {
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
												$author$project$NativeProvider$counter(scope.bm)),
												_Utils_Tuple2(
												'capabilityGeneration',
												$author$project$NativeProvider$counter(scope.cp)),
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
															$author$project$NativeProvider$counter(observed.am.cP)),
															_Utils_Tuple2(
															'outputId',
															$author$project$NativeProvider$counter(scope.bi)),
															_Utils_Tuple2(
															'outputGeneration',
															$author$project$NativeProvider$counter(observed.am.v))
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
															$author$project$NativeProvider$counter(window.A))
														]))),
												_Utils_Tuple2(
												'title',
												$elm$json$Json$Encode$string(
													($elm$core$String$trim(window.bP) === '') ? 'Window actions' : window.bP)),
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
															A4(item, '1', 'Restore', window.bc && window.aq, 'Restore'),
															A4(item, '2', 'Minimize', window.bc && (!window.aq), 'Minimize')
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
var $author$project$ActionProjection$find = F2(
	function (identity, rows) {
		return $elm$core$List$head(
			A2(
				$elm$core$List$filter,
				function (w) {
					return _Utils_eq(w.A, identity);
				},
				rows));
	});
var $author$project$ActionProjection$minimized = F2(
	function (identity, projection) {
		return A2(
			$elm$core$Maybe$map,
			function ($) {
				return $.aq;
			},
			A2(
				$author$project$ActionProjection$find,
				identity,
				$author$project$ActionProjection$windows(projection)));
	});
var $author$project$GeometryProjection$window = F2(
	function (incarnation, snapshot) {
		return $elm$core$List$head(
			A2(
				$elm$core$List$filter,
				function (row) {
					return _Utils_eq(row.A, incarnation);
				},
				snapshot.a));
	});
var $author$project$GeometryProjection$Maximized = 1;
var $author$project$GeometryProjection$Ordinary = 0;
var $author$project$Menu$RestoreGeometry = {$: 1};
var $author$project$Provider$withGeometry = F3(
	function (caps, observed, snapshot) {
		var state = snapshot;
		if ((!_Utils_eq(observed.c, state.am.bU)) || (!_Utils_eq(observed.am.v, state.am.cL))) {
			return $elm$core$Result$Err('Geometry/legacy authority mismatch');
		} else {
			var _v0 = A2($author$project$GeometryProjection$window, state.A, observed);
			if (_v0.$ === 1) {
				return $elm$core$Result$Err('Geometry target missing');
			} else {
				var window = _v0.a;
				var supported = function (op) {
					return caps.aE && A2($elm$core$List$member, op, caps.cK);
				};
				var restoreGeometry = supported('restore-geometry') && (!window.aq);
				var ready = A2(
					$elm$core$List$any,
					function ($) {
						return $.aF;
					},
					state.aM) && ((!observed.aC) && (window.cu && ((!window.cw) && (!window.cr))));
				var legacyRestore = $elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (item) {
							return _Utils_eq(item.a1, $author$project$Menu$Restore);
						},
						state.aM));
				var restore = restoreGeometry ? {a1: $author$project$Menu$RestoreGeometry, aF: ready && (window.cN && ((window.bV === 1) && window.cM)), bP: 'Restore'} : A2(
					$elm$core$Maybe$withDefault,
					{a1: $author$project$Menu$Restore, aF: false, bP: 'Restore'},
					legacyRestore);
				var legacyMinimize = $elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (item) {
							return _Utils_eq(item.a1, $author$project$Menu$Minimize);
						},
						state.aM));
				var minimize = A2(
					$elm$core$Maybe$withDefault,
					{a1: $author$project$Menu$Minimize, aF: false, bP: 'Minimize'},
					legacyMinimize);
				var items = _Utils_ap(
					_List_fromArray(
						[restore, minimize]),
					supported('maximize') ? _List_fromArray(
						[
							{a1: $author$project$Menu$Maximize, aF: ready && (window.cG && ((!window.aq) && (!window.bV))), bP: 'Maximize'}
						]) : _List_Nil);
				var authority = A2(
					$elm$json$Json$Encode$encode,
					0,
					A2(
						$elm$json$Json$Encode$list,
						$elm$core$Basics$identity,
						_List_fromArray(
							[
								$elm$json$Json$Encode$string(
								A2(
									$elm$json$Json$Encode$encode,
									0,
									$author$project$Binding$encode(state.am.bU)) + (':' + ($author$project$UInt64$string(state.bm) + (':' + ($author$project$UInt64$string(state.cp) + (':' + $author$project$UInt64$string(state.am.cP))))))),
								$elm$json$Json$Encode$string(
								$author$project$UInt64$string(observed.am.cP)),
								$elm$json$Json$Encode$string(
								$author$project$UInt64$string(observed.am.v)),
								A2($elm$json$Json$Encode$list, $elm$json$Json$Encode$string, caps.cK)
							])));
				return $elm$core$Result$Ok(
					_Utils_update(
						state,
						{
							c: $author$project$Menu$binding(
								{
									bt: authority,
									v: $author$project$Menu$outputId(
										$author$project$UInt64$string(state.am.bi)),
									cL: $author$project$UInt64$string(observed.am.v),
									cP: $author$project$UInt64$string(observed.am.cP),
									br: $author$project$Menu$Window(
										A2(
											$author$project$Menu$windowId,
											$author$project$Binding$authorityIdentity(state.am.bU),
											$author$project$UInt64$string(state.A)))
								}),
							bG: $elm$core$Maybe$Just(observed),
							aM: items
						}));
			}
		}
	});
var $author$project$NativeProvider$fromShell = F3(
	function (scope, incarnation, shell) {
		return A2(
			$elm$core$Result$andThen,
			function (legacy) {
				var _v0 = shell.cz;
				if (_v0.$ === 1) {
					return $elm$core$Result$Ok(legacy);
				} else {
					var caps = _v0.a;
					if (!caps.aE) {
						return $elm$core$Result$Ok(legacy);
					} else {
						var _v1 = _Utils_Tuple3(shell.bG, shell.cA, shell.aE.aS);
						if (((!_v1.a.$) && (_v1.b.$ === 1)) && (!_v1.c.$)) {
							var observed = _v1.a.a;
							var _v2 = _v1.b;
							var legacyObserved = _v1.c.a;
							var root = $author$project$Provider$incarnation(legacy);
							var legacyMinimized = A2($author$project$ActionProjection$minimized, root, legacyObserved.N);
							var geometryMinimized = A2(
								$elm$core$Maybe$map,
								function ($) {
									return $.aq;
								},
								A2($author$project$GeometryProjection$window, root, observed));
							return (!_Utils_eq(legacyMinimized, geometryMinimized)) ? $elm$core$Result$Err('Independent geometry/legacy facts disagree') : A3($author$project$Provider$withGeometry, caps, observed, legacy);
						} else {
							return $elm$core$Result$Err('Geometry facts are awaiting fresh observation');
						}
					}
				}
			},
			A3($author$project$NativeProvider$legacyFromShell, scope, incarnation, shell));
	});
var $author$project$Provider$getBinding = function (_v0) {
	var value = _v0;
	return value.c;
};
var $author$project$Launch$PendingToken = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$Launch$pending = function (_v0) {
	var model = _v0;
	var _v1 = model.aU;
	if (_v1.$ === 1) {
		var host = _v1.a;
		var intent = _v1.b;
		return $elm$core$Maybe$Just(
			A2($author$project$Launch$PendingToken, host, intent));
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$Launch$Settled = F2(
	function (a, b) {
		return {$: 2, a: a, b: b};
	});
var $author$project$Launch$Refused = 1;
var $author$project$Launch$Submitted = 0;
var $author$project$Launch$Unknown = 2;
var $author$project$Launch$Intent = F4(
	function (request, lifetime, generation, entry) {
		return {bA: entry, cx: generation, cF: lifetime, a6: request};
	});
var $author$project$Launch$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return _Utils_eq(value, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero launch counter') : $elm$json$Json$Decode$succeed(value);
	},
	$author$project$UInt64$decoder);
var $author$project$Launch$strict = F2(
	function (names, decoder) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (fields) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, fields)),
					$elm$core$List$sort(names)) ? decoder : $elm$json$Json$Decode$fail('Unexpected launch receipt fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$Launch$intentDecoder = A2(
	$author$project$Launch$strict,
	_List_fromArray(
		['request', 'lifetime', 'generation', 'entry']),
	A5(
		$elm$json$Json$Decode$map4,
		$author$project$Launch$Intent,
		A2($elm$json$Json$Decode$field, 'request', $author$project$Launch$positive),
		A2($elm$json$Json$Decode$field, 'lifetime', $author$project$Launch$positive),
		A2($elm$json$Json$Decode$field, 'generation', $author$project$Launch$positive),
		A2(
			$elm$json$Json$Decode$andThen,
			function (value) {
				return ($elm$core$String$isEmpty(value) || (($elm$core$String$length(value) > 256) || A2(
					$elm$core$String$any,
					function (c) {
						return $elm$core$Char$toCode(c) < 32;
					},
					value))) ? $elm$json$Json$Decode$fail('Launch identity') : $elm$json$Json$Decode$succeed(value);
			},
			A2($elm$json$Json$Decode$field, 'entry', $elm$json$Json$Decode$string))));
var $elm$json$Json$Decode$map5 = _Json_map5;
var $author$project$Launch$receiptDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (receipt) {
		return ((receipt.ca !== 1) || (receipt.bN !== 'launch-outcome')) ? $elm$json$Json$Decode$fail('Launch receipt version/kind') : (((receipt.a9 === 'Submitted') && (receipt.a5 === 'native-submission-accepted')) ? $elm$json$Json$Decode$succeed(
			_Utils_Tuple2(receipt.G, 0)) : (((receipt.a9 === 'Unknown') && (receipt.a5 === 'submission-not-confirmed')) ? $elm$json$Json$Decode$succeed(
			_Utils_Tuple2(receipt.G, 2)) : (((receipt.a9 === 'Refused') && A2(
			$elm$core$List$member,
			receipt.a5,
			_List_fromArray(
				['retired-authority', 'request-reuse', 'retired-request', 'catalog-unavailable', 'stale-catalog', 'removed-entry', 'native-entry-unavailable', 'desktop-entry-raced']))) ? $elm$json$Json$Decode$succeed(
			_Utils_Tuple2(receipt.G, 1)) : $elm$json$Json$Decode$fail('Launch receipt outcome'))));
	},
	A2(
		$author$project$Launch$strict,
		_List_fromArray(
			['catalogProtocol', 'kind', 'intent', 'status', 'reason']),
		A6(
			$elm$json$Json$Decode$map5,
			F5(
				function (version, kind, intent, state, reason) {
					return {G: intent, bN: kind, a5: reason, a9: state, ca: version};
				}),
			A2($elm$json$Json$Decode$field, 'catalogProtocol', $elm$json$Json$Decode$int),
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			A2($elm$json$Json$Decode$field, 'intent', $author$project$Launch$intentDecoder),
			A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string),
			A2($elm$json$Json$Decode$field, 'reason', $elm$json$Json$Decode$string))));
var $author$project$Launch$receive = F3(
	function (host, raw, current) {
		var model = current;
		var _v0 = _Utils_Tuple2(
			model.aU,
			A2($elm$json$Json$Decode$decodeValue, $author$project$Launch$receiptDecoder, raw));
		if ((_v0.a.$ === 1) && (!_v0.b.$)) {
			var _v1 = _v0.a;
			var owner = _v1.a;
			var intent = _v1.b;
			var _v2 = _v0.b.a;
			var received = _v2.a;
			var result = _v2.b;
			return (_Utils_eq(host, owner) && (_Utils_eq(
				model.S,
				$elm$core$Maybe$Just(owner)) && _Utils_eq(received, intent))) ? $author$project$Launch$advance(
				_Utils_update(
					model,
					{
						aU: A2($author$project$Launch$Settled, intent, result)
					})) : current;
		} else {
			return current;
		}
	});
var $author$project$Launch$Pending = F2(
	function (a, b) {
		return {$: 1, a: a, b: b};
	});
var $elm$core$Dict$member = F2(
	function (key, dict) {
		var _v0 = A2($elm$core$Dict$get, key, dict);
		if (!_v0.$) {
			return true;
		} else {
			return false;
		}
	});
var $author$project$Catalog$intent = F3(
	function (request, entry, _v0) {
		var lifetime = _v0.a;
		var generation = _v0.b;
		var values = _v0.c;
		return (_Utils_eq(request, $author$project$UInt64$zero) || (!A2(
			$elm$core$Dict$member,
			$author$project$Catalog$id(entry),
			values))) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(
			$elm$json$Json$Encode$object(
				_List_fromArray(
					[
						_Utils_Tuple2(
						'request',
						$elm$json$Json$Encode$string(
							$author$project$UInt64$string(request))),
						_Utils_Tuple2(
						'lifetime',
						$elm$json$Json$Encode$string(
							$author$project$UInt64$string(lifetime))),
						_Utils_Tuple2(
						'generation',
						$elm$json$Json$Encode$string(
							$author$project$UInt64$string(generation))),
						_Utils_Tuple2(
						'entry',
						$elm$json$Json$Encode$string(
							$author$project$Catalog$id(entry)))
					])));
	});
var $author$project$Launch$start = F2(
	function (_v0, current) {
		var host = _v0.a;
		var revision = _v0.b;
		var lifetime = _v0.c;
		var generation = _v0.d;
		var entry = _v0.e;
		var model = current;
		var ready = function () {
			var _v3 = model.aU;
			switch (_v3.$) {
				case 0:
					return true;
				case 2:
					if (_v3.b === 2) {
						var _v4 = _v3.b;
						return false;
					} else {
						return true;
					}
				default:
					return false;
			}
		}();
		var _v1 = _Utils_Tuple2(
			model.aw,
			$author$project$UInt64$next(model.a6));
		if ((!_v1.a.$) && (!_v1.b.$)) {
			var snapshot = _v1.a.a;
			var request = _v1.b.a;
			var scope = $author$project$Catalog$scope(snapshot);
			if (ready && (_Utils_eq(
				model.S,
				$elm$core$Maybe$Just(host)) && (_Utils_eq(model.cP, revision) && (_Utils_eq(lifetime, scope.cF) && _Utils_eq(generation, scope.cx))))) {
				var _v2 = A3($author$project$Catalog$intent, request, entry, snapshot);
				if (!_v2.$) {
					var wire = _v2.a;
					return _Utils_Tuple2(
						$author$project$Launch$advance(
							_Utils_update(
								model,
								{
									aU: A2(
										$author$project$Launch$Pending,
										host,
										{
											bA: $author$project$Catalog$id(entry),
											cx: generation,
											cF: lifetime,
											a6: request
										}),
									a6: request
								})),
						$elm$core$Maybe$Just(wire));
				} else {
					return _Utils_Tuple2(current, $elm$core$Maybe$Nothing);
				}
			} else {
				return _Utils_Tuple2(current, $elm$core$Maybe$Nothing);
			}
		} else {
			return _Utils_Tuple2(current, $elm$core$Maybe$Nothing);
		}
	});
var $author$project$Desktop$strict = F2(
	function (fields, decoder) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? decoder : $elm$json$Json$Decode$fail('Desktop frame fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$Launch$timeout = F2(
	function (_v0, current) {
		var host = _v0.a;
		var intent = _v0.b;
		var model = current;
		var _v1 = model.aU;
		if (_v1.$ === 1) {
			var owner = _v1.a;
			var active = _v1.b;
			return (_Utils_eq(owner, host) && _Utils_eq(active, intent)) ? $author$project$Launch$advance(
				_Utils_update(
					model,
					{
						aU: A2($author$project$Launch$Settled, intent, 2)
					})) : current;
		} else {
			return current;
		}
	});
var $author$project$Desktop$version = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (value === 3) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Desktop version');
	},
	A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int));
var $author$project$Shell$Act = F3(
	function (a, b, c) {
		return {$: 6, a: a, b: b, c: c};
	});
var $author$project$Desktop$ArmChoice = function (a) {
	return {$: 3, a: a};
};
var $author$project$Desktop$ChoiceToken = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $elm$core$Tuple$pair = F2(
	function (a, b) {
		return _Utils_Tuple2(a, b);
	});
var $author$project$Taskbar$selection = function (entry) {
	return (!entry.bc) ? $author$project$Taskbar$Unavailable : A2(
		$author$project$Taskbar$Apply,
		entry.aq ? 1 : 2,
		entry.ai);
};
var $author$project$Shell$Exhausted = 3;
var $author$project$Desktop$WindowEffect = function (a) {
	return {$: 0, a: a};
};
var $author$project$Launch$disconnect = function (current) {
	var _v0 = A2(
		$elm$core$Maybe$withDefault,
		current,
		A2(
			$elm$core$Maybe$map,
			function (token) {
				return A2($author$project$Launch$timeout, token, current);
			},
			$author$project$Launch$pending(current)));
	var model = _v0;
	return $author$project$Launch$advance(
		_Utils_update(
			model,
			{S: $elm$core$Maybe$Nothing, aw: $elm$core$Maybe$Nothing}));
};
var $author$project$Launch$bind = F2(
	function (host, current) {
		var model = current;
		if ($elm$core$String$isEmpty(host) || (($elm$core$String$length(host) > 256) || A2(
			$elm$core$String$any,
			function (c) {
				return $elm$core$Char$toCode(c) < 32;
			},
			host))) {
			return $author$project$Launch$disconnect(current);
		} else {
			if (_Utils_eq(
				model.S,
				$elm$core$Maybe$Just(host))) {
				return current;
			} else {
				var _v0 = $author$project$Launch$disconnect(current);
				var retired = _v0;
				return $author$project$Launch$advance(
					_Utils_update(
						retired,
						{
							S: $elm$core$Maybe$Just(host)
						}));
			}
		}
	});
var $author$project$MenuBridge$Model = $elm$core$Basics$identity;
var $author$project$Menu$Model = $elm$core$Basics$identity;
var $author$project$Menu$Unknown = function (a) {
	return {$: 4, a: a};
};
var $author$project$Menu$markDisconnected = function (_v0) {
	var state = _v0;
	return _Utils_update(
		state,
		{
			ap: A2(
				$elm$core$Maybe$map,
				function (menu) {
					var _v1 = menu.x;
					if (_v1.$ === 1) {
						var intent = _v1.a;
						return _Utils_update(
							menu,
							{
								x: $author$project$Menu$Unknown(intent)
							});
					} else {
						return menu;
					}
				},
				state.ap),
			j: A2(
				$elm$core$List$map,
				function (entry) {
					return _Utils_update(
						entry,
						{aZ: true});
				},
				state.j)
		});
};
var $author$project$Menu$Cancelled = {$: 3};
var $author$project$Menu$Dispatch = F3(
	function (a, b, c) {
		return {$: 0, a: a, b: b, c: c};
	});
var $author$project$Menu$IntentId = $elm$core$Basics$identity;
var $author$project$Menu$MenuId = $elm$core$Basics$identity;
var $author$project$Menu$Pending = function (a) {
	return {$: 1, a: a};
};
var $author$project$Menu$Refused = function (a) {
	return {$: 2, a: a};
};
var $author$project$Menu$Uncertain = {$: 3};
var $author$project$Menu$awaits = F2(
	function (id, status) {
		switch (status.$) {
			case 1:
				var pending = status.a;
				return _Utils_eq(pending, id);
			case 4:
				var unknown = status.a;
				return _Utils_eq(unknown, id);
			default:
				return false;
		}
	});
var $author$project$Menu$Refusal = function (a) {
	return {$: 1, a: a};
};
var $author$project$Menu$maxLabel = 256;
var $author$project$Menu$boundedOutcome = function (outcome) {
	if (outcome.$ === 1) {
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
					return item.aF ? $elm$core$Maybe$Just(index) : $elm$core$Maybe$Nothing;
				}),
			items));
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
var $author$project$Menu$itemAt = F2(
	function (index, items) {
		return (index < 0) ? $elm$core$Maybe$Nothing : $elm$core$List$head(
			A2($elm$core$List$drop, index, items));
	});
var $author$project$Menu$maxOutstanding = 64;
var $author$project$Menu$maxRetired = 128;
var $author$project$Menu$orElse = F2(
	function (fallback, value) {
		if (!value.$) {
			return value;
		} else {
			return fallback;
		}
	});
var $author$project$Menu$navigate = F2(
	function (direction, menu) {
		var enabled = $author$project$Menu$enabledIndices(menu.aM);
		var first = $elm$core$List$head(enabled);
		var last = $elm$core$List$head(
			$elm$core$List$reverse(enabled));
		var selected = function () {
			switch (direction) {
				case 2:
					return first;
				case 3:
					return last;
				case 1:
					var _v1 = menu.aj;
					if (_v1.$ === 1) {
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
					var _v2 = menu.aj;
					if (_v2.$ === 1) {
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
			{aj: selected});
	});
var $author$project$Menu$outputTuple = function (_v0) {
	var value = _v0;
	return _Utils_Tuple2(value.v, value.cL);
};
var $author$project$Menu$sameTarget = F2(
	function (_v0, _v1) {
		var left = _v0;
		var right = _v1;
		return _Utils_eq(left.br, right.br);
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
					if (A2($elm$core$List$member, item.a1, seen)) {
						return false;
					} else {
						var $temp$remaining = rest,
							$temp$seen = A2($elm$core$List$cons, item.a1, seen);
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
				$elm$core$String$length(item.bP),
				$author$project$Menu$maxLabel) < 1) && (!$elm$core$String$isEmpty(
				$elm$core$String$trim(item.bP)));
		},
		items) && A2(uniqueActions, items, _List_Nil));
};
var $author$project$Menu$update = F2(
	function (message, model) {
		var state = model;
		var valid = function (target) {
			return (!A2($elm$core$List$member, target, state.T)) && (!A2(
				$elm$core$List$member,
				$author$project$Menu$outputTuple(target),
				state.Z));
		};
		var unchanged = _Utils_Tuple2(model, _List_Nil);
		var editMenu = F2(
			function (id, transform) {
				var _v8 = state.ap;
				if (!_v8.$) {
					var menu = _v8.a;
					return _Utils_eq(menu.bJ, id) ? _Utils_Tuple2(
						_Utils_update(
							state,
							{
								ap: transform(menu)
							}),
						_List_Nil) : unchanged;
				} else {
					return unchanged;
				}
			});
		switch (message.$) {
			case 0:
				var target = message.a;
				var items = message.b;
				if (state.F || ((!valid(target)) || ((!$author$project$Menu$validItems(items)) || (state.aR > 2147483647)))) {
					return unchanged;
				} else {
					var status = function () {
						var _v1 = $elm$core$List$head(
							A2(
								$elm$core$List$filter,
								function (entry) {
									return A2($author$project$Menu$sameTarget, entry.c, target);
								},
								state.j));
						if (_v1.$ === 1) {
							return $author$project$Menu$Ready;
						} else {
							var entry = _v1.a;
							return entry.aZ ? $author$project$Menu$Unknown(entry.bJ) : $author$project$Menu$Pending(entry.bJ);
						}
					}();
					var menu = {
						c: target,
						bJ: state.aR,
						aM: items,
						aj: $elm$core$List$head(
							$author$project$Menu$enabledIndices(items)),
						x: status
					};
					return _Utils_Tuple2(
						_Utils_update(
							state,
							{
								ap: $elm$core$Maybe$Just(menu),
								aR: state.aR + 1
							}),
						_List_Nil);
				}
			case 1:
				var id = message.a;
				var target = message.b;
				var index = message.c;
				return A2(
					editMenu,
					id,
					function (menu) {
						if (_Utils_eq(menu.c, target) && valid(target)) {
							var _v2 = A2($author$project$Menu$itemAt, index, menu.aM);
							if (!_v2.$) {
								var item = _v2.a;
								return item.aF ? $elm$core$Maybe$Just(
									_Utils_update(
										menu,
										{
											aj: $elm$core$Maybe$Just(index)
										})) : $elm$core$Maybe$Just(menu);
							} else {
								return $elm$core$Maybe$Just(menu);
							}
						} else {
							return $elm$core$Maybe$Just(menu);
						}
					});
			case 2:
				var id = message.a;
				var direction = message.b;
				return A2(
					editMenu,
					id,
					A2(
						$elm$core$Basics$composeR,
						$author$project$Menu$navigate(direction),
						$elm$core$Maybe$Just));
			case 3:
				var id = message.a;
				var target = message.b;
				var index = message.c;
				var _v3 = state.ap;
				if (_v3.$ === 1) {
					return unchanged;
				} else {
					var menu = _v3.a;
					if (state.F || ((!_Utils_eq(menu.bJ, id)) || ((!_Utils_eq(menu.c, target)) || ((!valid(target)) || (state.aQ > 2147483647))))) {
						return unchanged;
					} else {
						if (A2(
							$elm$core$List$any,
							function (entry) {
								return A2($author$project$Menu$sameTarget, entry.c, target);
							},
							state.j)) {
							return unchanged;
						} else {
							var _v4 = A2($author$project$Menu$itemAt, index, menu.aM);
							if (!_v4.$) {
								var item = _v4.a;
								if (item.aF && (_Utils_cmp(
									$elm$core$List$length(state.j),
									$author$project$Menu$maxOutstanding) > -1)) {
									return _Utils_Tuple2(
										_Utils_update(
											state,
											{
												ap: $elm$core$Maybe$Just(
													_Utils_update(
														menu,
														{
															x: $author$project$Menu$Refused('Outstanding operation limit reached; reconcile existing requests.')
														}))
											}),
										_List_Nil);
								} else {
									if (item.aF) {
										var intent = state.aQ;
										var entry = {c: target, bJ: intent, aZ: false};
										return _Utils_Tuple2(
											_Utils_update(
												state,
												{
													ap: $elm$core$Maybe$Just(
														_Utils_update(
															menu,
															{
																aj: $elm$core$Maybe$Just(index),
																x: $author$project$Menu$Pending(intent)
															})),
													aQ: state.aQ + 1,
													j: A2($elm$core$List$cons, entry, state.j)
												}),
											_List_fromArray(
												[
													A3($author$project$Menu$Dispatch, intent, target, item.a1)
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
			case 4:
				var intent = message.a;
				var receiptBinding = message.b;
				var receivedOutcome = message.c;
				var _v5 = $elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (entry) {
							return _Utils_eq(entry.bJ, intent) && _Utils_eq(entry.c, receiptBinding);
						},
						state.j));
				if (_v5.$ === 1) {
					return unchanged;
				} else {
					var entry = _v5.a;
					var outcome = $author$project$Menu$boundedOutcome(receivedOutcome);
					var outstanding = _Utils_eq(outcome, $author$project$Menu$Uncertain) ? A2(
						$elm$core$List$map,
						function (current) {
							return _Utils_eq(current.bJ, intent) ? _Utils_update(
								current,
								{aZ: true}) : current;
						},
						state.j) : A2(
						$elm$core$List$filter,
						function (current) {
							return !_Utils_eq(current.bJ, intent);
						},
						state.j);
					var menu = A2(
						$elm$core$Maybe$andThen,
						function (current) {
							if (!A2($author$project$Menu$awaits, intent, current.x)) {
								return $elm$core$Maybe$Just(current);
							} else {
								switch (outcome.$) {
									case 0:
										return $elm$core$Maybe$Nothing;
									case 1:
										var reason = outcome.a;
										return $elm$core$Maybe$Just(
											_Utils_update(
												current,
												{
													x: $author$project$Menu$Refused(reason)
												}));
									case 2:
										return $elm$core$Maybe$Just(
											_Utils_update(
												current,
												{x: $author$project$Menu$Cancelled}));
									default:
										return $elm$core$Maybe$Just(
											_Utils_update(
												current,
												{
													x: $author$project$Menu$Unknown(intent)
												}));
								}
							}
						},
						state.ap);
					return _Utils_Tuple2(
						_Utils_update(
							state,
							{
								aN: $elm$core$Maybe$Just(
									_Utils_Tuple2(intent, outcome)),
								ap: menu,
								j: outstanding
							}),
						_List_Nil);
				}
			case 5:
				var id = message.a;
				return A2(
					editMenu,
					id,
					function (_v7) {
						return $elm$core$Maybe$Nothing;
					});
			case 6:
				var target = message.a;
				if (A2($elm$core$List$member, target, state.T) || state.F) {
					return unchanged;
				} else {
					if (_Utils_cmp(
						$elm$core$List$length(state.T) + $elm$core$List$length(state.Z),
						$author$project$Menu$maxRetired) > -1) {
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{F: true, ap: $elm$core$Maybe$Nothing}),
							_List_Nil);
					} else {
						var menu = A2(
							$elm$core$Maybe$andThen,
							function (current) {
								return _Utils_eq(current.c, target) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(current);
							},
							state.ap);
						var invalidated = A2($elm$core$List$cons, target, state.T);
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{T: invalidated, ap: menu}),
							_List_Nil);
					}
				}
			default:
				var output = message.a;
				var generation = message.b;
				var retired = _Utils_Tuple2(output, generation);
				if (A2($elm$core$List$member, retired, state.Z) || state.F) {
					return unchanged;
				} else {
					if (_Utils_cmp(
						$elm$core$List$length(state.T) + $elm$core$List$length(state.Z),
						$author$project$Menu$maxRetired) > -1) {
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{F: true, ap: $elm$core$Maybe$Nothing}),
							_List_Nil);
					} else {
						var retiredOutputs = A2($elm$core$List$cons, retired, state.Z);
						var menu = A2(
							$elm$core$Maybe$andThen,
							function (current) {
								return _Utils_eq(
									$author$project$Menu$outputTuple(current.c),
									retired) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(current);
							},
							state.ap);
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{ap: menu, Z: retiredOutputs}),
							_List_Nil);
					}
				}
		}
	});
var $author$project$MenuBridge$connectionLost = function (_v0) {
	var state = _v0;
	var uncertain = $author$project$Menu$markDisconnected(state.ap);
	var closed = function () {
		var _v1 = $author$project$Menu$snapshot(uncertain).ap;
		if (_v1.$ === 1) {
			return uncertain;
		} else {
			var view = _v1.a;
			return A2(
				$author$project$Menu$update,
				$author$project$Menu$Dismiss(view.bJ),
				uncertain).a;
		}
	}();
	return _Utils_update(
		state,
		{ap: closed});
};
var $author$project$Menu$hasOutstandingFor = F2(
	function (window, _v0) {
		var state = _v0;
		return A2(
			$elm$core$List$any,
			function (entry) {
				var _v1 = entry.c;
				var value = _v1;
				return _Utils_eq(
					value.br,
					$author$project$Menu$Window(window));
			},
			state.j);
	});
var $author$project$MenuBridge$blockedFor = F3(
	function (incarnation, shell, _v0) {
		var state = _v0;
		var root = A2(
			$elm$core$Maybe$andThen,
			function (observed) {
				return A2($author$project$ActionProjection$rootOf, incarnation, observed.N);
			},
			shell.aE.aS);
		var blocked = function () {
			var _v1 = _Utils_Tuple2(shell.c, root);
			if ((!_v1.a.$) && (!_v1.b.$)) {
				var _native = _v1.a.a;
				var family = _v1.b.a;
				return A2(
					$author$project$Menu$hasOutstandingFor,
					A2(
						$author$project$Menu$windowId,
						$author$project$Binding$authorityIdentity(_native),
						$author$project$UInt64$string(family)),
					state.ap);
			} else {
				return $author$project$Menu$snapshot(state.ap).j > 0;
			}
		}();
		return blocked;
	});
var $author$project$Shell$Reconciling = 1;
var $author$project$Shell$RestartBackend = {$: 1};
var $author$project$Shell$Send = function (a) {
	return {$: 0, a: a};
};
var $author$project$Effects$Maximize = 3;
var $author$project$Effects$RestoreGeometry = 4;
var $author$project$Effects$Unknown = 4;
var $author$project$ActionProjection$actionable = F2(
	function (identity, projection) {
		return A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.bc;
				},
				A2(
					$author$project$ActionProjection$find,
					identity,
					$author$project$ActionProjection$windows(projection))));
	});
var $author$project$Effects$blocked = F3(
	function (lifetime, incarnation, model) {
		return A2(
			$elm$core$List$any,
			function (t) {
				return _Utils_eq(t.G.am.cF, lifetime) && (_Utils_eq(t.G.A, incarnation) && A2(
					$elm$core$List$member,
					t.x,
					_List_fromArray(
						[0, 4])));
			},
			model.f);
	});
var $author$project$Effects$Context = F4(
	function (lifetime, epoch, output, revision) {
		return {a4: epoch, cF: lifetime, v: output, cP: revision};
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
		return {$: 0, a: a, b: b, c: c, d: d};
	});
var $author$project$ActionProjection$Window = F6(
	function (incarnation, label, minimized, owner, application, available) {
		return {bb: application, bc: available, A: incarnation, bP: label, aq: minimized, bj: owner};
	});
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
		if (!_v0.$) {
			return $elm$json$Json$Decode$fail('Window bound');
		} else {
			return $elm$json$Json$Decode$list($author$project$ActionProjection$windowDecoder);
		}
	},
	$elm$json$Json$Decode$value);
var $author$project$ActionProjection$rootIn = F3(
	function (fuel, identity, rows) {
		return (fuel <= 0) ? $elm$core$Maybe$Nothing : A2(
			$elm$core$Maybe$andThen,
			function (w) {
				var _v0 = w.bj;
				if (_v0.$ === 1) {
					return $elm$core$Maybe$Just(w.A);
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
									return !w.aq;
								},
								A2($author$project$ActionProjection$find, identity, rows)));
					},
					focus));
			var unique = A3(
				$elm$core$List$foldl,
				F2(
					function (w, seen) {
						return A2($elm$core$List$member, w.A, seen) ? seen : A2($elm$core$List$cons, w.A, seen);
					}),
				_List_Nil,
				rows);
			var table = $elm$core$Dict$fromList(
				A2(
					$elm$core$List$map,
					function (w) {
						return _Utils_Tuple2(
							$author$project$UInt64$string(w.A),
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
										$author$project$UInt64$string(w.A),
										root,
										cache);
								}),
							accumulated,
							A3($author$project$ActionProjection$rootIn, 256, w.A, table));
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
							return _Utils_eq(root.aq, w.aq);
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
									$author$project$UInt64$string(w.A)),
								roots))));
			};
			if ((!_Utils_eq(
				$elm$core$List$length(unique),
				$elm$core$List$length(rows))) || ((!validFocus) || A2(
				$elm$core$List$any,
				function (w) {
					return !($author$project$ActionProjection$validText(w.bP) && ($author$project$ActionProjection$validText(w.bb) && validFamily(w)));
				},
				rows))) {
				return $elm$core$Result$Err('Incoherent ownership/focus projection');
			} else {
				if (!roots.$) {
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
		return {am: context, cx: generation, A: incarnation, ar: operation, a6: request};
	});
var $author$project$Effects$operationDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (name) {
		switch (name) {
			case 'minimize':
				return $elm$json$Json$Decode$succeed(0);
			case 'restore':
				return $elm$json$Json$Decode$succeed(1);
			case 'activate':
				return $elm$json$Json$Decode$succeed(2);
			case 'maximize':
				return $elm$json$Json$Decode$succeed(3);
			case 'restore-geometry':
				return $elm$json$Json$Decode$succeed(4);
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
var $author$project$Effects$protocol = function (operation) {
	return ((operation === 3) || (operation === 4)) ? 2 : 1;
};
var $author$project$ActionProjection$revision = function (_v0) {
	var value = _v0.a;
	return value;
};
var $author$project$Effects$sameAuthority = F2(
	function (a, b) {
		return _Utils_eq(a.cF, b.cF) && (_Utils_eq(a.a4, b.a4) && _Utils_eq(a.v, b.v));
	});
var $author$project$ActionProjection$sameState = F2(
	function (left, right) {
		var state = function (projection) {
			return A2(
				$elm$core$List$map,
				function (w) {
					return _Utils_Tuple3(
						w.A,
						_Utils_Tuple2(w.aq, w.bj),
						_Utils_Tuple2(w.bb, w.bc));
				},
				A2(
					$elm$core$List$sortWith,
					F2(
						function (a, b) {
							return A2($author$project$UInt64$compare, a.A, b.A);
						}),
					$author$project$ActionProjection$windows(projection)));
		};
		return _Utils_eq(
			$author$project$ActionProjection$focused(left),
			$author$project$ActionProjection$focused(right)) && _Utils_eq(
			state(left),
			state(right));
	});
var $author$project$Effects$Cancelled = 3;
var $author$project$Effects$Committed = 1;
var $author$project$Effects$Refused = 2;
var $author$project$Effects$statusDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (name) {
		switch (name) {
			case 'Committed':
				return $elm$json$Json$Decode$succeed(1);
			case 'Refused':
				return $elm$json$Json$Decode$succeed(2);
			case 'Cancelled':
				return $elm$json$Json$Decode$succeed(3);
			case 'Unknown':
				return $elm$json$Json$Decode$succeed(4);
			default:
				return $elm$json$Json$Decode$fail('Not an authoritative terminal outcome');
		}
	},
	$elm$json$Json$Decode$string);
var $author$project$Effects$unknown = $elm$core$Maybe$map(
	function (transaction) {
		return (!transaction.x) ? _Utils_update(
			transaction,
			{x: 4}) : transaction;
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
				if (_v10.$ === 1) {
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
		if (_v0.$ === 1) {
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
							if (_v2.$ === 1) {
								var error = _v2.a;
								return refuse(error);
							} else {
								var scene = _v2.a;
								if (!_Utils_eq(
									$author$project$ActionProjection$revision(scene),
									context.cP)) {
									return refuse('Scene/context revision mismatch');
								} else {
									var _v3 = model.aS;
									if (!_v3.$) {
										var old = _v3.a;
										return (A2($author$project$Effects$sameAuthority, old.am, context) && ((!A2($author$project$UInt64$compare, context.cP, old.am.cP)) || (_Utils_eq(context.cP, old.am.cP) && (!A2($author$project$ActionProjection$sameState, old.N, scene))))) ? refuse('Nonincreasing snapshot') : _Utils_Tuple3(
											_Utils_update(
												model,
												{
													R: true,
													aS: $elm$core$Maybe$Just(
														{am: context, N: scene}),
													r: A2($author$project$Effects$sameAuthority, old.am, context) ? model.r : $author$project$Effects$unknown(model.r)
												}),
											$elm$core$Maybe$Nothing,
											$elm$core$Maybe$Nothing);
									} else {
										return _Utils_Tuple3(
											_Utils_update(
												model,
												{
													R: true,
													aS: $elm$core$Maybe$Just(
														{am: context, N: scene})
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
								model.aS,
								$author$project$UInt64$next(model.a6),
								$author$project$UInt64$next(model.cx));
							if (((!_v5.a.$) && (!_v5.b.$)) && (!_v5.c.$)) {
								var observed = _v5.a.a;
								var request = _v5.b.a;
								var generation = _v5.c.a;
								if (!model.R) {
									return refuse('Disconnected');
								} else {
									if ($author$project$Effects$pending(model)) {
										return refuse('Operation already pending');
									} else {
										if ($elm$core$List$length(model.f) >= 64) {
											return refuse('Unresolved operation capacity');
										} else {
											if ((operation === 3) || (operation === 4)) {
												return refuse('Geometry observation required');
											} else {
												if (A3($author$project$Effects$blocked, observed.am.cF, incarnation, model)) {
													return refuse('Unresolved native operation');
												} else {
													if (!A2($author$project$ActionProjection$actionable, incarnation, observed.N)) {
														return refuse('Locked or unmapped target');
													} else {
														var _v6 = A2($author$project$ActionProjection$minimized, incarnation, observed.N);
														if (_v6.$ === 1) {
															return refuse('Unknown incarnation');
														} else {
															var minimized = _v6.a;
															if (((!operation) && minimized) || (((operation === 1) && (!minimized)) || ((operation === 2) && minimized))) {
																return refuse('Already in requested native state');
															} else {
																var intent = {am: observed.am, cx: generation, A: incarnation, ar: operation, a6: request};
																return _Utils_Tuple3(
																	_Utils_update(
																		model,
																		{
																			cx: generation,
																			a6: request,
																			r: $elm$core$Maybe$Just(
																				{aa: 1, G: intent, x: 0}),
																			f: A2(
																				$elm$core$List$cons,
																				{aa: 1, G: intent, x: 0},
																				model.f)
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
								return _Utils_eq(t.aa, protocolId) && _Utils_eq(t.G, intent);
							};
							var found = A2($elm$core$List$any, exact, model.f);
							var settled = function (t) {
								return exact(t) ? _Utils_update(
									t,
									{x: status}) : t;
							};
							var unresolved = (status === 4) ? A2($elm$core$List$map, settled, model.f) : A2(
								$elm$core$List$filter,
								A2($elm$core$Basics$composeR, exact, $elm$core$Basics$not),
								model.f);
							return ((!found) || ((!A2(
								$elm$core$List$member,
								protocolId,
								_List_fromArray(
									[1, 2]))) || (!_Utils_eq(
								$author$project$Effects$protocol(intent.ar),
								protocolId)))) ? refuse('Stale, mismatched or terminal receipt') : _Utils_Tuple3(
								_Utils_update(
									model,
									{
										r: A2(
											$elm$core$Maybe$map,
											function (t) {
												return A2(
													$elm$core$Maybe$withDefault,
													false,
													A2(
														$elm$core$Maybe$map,
														function (observed) {
															return A2($author$project$Effects$sameAuthority, observed.am, intent.am);
														},
														model.aS)) ? settled(t) : t;
											},
											model.r),
										f: unresolved
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
						function (_v8) {
							var intent = _v8.a;
							var protocolId = _v8.b;
							if ((!A2(
								$elm$core$List$member,
								protocolId,
								_List_fromArray(
									[1, 2]))) || (!_Utils_eq(
								$author$project$Effects$protocol(intent.ar),
								protocolId))) {
								return refuse('Recovery operation protocol');
							} else {
								if (A2(
									$elm$core$List$any,
									function (t) {
										return _Utils_eq(t.G, intent) && _Utils_eq(t.aa, protocolId);
									},
									model.f)) {
									return _Utils_Tuple3(model, $elm$core$Maybe$Nothing, $elm$core$Maybe$Nothing);
								} else {
									if ($elm$core$List$length(model.f) >= 64) {
										return refuse('Unresolved operation capacity');
									} else {
										var transaction = {aa: protocolId, G: intent, x: 4};
										var maximum = F2(
											function (old, _new) {
												return (!A2($author$project$UInt64$compare, old, _new)) ? _new : old;
											});
										return _Utils_Tuple3(
											_Utils_update(
												model,
												{
													cx: A2(maximum, model.cx, intent.cx),
													a6: A2(maximum, model.a6, intent.a6),
													r: $elm$core$Maybe$Just(transaction),
													f: A2($elm$core$List$cons, transaction, model.f)
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
							$elm$json$Json$Decode$succeed(0)),
						function (_v9) {
							return _Utils_Tuple3(
								_Utils_update(
									model,
									{
										R: false,
										r: $author$project$Effects$unknown(model.r),
										f: A2(
											$elm$core$List$map,
											function (t) {
												return (!t.x) ? _Utils_update(
													t,
													{x: 4}) : t;
											},
											model.f)
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
					return A2($author$project$ActionProjection$actionable, incarnation, legacy.N) && _Utils_eq(
						A2($author$project$ActionProjection$rootOf, incarnation, legacy.N),
						$elm$core$Maybe$Just(incarnation));
				},
				model.aS));
		var _v0 = _Utils_Tuple3(
			A2($author$project$GeometryProjection$window, incarnation, observed),
			$author$project$UInt64$next(model.a6),
			$author$project$UInt64$next(model.cx));
		if (((!_v0.a.$) && (!_v0.b.$)) && (!_v0.c.$)) {
			var window = _v0.a.a;
			var request = _v0.b.a;
			var generation = _v0.c.a;
			if ((!model.R) || ((!legacyReady) || ($author$project$Effects$pending(model) || A3($author$project$Effects$blocked, observed.am.cF, incarnation, model)))) {
				return refuse('Unresolved or disconnected native operation');
			} else {
				if ($elm$core$List$length(model.f) >= 64) {
					return refuse('Unresolved operation capacity');
				} else {
					if (($author$project$Effects$protocol(operation) !== 2) || ((!caps.aE) || (!A2(
						$elm$core$List$member,
						$author$project$Effects$operationName(operation),
						caps.cK)))) {
						return refuse('Geometry operation not negotiated');
					} else {
						if ((!window.cu) || (window.aq || (window.cw || window.cr))) {
							return refuse('Geometry target ineligible');
						} else {
							if (((operation === 3) && ((!window.cG) || (!(!window.bV)))) || ((operation === 4) && ((!window.cN) || ((window.bV !== 1) || (!window.cM))))) {
								return refuse('Geometry state/capability unavailable');
							} else {
								var intent = {am: observed.am, cx: generation, A: incarnation, ar: operation, a6: request};
								var transaction = {aa: 2, G: intent, x: 0};
								return _Utils_Tuple3(
									_Utils_update(
										model,
										{
											cx: generation,
											a6: request,
											r: $elm$core$Maybe$Just(transaction),
											f: A2($elm$core$List$cons, transaction, model.f)
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
var $author$project$GeometryProjection$exact = F3(
	function (name, child, value) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (x) {
				return _Utils_eq(x, value) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Geometry version');
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
		return (($elm$core$List$length(caps.cK) <= 2) && (A2(
			$elm$core$List$all,
			function (op) {
				return A2(
					$elm$core$List$member,
					op,
					_List_fromArray(
						['maximize', 'restore-geometry']));
			},
			caps.cK) && (_Utils_eq(
			$elm$core$List$length(caps.cK),
			$elm$core$List$length(
				A3(
					$elm$core$List$foldl,
					F2(
						function (x, xs) {
							return A2($elm$core$List$member, x, xs) ? xs : A2($elm$core$List$cons, x, xs);
						}),
					_List_Nil,
					caps.cK))) && _Utils_eq(
			caps.aE,
			!$elm$core$List$isEmpty(caps.cK))))) ? $elm$json$Json$Decode$succeed(caps) : $elm$json$Json$Decode$fail('Geometry capabilities');
	},
	A2(
		$author$project$GeometryProjection$strict,
		_List_fromArray(
			['observe', 'effects', 'effectProtocol', 'operations', 'placementCapacity', 'canonicalScene']),
		A7(
			$elm$json$Json$Decode$map6,
			F6(
				function (_v0, effects, _v1, operations, _v2, _v3) {
					return {aE: effects, cK: operations};
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
var $author$project$Shell$captureGeometry = function (model) {
	return A2(
		$elm$core$Maybe$map,
		function (observed) {
			return A3($author$project$Shell$Stamp, observed.c, observed.am.v, observed.am.cP);
		},
		model.bG);
};
var $elm$json$Json$Decode$map8 = _Json_map8;
var $author$project$GeometryProjection$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (x) {
		return _Utils_eq(x, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero geometry identity') : $elm$json$Json$Decode$succeed(x);
	},
	$author$project$UInt64$decoder);
var $author$project$GeometryProjection$Fullscreen = 2;
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
									return _Utils_eq(row.A, id);
								},
								rows));
						if (_v0.$ === 1) {
							return false;
						} else {
							var row = _v0.a;
							var _v1 = row.bj;
							if (_v1.$ === 1) {
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
			var ownership = function () {
				var _v2 = row.bj;
				if (_v2.$ === 1) {
					return true;
				} else {
					return A2(walk, _List_Nil, row.A);
				}
			}();
			var known = A2(
				$elm$core$List$map,
				$elm$core$Basics$identity,
				_List_fromArray(
					[
						!_Utils_eq(row.az, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.aA, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.aP, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.V, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.a0, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.a$, $elm$core$Maybe$Nothing)
					]));
			var paired = A2(
				$elm$core$List$all,
				$elm$core$Basics$eq(true),
				known) || A2(
				$elm$core$List$all,
				$elm$core$Basics$eq(false),
				known);
			var eligible = (!row.cu) || ((!_Utils_eq(row.az, $elm$core$Maybe$Nothing)) && ((!blocked) && ((!row.aq) && ((!row.aK) && ((!row.cr) && (row.aI && (_Utils_eq(row.bj, $elm$core$Maybe$Nothing) && (_Utils_eq(row.bV, row.bf) && (row.bV !== 2)))))))));
			return paired && (eligible && (ownership && (((!row.cG) || A2($elm$core$List$member, 'maximize', caps.cK)) && ((!row.cN) || A2($elm$core$List$member, 'restore-geometry', caps.cK)))));
		};
		var ids = A2(
			$elm$core$List$map,
			function ($) {
				return $.A;
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
				return (_Utils_eq(a.V, $elm$core$Maybe$Nothing) || ((!_Utils_eq(a.V, b.V)) || _Utils_eq(a.aP, b.aP))) && (_Utils_eq(a.aA, $elm$core$Maybe$Nothing) || ((!_Utils_eq(a.aA, b.aA)) || (_Utils_eq(a.az, b.az) && (_Utils_eq(a.V, b.V) && (_Utils_eq(a.a0, b.a0) && _Utils_eq(a.a$, b.a$))))));
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
var $author$project$GeometryProjection$modeDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (x) {
		switch (x) {
			case 'ordinary':
				return $elm$json$Json$Decode$succeed(0);
			case 'maximized':
				return $elm$json$Json$Decode$succeed(1);
			case 'fullscreen':
				return $elm$json$Json$Decode$succeed(2);
			default:
				return $elm$json$Json$Decode$fail('Geometry mode');
		}
	},
	$elm$json$Json$Decode$string);
var $elm$json$Json$Decode$float = _Json_decodeFloat;
var $elm$core$Basics$isInfinite = _Basics_isInfinite;
var $elm$core$Basics$isNaN = _Basics_isNaN;
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
var $author$project$GeometryProjection$windowDecoder = function () {
	var state = A9(
		$elm$json$Json$Decode$map8,
		F8(
			function (logical, visual, _native, client, minimized, floating, grouped, fixed) {
				return {bw: client, bD: fixed, aI: floating, aK: grouped, bQ: logical, aq: minimized, bU: _native, cd: visual};
			}),
		A2($elm$json$Json$Decode$field, 'logicalGeometry', $author$project$GeometryProjection$rect),
		A2($elm$json$Json$Decode$field, 'visualGeometry', $author$project$GeometryProjection$rect),
		A2($elm$json$Json$Decode$field, 'nativeMode', $author$project$GeometryProjection$modeDecoder),
		A2($elm$json$Json$Decode$field, 'clientMode', $author$project$GeometryProjection$modeDecoder),
		A2($elm$json$Json$Decode$field, 'minimized', $elm$json$Json$Decode$bool),
		A2($elm$json$Json$Decode$field, 'floating', $elm$json$Json$Decode$bool),
		A2($elm$json$Json$Decode$field, 'grouped', $elm$json$Json$Decode$bool),
		A2($elm$json$Json$Decode$field, 'fixedSize', $elm$json$Json$Decode$bool));
	var policy = A5(
		$elm$json$Json$Decode$map4,
		F4(
			function (constrained, eligible, known, caps) {
				return {be: caps, bx: constrained, cu: eligible, bO: known};
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
					A2($elm$json$Json$Decode$field, 'restoreGeometry', $elm$json$Json$Decode$bool)))));
	var identities = A9(
		$elm$json$Json$Decode$map8,
		F8(
			function (inc, owner, ws, wg, mon, og, wr, wa) {
				return {bL: inc, bS: mon, bX: og, bj: owner, cf: wa, cg: wg, ci: wr, cj: ws};
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
		_List_fromArray(
			['incarnation', 'owner', 'workspace', 'workspaceGeneration', 'monitor', 'outputOwnershipGeneration', 'workAreaRevision', 'workArea', 'logicalGeometry', 'visualGeometry', 'nativeMode', 'clientMode', 'minimized', 'floating', 'grouped', 'fixedSize', 'constrainedSize', 'geometryEligible', 'ordinaryPlacementKnown', 'capabilities']),
		A4(
			$elm$json$Json$Decode$map3,
			F3(
				function (i, s, p) {
					return {bf: s.bw, cr: p.bx, cu: p.cu, cw: s.bD, aI: s.aI, aK: s.aK, A: i.bL, bR: s.bQ, cG: p.be.a, aq: s.aq, aP: i.bS, bV: s.bU, V: i.bX, bj: i.bj, cM: p.bO, cN: p.be.b, ce: s.cd, a$: i.cf, a0: i.ci, az: i.cj, aA: i.cg};
				}),
			identities,
			state,
			policy));
}();
var $author$project$GeometryProjection$decoder = function (caps) {
	return A2(
		$elm$json$Json$Decode$andThen,
		function (snapshot) {
			return (A3($author$project$GeometryProjection$validRows, caps, snapshot.aC, snapshot.a) && A2(
				$elm$core$Maybe$withDefault,
				true,
				A2(
					$elm$core$Maybe$map,
					function (id) {
						return A2(
							$elm$core$List$any,
							function (row) {
								return _Utils_eq(row.A, id);
							},
							snapshot.a);
					},
					snapshot.aJ))) ? $elm$json$Json$Decode$succeed(snapshot) : $elm$json$Json$Decode$fail('Geometry facts coherence');
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
							if (!_v4.$) {
								var _v5 = _v4.a;
								var life = _v5.a;
								var epoch = _v5.b;
								return {a4: epoch, cF: life, v: output, cP: revision};
							} else {
								return {a4: $author$project$UInt64$zero, cF: $author$project$UInt64$zero, v: output, cP: revision};
							}
						}();
						return {c: binding, aC: facts.aC, am: context, aJ: facts.aJ, a6: request, b5: sequence, a: facts.a};
					}),
				A3($author$project$GeometryProjection$exact, 'protocolVersion', $elm$json$Json$Decode$int, 3),
				A3($author$project$GeometryProjection$exact, 'kind', $elm$json$Json$Decode$string, 'geometry-facts'),
				A3($author$project$GeometryProjection$exact, 'geometryProtocol', $elm$json$Json$Decode$int, 1),
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
										return {aC: blocked, aJ: focus, a: rows};
									}),
								A2(
									$elm$json$Json$Decode$field,
									'focused',
									$elm$json$Json$Decode$nullable($author$project$GeometryProjection$positive)),
								A2($elm$json$Json$Decode$field, 'inputBlocked', $elm$json$Json$Decode$bool),
								A2(
									$elm$json$Json$Decode$field,
									'windows',
									$elm$json$Json$Decode$list($author$project$GeometryProjection$windowDecoder)))))))));
};
var $author$project$GeometryProjection$decode = F2(
	function (caps, raw) {
		return A2(
			$elm$core$Result$mapError,
			function (_v0) {
				return 'Invalid geometry projection';
			},
			A2(
				$elm$json$Json$Decode$decodeValue,
				$author$project$GeometryProjection$decoder(caps),
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
		model.aE);
	var effects = _v0.a;
	return _Utils_update(
		model,
		{
			aE: effects,
			k: $elm$core$Maybe$Nothing,
			bG: $elm$core$Maybe$Nothing,
			cy: $elm$core$Maybe$Nothing,
			cz: $elm$core$Maybe$Nothing,
			cA: $elm$core$Maybe$Nothing,
			n: A2(
				$elm$core$Maybe$withDefault,
				'Connection lost. Reconnect to continue.',
				A2($elm$core$Maybe$map, $author$project$Shell$recoveryNotice, model.au)),
			ad: false,
			aU: 0,
			Y: false
		});
};
var $author$project$Shell$geometryRequest = F2(
	function (attach, model) {
		var _v0 = _Utils_Tuple2(
			model.c,
			$author$project$UInt64$next(model.a6));
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var binding = _v0.a.a;
			var request = _v0.b.a;
			if ((!model.aU) || ((attach && (!_Utils_eq(model.cy, $elm$core$Maybe$Nothing))) || ((!attach) && (_Utils_eq(model.cz, $elm$core$Maybe$Nothing) || (!_Utils_eq(model.cA, $elm$core$Maybe$Nothing)))))) {
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
						$elm$json$Json$Encode$int(1)),
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
												return $.b5;
											},
											$author$project$UInt64$string),
										model.bG))))
						]));
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							cy: attach ? $elm$core$Maybe$Just(request) : model.cy,
							cA: attach ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(request),
							a6: request
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
	});
var $author$project$Shell$geometrySupported = function (model) {
	return A2(
		$elm$core$Maybe$withDefault,
		false,
		A2(
			$elm$core$Maybe$map,
			function ($) {
				return $.aE;
			},
			model.cz));
};
var $author$project$Shell$refresh = function (model) {
	var _v0 = _Utils_Tuple2(
		model.c,
		$author$project$UInt64$next(model.a6));
	if ((!_v0.a.$) && (!_v0.b.$)) {
		var binding = _v0.a.a;
		var request = _v0.b.a;
		return (!model.aU) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
			_Utils_update(
				model,
				{
					k: $elm$core$Maybe$Just(request),
					aU: 1,
					a6: request
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
				{k: $elm$core$Maybe$Nothing, n: 'Restart the shell to continue.', aU: 3}),
			_List_Nil);
	}
};
var $author$project$Shell$refreshObservations = function (model) {
	var _v0 = $author$project$Shell$refresh(
		_Utils_update(
			model,
			{ad: false}));
	var legacy = _v0.a;
	var commands = _v0.b;
	if ($author$project$Shell$geometrySupported(legacy)) {
		var _v1 = A2($author$project$Shell$geometryRequest, false, legacy);
		var geometry = _v1.a;
		var geometryCommands = _v1.b;
		return _Utils_Tuple2(
			geometry,
			_Utils_ap(commands, geometryCommands));
	} else {
		return _Utils_Tuple2(legacy, commands);
	}
};
var $author$project$Shell$drainNotifications = function (model) {
	return (model.ad && ((model.aU === 2) && ((!$author$project$Effects$pending(model.aE)) && (_Utils_eq(model.k, $elm$core$Maybe$Nothing) && (_Utils_eq(model.cA, $elm$core$Maybe$Nothing) && _Utils_eq(model.cy, $elm$core$Maybe$Nothing)))))) ? $author$project$Shell$refreshObservations(model) : _Utils_Tuple2(model, _List_Nil);
};
var $author$project$Shell$notificationRefresh = function (model) {
	return ((!model.aU) || (model.aU === 3)) ? _Utils_Tuple2(model, _List_Nil) : (($author$project$Effects$pending(model.aE) || ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(model.cA, $elm$core$Maybe$Nothing)) || (!_Utils_eq(model.cy, $elm$core$Maybe$Nothing))))) ? _Utils_Tuple2(
		_Utils_update(
			model,
			{ad: true}),
		_List_Nil) : $author$project$Shell$refreshObservations(model));
};
var $author$project$Shell$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (!_Utils_eq(value, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Zero displayed scope');
	},
	$author$project$UInt64$decoder);
var $author$project$Shell$Busy = 2;
var $author$project$Shell$Full = 1;
var $author$project$Shell$LegacyOwner = 4;
var $author$project$Shell$Unavailable = 0;
var $author$project$Shell$Unverified = 3;
var $author$project$Shell$recoveryDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (reason) {
		switch (reason) {
			case 'unavailable':
				return $elm$json$Json$Decode$succeed(0);
			case 'full':
				return $elm$json$Json$Decode$succeed(1);
			case 'busy':
				return $elm$json$Json$Decode$succeed(2);
			case 'unverified':
				return $elm$json$Json$Decode$succeed(3);
			case 'legacy-owner':
				return $elm$json$Json$Decode$succeed(4);
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
		return (!_Utils_eq(life, oldLife)) || ((!_Utils_eq(session, oldSession)) || (A2($author$project$UInt64$compare, frontend, oldFrontend) === 2));
	});
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
var $author$project$NativeOutcome$exact = F3(
	function (name, child, expected) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (value) {
				return _Utils_eq(value, expected) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Outcome protocol');
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
				return 0;
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
					return 0;
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
							['maximize', 'restore-geometry'])) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Outcome operation');
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
					return 0;
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
							['Committed', 'Refused', 'Unknown'])) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Outcome status');
				},
				A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string)),
			A2(
				$elm$json$Json$Decode$andThen,
				function (value) {
					return ($elm$core$String$length(value) <= 256) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Outcome reason');
				},
				A2($elm$json$Json$Decode$field, 'reason', $elm$json$Json$Decode$string)),
			A3(
				$elm$json$Json$Decode$map2,
				F2(
					function (_v8, _v9) {
						return 0;
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
	if (!_v0.$) {
		return true;
	} else {
		return false;
	}
};
var $author$project$Shell$version = A2(
	$elm$json$Json$Decode$andThen,
	function (v) {
		return (v === 3) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Protocol version');
	},
	A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int));
var $author$project$Shell$update = F2(
	function (msg, model) {
		switch (msg.$) {
			case 1:
				return ((!model.aU) || $author$project$Effects$pending(model.aE)) ? _Utils_Tuple2(model, _List_Nil) : ($author$project$Shell$geometrySupported(model) ? $author$project$Shell$notificationRefresh(model) : $author$project$Shell$refresh(model));
			case 2:
				return ((!model.aU) && (!model.Y)) ? _Utils_Tuple2(
					_Utils_update(
						model,
						{n: 'Reconnecting…', Y: true}),
					_List_fromArray(
						[$author$project$Shell$RestartBackend])) : _Utils_Tuple2(model, _List_Nil);
			case 3:
				return _Utils_Tuple2(model, _List_Nil);
			case 4:
				return A2($author$project$Shell$geometryRequest, true, model);
			case 5:
				return A2($author$project$Shell$geometryRequest, false, model);
			case 6:
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
								{n: 'Window list changed. Choose again.'}),
							_List_Nil);
					} else {
						var _v1 = function () {
							if ($author$project$Effects$protocol(operation) === 2) {
								var _v2 = _Utils_Tuple2(model.cz, model.bG);
								if ((!_v2.a.$) && (!_v2.b.$)) {
									var caps = _v2.a.a;
									var observed = _v2.b.a;
									return ((!_Utils_eq(model.cA, $elm$core$Maybe$Nothing)) || (!_Utils_eq(model.cy, $elm$core$Maybe$Nothing))) ? _Utils_Tuple3(
										model.aE,
										$elm$core$Maybe$Nothing,
										$elm$core$Maybe$Just('Geometry refresh pending')) : A5($author$project$Effects$beginGeometry, caps, observed, operation, incarnation, model.aE);
								} else {
									return _Utils_Tuple3(
										model.aE,
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
									model.aE);
							}
						}();
						var effects = _v1.a;
						var command = _v1.b;
						var error = _v1.c;
						var commands = function () {
							var _v4 = _Utils_Tuple2(command, model.c);
							if ((!_v4.a.$) && (!_v4.b.$)) {
								var value = _v4.a.a;
								var binding = _v4.b.a;
								var _v5 = A2(
									$elm$json$Json$Decode$decodeValue,
									A2($elm$json$Json$Decode$field, 'intent', $elm$json$Json$Decode$value),
									value);
								if (!_v5.$) {
									var intent = _v5.a;
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
									aE: effects,
									H: function () {
										var _v3 = _Utils_Tuple3(command, model.c, effects.r);
										if (((!_v3.a.$) && (!_v3.b.$)) && (!_v3.c.$)) {
											var binding = _v3.b.a;
											var transaction = _v3.c.a;
											return A2(
												$elm$core$List$cons,
												{c: binding, G: transaction.G, bl: transaction.aa},
												model.H);
										} else {
											return model.H;
										}
									}(),
									n: A2($elm$core$Maybe$withDefault, model.n, error)
								}),
							commands);
					}
				}
			default:
				var raw = msg.a;
				var _v6 = A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
					raw);
				_v6$11:
				while (true) {
					if (!_v6.$) {
						switch (_v6.a) {
							case 'host-recovery-failed':
								var _v7 = A2(
									$elm$json$Json$Decode$decodeValue,
									A2(
										$author$project$Shell$strict,
										_List_fromArray(
											['protocolVersion', 'kind', 'reason']),
										A3(
											$elm$json$Json$Decode$map2,
											F2(
												function (_v8, reason) {
													return reason;
												}),
											$author$project$Shell$version,
											A2($elm$json$Json$Decode$field, 'reason', $author$project$Shell$recoveryDecoder))),
									raw);
								if (!_v7.$) {
									var reason = _v7.a;
									var detached = $author$project$Shell$disconnect(model);
									return _Utils_Tuple2(
										_Utils_update(
											detached,
											{
												n: $author$project$Shell$recoveryNotice(reason),
												au: $elm$core$Maybe$Just(reason)
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
								var _v9 = A2(
									$elm$json$Json$Decode$decodeValue,
									A2(
										$author$project$Shell$strict,
										_List_fromArray(
											['protocolVersion', 'kind']),
										$author$project$Shell$version),
									raw);
								if (!_v9.$) {
									return $author$project$Shell$notificationRefresh(model);
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'attached':
								var _v10 = A2(
									$elm$json$Json$Decode$decodeValue,
									A3(
										$elm$json$Json$Decode$map2,
										F2(
											function (_v11, binding) {
												return binding;
											}),
										$author$project$Shell$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder)),
									raw);
								if (!_v10.$) {
									var binding = _v10.a;
									if ((!(!model.aU)) || ((!model.Y) || A2(
										$elm$core$Maybe$withDefault,
										false,
										A2(
											$elm$core$Maybe$map,
											A2(
												$elm$core$Basics$composeR,
												$author$project$Binding$replaces(binding),
												$elm$core$Basics$not),
											model.c)))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var detached = $author$project$Shell$disconnect(model);
										return $author$project$Shell$refresh(
											_Utils_update(
												detached,
												{
													c: $elm$core$Maybe$Just(binding),
													n: 'Updating window information…',
													aU: 1,
													Y: false,
													au: $elm$core$Maybe$Nothing
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
											function (_v17, binding, request, life, epoch) {
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
								var _v12 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v12.$) {
									var _v13 = _v12.a;
									var binding = _v13.a;
									var request = _v13.b;
									var _v14 = _v13.c;
									var life = _v14.a;
									var epoch = _v14.b;
									if ((!model.aU) || ((!_Utils_eq(
										model.c,
										$elm$core$Maybe$Just(binding))) || ((!_Utils_eq(
										model.k,
										$elm$core$Maybe$Just(request))) || (!A3($author$project$Binding$matchesContext, life, epoch, binding))))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var _v15 = A2(
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
										if (!_v15.$) {
											var snapshot = _v15.a;
											var _v16 = A2($author$project$Effects$apply, snapshot, model.aE);
											var effects = _v16.a;
											var error = _v16.c;
											return $author$project$Shell$drainNotifications(
												_Utils_update(
													model,
													{
														aE: effects,
														k: _Utils_eq(error, $elm$core$Maybe$Nothing) ? $elm$core$Maybe$Nothing : model.k,
														n: _Utils_eq(error, $elm$core$Maybe$Nothing) ? 'Connected' : 'Window information could not be verified.',
														aU: _Utils_eq(error, $elm$core$Maybe$Nothing) ? 2 : 1
													}));
										} else {
											return _Utils_Tuple2(model, _List_Nil);
										}
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'host-geometry-negotiate':
								var _v18 = A2(
									$elm$json$Json$Decode$decodeValue,
									A2(
										$author$project$Shell$strict,
										_List_fromArray(
											['protocolVersion', 'kind']),
										$author$project$Shell$version),
									raw);
								if (_v18.$ === 1) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									return ((!_Utils_eq(model.cz, $elm$core$Maybe$Nothing)) || (!_Utils_eq(model.cy, $elm$core$Maybe$Nothing))) ? _Utils_Tuple2(model, _List_Nil) : A2($author$project$Shell$geometryRequest, true, model);
								}
							case 'geometry-unavailable':
								var decoder = A2(
									$author$project$Shell$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'reason']),
									A5(
										$elm$json$Json$Decode$map4,
										F4(
											function (_v20, binding, request, reason) {
												return {c: binding, a5: reason, a6: request};
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
								var _v19 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (_v19.$ === 1) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var refusal = _v19.a;
									return ((!_Utils_eq(
										model.c,
										$elm$core$Maybe$Just(refusal.c))) || (!_Utils_eq(
										model.cy,
										$elm$core$Maybe$Just(refusal.a6)))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$drainNotifications(
										_Utils_update(
											model,
											{
												bG: $elm$core$Maybe$Nothing,
												cy: $elm$core$Maybe$Nothing,
												cz: $elm$core$Maybe$Just(
													{aE: false, cK: _List_Nil}),
												cA: $elm$core$Maybe$Nothing
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
											function (_v22, _v23, binding, request, caps) {
												return {c: binding, be: caps, a6: request};
											}),
										$author$project$Shell$version,
										A2(
											$elm$json$Json$Decode$andThen,
											function (v) {
												return (v === 1) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Geometry protocol');
											},
											A2($elm$json$Json$Decode$field, 'geometryProtocol', $elm$json$Json$Decode$int)),
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$Shell$positive),
										A2($elm$json$Json$Decode$field, 'capabilities', $author$project$GeometryProjection$capabilitiesDecoder)));
								var _v21 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v21.$) {
									var value = _v21.a;
									return ((!_Utils_eq(
										model.c,
										$elm$core$Maybe$Just(value.c))) || ((!_Utils_eq(
										model.cy,
										$elm$core$Maybe$Just(value.a6))) || (!model.aU))) ? _Utils_Tuple2(model, _List_Nil) : A2(
										$author$project$Shell$geometryRequest,
										false,
										_Utils_update(
											model,
											{
												bG: $elm$core$Maybe$Nothing,
												cy: $elm$core$Maybe$Nothing,
												cz: $elm$core$Maybe$Just(value.be)
											}));
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'geometry-facts':
								var _v24 = model.cz;
								if (_v24.$ === 1) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var caps = _v24.a;
									var _v25 = A2($author$project$GeometryProjection$decode, caps, raw);
									if (_v25.$ === 1) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var observed = _v25.a;
										var newer = function () {
											var _v26 = model.bG;
											if (_v26.$ === 1) {
												return true;
											} else {
												var old = _v26.a;
												return (_Utils_eq(old.am.cF, observed.am.cF) && _Utils_eq(old.am.a4, observed.am.a4)) ? ((!(!A2($author$project$UInt64$compare, observed.am.v, old.am.v))) && ((!(!A2($author$project$UInt64$compare, observed.b5, old.b5))) && ((!(!A2($author$project$UInt64$compare, observed.am.cP, old.am.cP))) && ((!_Utils_eq(observed.am.cP, old.am.cP)) || _Utils_eq(
													observed,
													_Utils_update(
														old,
														{a6: observed.a6, b5: observed.b5})))))) : true;
											}
										}();
										return ((!_Utils_eq(
											model.c,
											$elm$core$Maybe$Just(observed.c))) || ((!_Utils_eq(
											model.cA,
											$elm$core$Maybe$Just(observed.a6))) || ((!model.aU) || (!newer)))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$drainNotifications(
											_Utils_update(
												model,
												{
													bG: $elm$core$Maybe$Just(observed),
													cA: $elm$core$Maybe$Nothing
												}));
									}
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
													function (_v30, binding, intent) {
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
													function (_v31, binding, intent, protocolId) {
														return _Utils_Tuple3(binding, intent, protocolId);
													}),
												$author$project$Shell$version,
												A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
												A2($elm$json$Json$Decode$field, 'intent', $elm$json$Json$Decode$value),
												A2($elm$json$Json$Decode$field, 'effectProtocol', $elm$json$Json$Decode$int)))
										]));
								var _v27 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v27.$) {
									var _v28 = _v27.a;
									var binding = _v28.a;
									var intent = _v28.b;
									var protocolId = _v28.c;
									if ((!_Utils_eq(
										model.c,
										$elm$core$Maybe$Just(binding))) || ((model.aU !== 1) || (!_Utils_eq(
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
										var _v29 = A2(
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
											model.aE);
										var effects = _v29.a;
										var error = _v29.c;
										return (!_Utils_eq(error, $elm$core$Maybe$Nothing)) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
											_Utils_update(
												model,
												{aE: effects, n: 'The previous window change could not be confirmed.'}),
											_List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'effect-outcome':
								if (!$author$project$NativeOutcome$valid(raw)) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var _v32 = A2(
										$elm$json$Json$Decode$decodeValue,
										A5(
											$elm$json$Json$Decode$map4,
											F4(
												function (_v33, binding, protocolId, receipt) {
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
									if (!_v32.$) {
										var _v34 = _v32.a;
										var binding = _v34.a;
										var protocolId = _v34.b;
										var receipt = _v34.c;
										var receivedIntent = $elm$core$Result$toMaybe(
											A2(
												$elm$json$Json$Decode$decodeValue,
												A2($elm$json$Json$Decode$field, 'intent', $author$project$Effects$intentDecoder),
												raw));
										var exact = function (entry) {
											return _Utils_eq(entry.c, binding) && (_Utils_eq(entry.bl, protocolId) && _Utils_eq(
												$elm$core$Maybe$Just(entry.G),
												receivedIntent));
										};
										var known = A2($elm$core$List$any, exact, model.H);
										if (!known) {
											return _Utils_Tuple2(model, _List_Nil);
										} else {
											var retained = _Utils_eq(
												A2(
													$elm$json$Json$Decode$decodeValue,
													A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string),
													raw),
												$elm$core$Result$Ok('Unknown')) ? model.H : A2(
												$elm$core$List$filter,
												A2($elm$core$Basics$composeR, exact, $elm$core$Basics$not),
												model.H);
											var _v35 = A2($author$project$Effects$apply, receipt, model.aE);
											var effects = _v35.a;
											var error = _v35.c;
											if (!_Utils_eq(error, $elm$core$Maybe$Nothing)) {
												return _Utils_Tuple2(model, _List_Nil);
											} else {
												var current = function () {
													var _v36 = model.aE.r;
													if (_v36.$ === 1) {
														return false;
													} else {
														var transaction = _v36.a;
														return _Utils_eq(transaction.aa, protocolId) && _Utils_eq(
															$elm$core$Maybe$Just(transaction.G),
															receivedIntent);
													}
												}();
												return ((!current) || ((!model.aU) || (!_Utils_eq(
													model.c,
													$elm$core$Maybe$Just(binding))))) ? _Utils_Tuple2(
													_Utils_update(
														model,
														{aE: effects, H: retained}),
													_List_Nil) : $author$project$Shell$refreshObservations(
													_Utils_update(
														model,
														{aE: effects, H: retained}));
											}
										}
									} else {
										return _Utils_Tuple2(model, _List_Nil);
									}
								}
							default:
								break _v6$11;
						}
					} else {
						break _v6$11;
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
var $author$project$ReceiptRouter$Model = $elm$core$Basics$identity;
var $author$project$Menu$ReceiveFor = F3(
	function (a, b, c) {
		return {$: 4, a: a, b: b, c: c};
	});
var $elm$json$Json$Decode$decodeString = _Json_runOnString;
var $author$project$Menu$Committed = {$: 0};
var $author$project$ReceiptRouter$effectVersion = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return A2(
			$elm$core$List$member,
			value,
			_List_fromArray(
				[1, 2])) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Effect protocol');
	},
	A2($elm$json$Json$Decode$field, 'effectProtocol', $elm$json$Json$Decode$int));
var $author$project$ReceiptRouter$Key = F3(
	function (_native, intent, protocol) {
		return {G: intent, bU: _native, bl: protocol};
	});
var $author$project$ReceiptRouter$Maximize = 2;
var $author$project$ReceiptRouter$RestoreGeometry = 3;
var $author$project$ReceiptRouter$Intent = F5(
	function (request, generation, incarnation, operation, context) {
		return {am: context, cx: generation, A: incarnation, ar: operation, a6: request};
	});
var $author$project$ReceiptRouter$Context = F4(
	function (lifetime, epoch, output, revision) {
		return {a4: epoch, cF: lifetime, v: output, cP: revision};
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
var $author$project$ReceiptRouter$Minimize = 0;
var $author$project$ReceiptRouter$Restore = 1;
var $author$project$ReceiptRouter$operation = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		switch (value) {
			case 'minimize':
				return $elm$json$Json$Decode$succeed(0);
			case 'restore':
				return $elm$json$Json$Decode$succeed(1);
			case 'maximize':
				return $elm$json$Json$Decode$succeed(2);
			case 'restore-geometry':
				return $elm$json$Json$Decode$succeed(3);
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
var $author$project$ReceiptRouter$key = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return _Utils_eq(
			value.bl,
			((value.G.ar === 2) || (value.G.ar === 3)) ? 2 : 1) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Operation protocol mismatch');
	},
	A4(
		$elm$json$Json$Decode$map3,
		$author$project$ReceiptRouter$Key,
		A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
		A2($elm$json$Json$Decode$field, 'intent', $author$project$ReceiptRouter$intent),
		A2($elm$json$Json$Decode$field, 'effectProtocol', $elm$json$Json$Decode$int)));
var $author$project$ReceiptRouter$kind = function (expected) {
	return A2(
		$elm$json$Json$Decode$andThen,
		function (value) {
			return _Utils_eq(value, expected) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Native message kind');
		},
		A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string));
};
var $author$project$ReceiptRouter$version = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (value === 3) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Native protocol');
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
			case 3:
				var reason = error.a;
				return A2($elm$core$String$left, 256, reason);
			case 0:
				var nested = error.b;
				var $temp$error = nested;
				error = $temp$error;
				continue safeError;
			case 1:
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
		var entries = model;
		if (($elm$core$String$length(raw) > 16384) || ($author$project$ReceiptRouter$utf8Bytes(raw) > 16384)) {
			return _Utils_Tuple3(
				model,
				$elm$core$Maybe$Nothing,
				$elm$core$Maybe$Just('Native receipt byte bound'));
		} else {
			var _v0 = A2($elm$json$Json$Decode$decodeString, $author$project$ReceiptRouter$receipt, raw);
			if (_v0.$ === 1) {
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
							return _Utils_eq(entry.t, _native);
						},
						entries));
				if (_v2.$ === 1) {
					return _Utils_Tuple3(
						model,
						$elm$core$Maybe$Nothing,
						$elm$core$Maybe$Just('Unknown or mismatched native receipt'));
				} else {
					var entry = _v2.a;
					var next = _Utils_eq(outcome, $author$project$Menu$Uncertain) ? model : A2(
						$elm$core$List$filter,
						function (item) {
							return !_Utils_eq(item.ao, entry.ao);
						},
						entries);
					return _Utils_Tuple3(
						next,
						$elm$core$Maybe$Just(
							A3($author$project$Menu$ReceiveFor, entry.ao, entry.c, outcome)),
						$elm$core$Maybe$Nothing);
				}
			}
		}
	});
var $author$project$MenuBridge$nativeFrame = F2(
	function (raw, model) {
		var state = model;
		var _v0 = A2(
			$elm$json$Json$Decode$decodeString,
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			raw);
		if (_v0.$ === 1) {
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
					var _v1 = A2($author$project$ReceiptRouter$accept, raw, state.av);
					var router = _v1.a;
					var receipt = _v1.b;
					var error = _v1.c;
					if (receipt.$ === 1) {
						return _Utils_Tuple2(model, error);
					} else {
						var message = receipt.a;
						var _v3 = A2($author$project$Menu$update, message, state.ap);
						var menu = _v3.a;
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{ap: menu, av: router}),
							error);
					}
				default:
					return _Utils_Tuple2(model, $elm$core$Maybe$Nothing);
			}
		}
	});
var $author$project$Menu$Select = F3(
	function (a, b, c) {
		return {$: 1, a: a, b: b, c: c};
	});
var $author$project$Provider$geometryObservation = function (_v0) {
	var state = _v0;
	return state.bG;
};
var $author$project$Provider$getItems = function (_v0) {
	var value = _v0;
	return value.aM;
};
var $author$project$Provider$nativeBinding = function (_v0) {
	var value = _v0;
	return value.am.bU;
};
var $author$project$Provider$nativeContext = function (_v0) {
	var value = _v0;
	return {a4: value.am.bF, cF: value.am.cF, v: value.am.cL, cP: value.am.cP};
};
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
							$author$project$UInt64$string(context.v))),
						_Utils_Tuple2(
						'revision',
						$elm$json$Json$Encode$string(
							$author$project$UInt64$string(context.cP)))
					]))));
};
var $author$project$Menu$Open = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$Provider$toOpen = function (_v0) {
	var value = _v0;
	return A2($author$project$Menu$Open, value.c, value.aM);
};
var $author$project$MenuBridge$open = F2(
	function (provider, model) {
		var state = model;
		var _v0 = $author$project$MenuBridge$providerStamp(provider);
		if (_v0.$ === 1) {
			return model;
		} else {
			var stamp = _v0.a;
			var before = $author$project$Menu$snapshot(state.ap);
			var _v1 = A2(
				$author$project$Menu$update,
				$author$project$Provider$toOpen(provider),
				state.ap);
			var menu = _v1.a;
			return _Utils_eq(
				$author$project$Menu$snapshot(menu).ap,
				before.ap) ? model : _Utils_update(
				state,
				{
					ap: menu,
					at: $elm$core$Maybe$Just(
						{aw: provider, aV: stamp})
				});
		}
	});
var $author$project$MenuBridge$reconcileWithShell = F2(
	function (shell, model) {
		var state = model;
		if (!shell.aU) {
			return $author$project$MenuBridge$connectionLost(model);
		} else {
			var _v0 = state.at;
			if (_v0.$ === 1) {
				return model;
			} else {
				var captured = _v0.a;
				var _v1 = shell.aE.aS;
				if (_v1.$ === 1) {
					return model;
				} else {
					var observed = _v1.a;
					var retired = function () {
						var _v7 = A2(
							$author$project$Menu$update,
							$author$project$Menu$Invalidate(
								$author$project$Provider$getBinding(captured.aw)),
							state.ap);
						var menu = _v7.a;
						return _Utils_update(
							state,
							{ap: menu});
					}();
					var previous = $author$project$Provider$nativeContext(captured.aw);
					var sameAuthority = _Utils_eq(
						shell.c,
						$elm$core$Maybe$Just(
							$author$project$Provider$nativeBinding(captured.aw))) && (_Utils_eq(observed.am.cF, previous.cF) && (_Utils_eq(observed.am.a4, previous.a4) && _Utils_eq(observed.am.v, previous.v)));
					var liveRoot = _Utils_eq(
						A2(
							$author$project$ActionProjection$rootOf,
							$author$project$Provider$incarnation(captured.aw),
							observed.N),
						$elm$core$Maybe$Just(
							$author$project$Provider$incarnation(captured.aw)));
					var changed = (!_Utils_eq(observed.am, previous)) || ((!sameAuthority) || ((!liveRoot) || (!_Utils_eq(
						A2(
							$elm$core$Maybe$map,
							function ($) {
								return $.am;
							},
							$author$project$Provider$geometryObservation(captured.aw)),
						_Utils_eq(
							$author$project$Provider$geometryObservation(captured.aw),
							$elm$core$Maybe$Nothing) ? $elm$core$Maybe$Nothing : A2(
							$elm$core$Maybe$map,
							function ($) {
								return $.am;
							},
							shell.bG)))));
					if (!changed) {
						return model;
					} else {
						var _v2 = $author$project$Menu$snapshot(state.ap).ap;
						if (!_v2.$) {
							var view = _v2.a;
							if ((!_Utils_eq(view.x, $author$project$Menu$Ready)) || ((!sameAuthority) || ((!liveRoot) || (_Utils_eq(observed.am.cP, previous.cP) || (!$author$project$Shell$available(shell)))))) {
								return retired;
							} else {
								var scope = $author$project$Provider$presentationScope(captured.aw);
								var _v3 = A3(
									$author$project$NativeProvider$fromShell,
									{cp: observed.am.cP, bi: scope.bi, bm: scope.bm},
									$author$project$Provider$incarnation(captured.aw),
									shell);
								if (_v3.$ === 1) {
									return retired;
								} else {
									var fresh = _v3.a;
									if (!_Utils_eq(
										$author$project$Provider$getItems(fresh),
										$author$project$Provider$getItems(captured.aw))) {
										return retired;
									} else {
										var opened = A2($author$project$MenuBridge$open, fresh, retired);
										var _v4 = _Utils_Tuple2(
											view.aj,
											$author$project$MenuBridge$menuSnapshot(opened).ap);
										if ((!_v4.a.$) && (!_v4.b.$)) {
											var selected = _v4.a.a;
											var next = _v4.b.a;
											if (_Utils_eq(next.bJ, view.bJ)) {
												return retired;
											} else {
												var _v5 = opened;
												var openedState = _v5;
												var _v6 = A2(
													$author$project$Menu$update,
													A3($author$project$Menu$Select, next.bJ, next.c, selected),
													openedState.ap);
												var selectedMenu = _v6.a;
												return _Utils_update(
													openedState,
													{ap: selectedMenu});
											}
										} else {
											return opened;
										}
									}
								}
							}
						} else {
							return retired;
						}
					}
				}
			}
		}
	});
var $author$project$TaskbarShell$native = F2(
	function (message, model) {
		var menus = function () {
			if (!message.$) {
				var raw = message.a;
				var _v4 = A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
					raw);
				_v4$2:
				while (true) {
					if (!_v4.$) {
						switch (_v4.a) {
							case 'effect-outcome':
								return $author$project$NativeOutcome$valid(raw) ? A2(
									$author$project$MenuBridge$nativeFrame,
									A2($elm$json$Json$Encode$encode, 0, raw),
									model.ac).a : model.ac;
							case 'host-disconnected':
								return $author$project$MenuBridge$connectionLost(model.ac);
							default:
								break _v4$2;
						}
					} else {
						break _v4$2;
					}
				}
				return model.ac;
			} else {
				return model.ac;
			}
		}();
		var _v0 = function () {
			switch (message.$) {
				case 6:
					var scope = message.a;
					var operation = message.b;
					var target = message.c;
					var _v2 = A5($author$project$MenuBridge$guardedAct, scope, operation, target, model.b, menus);
					var next = _v2.a;
					var emitted = _v2.b;
					var error = _v2.c;
					return _Utils_Tuple2(
						_Utils_update(
							next,
							{
								n: A2($elm$core$Maybe$withDefault, next.n, error)
							}),
						emitted);
				case 0:
					var raw = message.a;
					return (_Utils_eq(
						A2(
							$elm$json$Json$Decode$decodeValue,
							A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
							raw),
						$elm$core$Result$Ok('effect-outcome')) && (!$author$project$NativeOutcome$valid(raw))) ? _Utils_Tuple2(model.b, _List_Nil) : A2($author$project$Shell$update, message, model.b);
				default:
					return A2($author$project$Shell$update, message, model.b);
			}
		}();
		var shell = _v0.a;
		var effects = _v0.b;
		var picker = A2(
			$elm$core$Maybe$andThen,
			function (current) {
				return (_Utils_eq(
					$author$project$Shell$capture(shell),
					$elm$core$Maybe$Just(current.a7)) && $author$project$Shell$available(shell)) ? $elm$core$Maybe$Just(current) : $elm$core$Maybe$Nothing;
			},
			model.D);
		var settledMenus = A2($author$project$MenuBridge$reconcileWithShell, shell, menus);
		return _Utils_Tuple2(
			_Utils_update(
				model,
				{ac: settledMenus, D: picker, b: shell}),
			effects);
	});
var $author$project$TaskbarShell$apply = F3(
	function (scope, decision, model) {
		if (decision.$ === 2) {
			var operation = decision.a;
			var root = decision.b;
			return A2(
				$author$project$TaskbarShell$native,
				A3($author$project$Shell$Act, scope, operation, root),
				_Utils_update(
					model,
					{D: $elm$core$Maybe$Nothing}));
		} else {
			return _Utils_Tuple2(model, _List_Nil);
		}
	});
var $author$project$Provider$actionProtocol = function (action) {
	return (_Utils_eq(action, $author$project$Menu$Maximize) || _Utils_eq(action, $author$project$Menu$RestoreGeometry)) ? 2 : 1;
};
var $author$project$MenuBridge$answer = F4(
	function (bridge, shell, effects, error) {
		return {bu: bridge, aE: effects, bB: error, b: shell};
	});
var $author$project$MenuBridge$operation = function (action) {
	switch (action.$) {
		case 4:
			return $elm$core$Maybe$Just(0);
		case 0:
			return $elm$core$Maybe$Just(1);
		case 5:
			return $elm$core$Maybe$Just(3);
		case 1:
			return $elm$core$Maybe$Just(4);
		default:
			return $elm$core$Maybe$Nothing;
	}
};
var $author$project$MenuBridge$providerMatches = F2(
	function (captured, shell) {
		return _Utils_eq(
			shell.c,
			$elm$core$Maybe$Just(
				$author$project$Provider$nativeBinding(captured.aw))) && (_Utils_eq(
			$author$project$Shell$capture(shell),
			$elm$core$Maybe$Just(captured.aV)) && (_Utils_eq(
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.am;
				},
				$author$project$Provider$geometryObservation(captured.aw)),
			_Utils_eq(
				$author$project$Provider$geometryObservation(captured.aw),
				$elm$core$Maybe$Nothing) ? $elm$core$Maybe$Nothing : A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.am;
				},
				shell.bG)) && (_Utils_eq(
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.am;
				},
				shell.aE.aS),
			$elm$core$Maybe$Just(
				$author$project$Provider$nativeContext(captured.aw))) && _Utils_eq(
			A2(
				$elm$core$Maybe$andThen,
				function (observed) {
					return A2(
						$author$project$ActionProjection$rootOf,
						$author$project$Provider$incarnation(captured.aw),
						observed.N);
				},
				shell.aE.aS),
			$elm$core$Maybe$Just(
				$author$project$Provider$incarnation(captured.aw))))));
	});
var $author$project$MenuBridge$refuse = F4(
	function (local, binding, reason, _v0) {
		var state = _v0;
		var _v1 = A2(
			$author$project$Menu$update,
			A3(
				$author$project$Menu$ReceiveFor,
				local,
				binding,
				$author$project$Menu$Refusal(reason)),
			state.ap);
		var menu = _v1.a;
		return _Utils_update(
			state,
			{ap: menu});
	});
var $author$project$Provider$actionContext = F2(
	function (action, snapshot) {
		var state = snapshot;
		return ($author$project$Provider$actionProtocol(action) === 2) ? A2(
			$elm$core$Maybe$withDefault,
			$author$project$Provider$nativeContext(snapshot),
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.am;
				},
				state.bG)) : $author$project$Provider$nativeContext(snapshot);
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
		var entries = model;
		var _v1 = A2($elm$json$Json$Decode$decodeValue, $author$project$ReceiptRouter$command, value);
		if (_v1.$ === 1) {
			var error = _v1.a;
			return $elm$core$Result$Err(
				$author$project$ReceiptRouter$safeError(error));
		} else {
			var _native = _v1.a;
			var expectedOperation = function () {
				switch (action.$) {
					case 4:
						return $elm$core$Maybe$Just(0);
					case 0:
						return $elm$core$Maybe$Just(1);
					case 5:
						return $elm$core$Maybe$Just(2);
					case 1:
						return $elm$core$Maybe$Just(3);
					default:
						return $elm$core$Maybe$Nothing;
				}
			}();
			var eligible = A2(
				$elm$core$List$any,
				function (item) {
					return item.aF && _Utils_eq(item.a1, action);
				},
				$author$project$Provider$getItems(provider));
			return ((!_Utils_eq(
				binding,
				$author$project$Provider$getBinding(provider))) || ((!eligible) || ((!_Utils_eq(
				$elm$core$Maybe$Just(_native.G.ar),
				expectedOperation)) || ((!_Utils_eq(
				_native.bU,
				$author$project$Provider$nativeBinding(provider))) || ((!_Utils_eq(
				_native.G.am,
				A2($author$project$Provider$actionContext, action, provider))) || ((!_Utils_eq(
				_native.bl,
				$author$project$Provider$actionProtocol(action))) || (!_Utils_eq(
				_native.G.A,
				$author$project$Provider$incarnation(provider))))))))) ? $elm$core$Result$Err('Native command does not match frozen menu action') : (A2(
				$elm$core$List$any,
				function (entry) {
					return _Utils_eq(entry.ao, local) || (_Utils_eq(entry.t, _native) || (_Utils_eq(entry.t.bU, _native.bU) && _Utils_eq(entry.t.G.a6, _native.G.a6)));
				},
				entries) ? $elm$core$Result$Err('Native/local operation already registered') : ((_Utils_cmp(
				$elm$core$List$length(entries),
				$author$project$Menu$maxOutstanding) > -1) ? $elm$core$Result$Err('Receipt registry capacity') : $elm$core$Result$Ok(
				A2(
					$elm$core$List$cons,
					{c: binding, t: _native, ao: local},
					entries))));
		}
	});
var $author$project$MenuBridge$menuEvent = F3(
	function (message, shell, model) {
		var state = model;
		switch (message.$) {
			case 4:
				return A4(
					$author$project$MenuBridge$answer,
					model,
					shell,
					_List_Nil,
					$elm$core$Maybe$Just('Native outcomes require an authenticated frame'));
			case 0:
				return A4(
					$author$project$MenuBridge$answer,
					model,
					shell,
					_List_Nil,
					$elm$core$Maybe$Just('Menu opening requires a validated provider'));
			default:
				var preblocked = function () {
					var _v8 = _Utils_Tuple2(message, state.at);
					if ((_v8.a.$ === 3) && (!_v8.b.$)) {
						var _v9 = _v8.a;
						var captured = _v8.b.a;
						return A3(
							$author$project$MenuBridge$blockedFor,
							$author$project$Provider$incarnation(captured.aw),
							shell,
							model);
					} else {
						return false;
					}
				}();
				var _v1 = A2($author$project$Menu$update, message, state.ap);
				var menu = _v1.a;
				var effects = _v1.b;
				var updated = _Utils_update(
					state,
					{ap: menu});
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
								state.at,
								$author$project$MenuBridge$operation(action));
							if ((!_v3.a.$) && (!_v3.b.$)) {
								var captured = _v3.a.a;
								var nativeOperation = _v3.b.a;
								if ((!_Utils_eq(
									$author$project$Provider$getBinding(captured.aw),
									binding)) || ((!A2($author$project$MenuBridge$providerMatches, captured, shell)) || (($author$project$Provider$actionProtocol(action) === 2) && ((!_Utils_eq(shell.cA, $elm$core$Maybe$Nothing)) || (!_Utils_eq(shell.cy, $elm$core$Maybe$Nothing)))))) {
									return rejected('Native window information changed; choose again');
								} else {
									var _v4 = A2(
										$author$project$Shell$update,
										A3(
											$author$project$Shell$Act,
											($author$project$Effects$protocol(nativeOperation) === 2) ? A2(
												$elm$core$Maybe$withDefault,
												captured.aV,
												$author$project$Shell$captureGeometry(shell)) : captured.aV,
											nativeOperation,
											$author$project$Provider$incarnation(captured.aw)),
										shell);
									var prepared = _v4.a;
									var commands = _v4.b;
									if ((commands.b && (!commands.a.$)) && (!commands.b.b)) {
										var command = commands.a.a;
										var _v6 = A4($author$project$ReceiptRouter$register, dispatch, captured.aw, command, state.av);
										if (_v6.$ === 1) {
											return rejected('Native menu command could not be registered');
										} else {
											var router = _v6.a;
											var closed = function () {
												var _v7 = $author$project$Menu$snapshot(menu).ap;
												if (_v7.$ === 1) {
													return menu;
												} else {
													var view = _v7.a;
													return A2(
														$author$project$Menu$update,
														$author$project$Menu$Dismiss(view.bJ),
														menu).a;
												}
											}();
											return A4(
												$author$project$MenuBridge$answer,
												_Utils_update(
													state,
													{ap: closed, av: router}),
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
	var _v0 = $author$project$MenuBridge$menuSnapshot(model.ac).ap;
	if (_v0.$ === 1) {
		return model;
	} else {
		var view = _v0.a;
		var result = A3(
			$author$project$MenuBridge$menuEvent,
			$author$project$Menu$Dismiss(view.bJ),
			model.b,
			model.ac);
		return _Utils_update(
			model,
			{ac: result.bu});
	}
};
var $author$project$TaskbarShell$valid = F2(
	function (scope, model) {
		return _Utils_eq(
			$author$project$Shell$capture(model.b),
			$elm$core$Maybe$Just(scope)) && $author$project$Shell$available(model.b);
	});
var $author$project$TaskbarShell$update = F2(
	function (message, model) {
		switch (message.$) {
			case 4:
				var provider = message.a;
				var menus = A2($author$project$MenuBridge$open, provider, model.ac);
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							ac: menus,
							D: _Utils_eq(menus, model.ac) ? model.D : $elm$core$Maybe$Nothing
						}),
					_List_Nil);
			case 5:
				var event = message.a;
				var result = A3($author$project$MenuBridge$menuEvent, event, model.b, model.ac);
				var shell = result.b;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							ac: result.bu,
							D: $elm$core$List$isEmpty(result.aE) ? model.D : $elm$core$Maybe$Nothing,
							b: _Utils_update(
								shell,
								{
									n: A2($elm$core$Maybe$withDefault, shell.n, result.bB)
								})
						}),
					result.aE);
			case 0:
				var value = message.a;
				return A2($author$project$TaskbarShell$native, value, model);
			case 1:
				var scope = message.a;
				var key = message.b;
				if (!A2($author$project$TaskbarShell$valid, scope, model)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v1 = $elm$core$List$head(
						A2(
							$elm$core$List$filter,
							function (group) {
								return _Utils_eq(group.t, key);
							},
							$author$project$TaskbarShell$groups(model)));
					if (_v1.$ === 1) {
						return _Utils_Tuple2(model, _List_Nil);
					} else {
						var group = _v1.a;
						var base = $author$project$TaskbarShell$dismissMenus(model);
						var _v2 = A2($author$project$Taskbar$primary, false, group.aH);
						if (_v2.$ === 1) {
							var _v3 = $author$project$UInt64$next(model.cx);
							if (!_v3.$) {
								var generation = _v3.a;
								return _Utils_Tuple2(
									_Utils_update(
										base,
										{
											cx: generation,
											D: $elm$core$Maybe$Just(
												{cx: generation, t: key, a7: scope})
										}),
									_List_Nil);
							} else {
								return _Utils_Tuple2(
									_Utils_update(
										base,
										{D: $elm$core$Maybe$Nothing}),
									_List_Nil);
							}
						} else {
							var decision = _v2;
							return A3($author$project$TaskbarShell$apply, scope, decision, base);
						}
					}
				}
			case 2:
				var scope = message.a;
				var generation = message.b;
				var root = message.c;
				var _v4 = model.D;
				if (!_v4.$) {
					var picker = _v4.a;
					return ((!A2($author$project$TaskbarShell$valid, scope, model)) || ((!_Utils_eq(picker.a7, scope)) || (!_Utils_eq(picker.cx, generation)))) ? _Utils_Tuple2(model, _List_Nil) : A2(
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
										return _Utils_eq(family.ai, root);
									},
									A2(
										$elm$core$List$concatMap,
										function ($) {
											return $.aH;
										},
										A2(
											$elm$core$List$filter,
											function (group) {
												return _Utils_eq(group.t, picker.t);
											},
											$author$project$TaskbarShell$groups(model)))))));
				} else {
					return _Utils_Tuple2(model, _List_Nil);
				}
			default:
				var scope = message.a;
				var generation = message.b;
				var _v5 = model.D;
				if (!_v5.$) {
					var picker = _v5.a;
					return (_Utils_eq(picker.a7, scope) && _Utils_eq(picker.cx, generation)) ? _Utils_Tuple2(
						_Utils_update(
							model,
							{D: $elm$core$Maybe$Nothing}),
						_List_Nil) : _Utils_Tuple2(model, _List_Nil);
				} else {
					return _Utils_Tuple2(model, _List_Nil);
				}
		}
	});
var $author$project$Desktop$windowBase = F2(
	function (message, model) {
		var _v0 = A2($author$project$TaskbarShell$update, message, model.a);
		var windows = _v0.a;
		var effects = _v0.b;
		var changed = !_Utils_eq(windows.b.c, model.a.b.c);
		var disconnected = !windows.b.aU;
		var launch = disconnected ? $author$project$Launch$disconnect(model.d) : (changed ? A2(
			$elm$core$Maybe$withDefault,
			$author$project$Launch$disconnect(model.d),
			A2(
				$elm$core$Maybe$map,
				function (binding) {
					return A2(
						$author$project$Launch$bind,
						$author$project$Desktop$host(binding),
						model.d);
				},
				windows.b.c)) : model.d);
		return _Utils_Tuple2(
			((disconnected || changed) ? $author$project$Desktop$advance : $elm$core$Basics$identity)(
				_Utils_update(
					model,
					{
						P: (disconnected || changed) ? $elm$core$Maybe$Nothing : model.P,
						s: (disconnected || (changed || (windows.b.aU === 3))) ? $elm$core$Maybe$Nothing : model.s,
						E: (disconnected || changed) ? '' : model.E,
						k: (disconnected || changed) ? $elm$core$Maybe$Nothing : model.k,
						d: launch,
						J: (disconnected || (changed || _Utils_eq(
							$author$project$MenuBridge$menuSnapshot(windows.ac).ap,
							$elm$core$Maybe$Nothing))) ? $elm$core$Maybe$Nothing : model.J,
						w: (disconnected || changed) ? $elm$core$Maybe$Nothing : model.w,
						a: windows
					})),
			_Utils_ap(
				A2($elm$core$List$map, $author$project$Desktop$WindowEffect, effects),
				function () {
					var _v1 = _Utils_Tuple3(model.a.D, windows.D, message);
					if (!_v1.b.$) {
						var prior = _v1.a;
						var picker = _v1.b.a;
						return _Utils_eq(
							A2(
								$elm$core$Maybe$map,
								function ($) {
									return $.cx;
								},
								prior),
							$elm$core$Maybe$Just(picker.cx)) ? _List_Nil : A2(
							$elm$core$Maybe$withDefault,
							_List_Nil,
							A2(
								$elm$core$Maybe$map,
								function (family) {
									return _List_fromArray(
										[
											$author$project$Desktop$Focus(
											'picker:' + ($author$project$Shell$stampKey(picker.a7) + (':' + ($author$project$UInt64$string(picker.cx) + (':' + $author$project$UInt64$string(family.ai))))))
										]);
								},
								$elm$core$List$head(
									A2(
										$elm$core$List$filter,
										function ($) {
											return $.bc;
										},
										A2(
											$elm$core$List$concatMap,
											function ($) {
												return $.aH;
											},
											A2(
												$elm$core$List$filter,
												function (group) {
													return _Utils_eq(group.t, picker.t);
												},
												$author$project$TaskbarShell$groups(windows)))))));
					} else {
						if ((!_v1.a.$) && (_v1.c.$ === 3)) {
							var picker = _v1.a.a;
							var _v2 = _v1.b;
							var _v3 = _v1.c;
							var scope = _v3.a;
							var generation = _v3.b;
							return (_Utils_eq(picker.a7, scope) && (_Utils_eq(picker.cx, generation) && _Utils_eq(
								$author$project$Shell$capture(windows.b),
								$elm$core$Maybe$Just(scope)))) ? _List_fromArray(
								[
									$author$project$Desktop$Focus(
									'group:' + ($author$project$Shell$stampKey(scope) + (':' + picker.t)))
								]) : _List_Nil;
						} else {
							return _List_Nil;
						}
					}
				}()));
	});
var $elm$core$Result$withDefault = F2(
	function (def, result) {
		if (!result.$) {
			var a = result.a;
			return a;
		} else {
			return def;
		}
	});
var $author$project$Desktop$window = F2(
	function (message, model) {
		_v0$3:
		while (true) {
			switch (message.$) {
				case 5:
					if (message.a.$ === 5) {
						var menuId = message.a.a;
						var _v1 = _Utils_Tuple2(
							$author$project$MenuBridge$menuSnapshot(model.a.ac).ap,
							model.J);
						if ((!_v1.a.$) && (!_v1.b.$)) {
							var menu = _v1.a.a;
							var origin = _v1.b.a;
							if (!_Utils_eq(menu.bJ, menuId)) {
								return _Utils_Tuple2(model, _List_Nil);
							} else {
								var _v2 = A2($author$project$Desktop$windowBase, message, model);
								var closed = _v2.a;
								var effects = _v2.b;
								var _v3 = A2(
									$author$project$Desktop$windowBase,
									$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
									closed);
								var refreshing = _v3.a;
								var commands = _v3.b;
								return _Utils_Tuple2(
									_Utils_update(
										refreshing,
										{
											J: $elm$core$Maybe$Nothing,
											w: $elm$core$Maybe$Just(origin)
										}),
									_Utils_ap(effects, commands));
							}
						} else {
							return A2($author$project$Desktop$windowBase, message, model);
						}
					} else {
						break _v0$3;
					}
				case 3:
					var scope = message.a;
					var generation = message.b;
					var _v4 = _Utils_Tuple2(model.a.D, model.a.b.c);
					if ((!_v4.a.$) && (!_v4.b.$)) {
						var picker = _v4.a.a;
						var binding = _v4.b.a;
						var _v5 = A2($author$project$Desktop$windowBase, message, model);
						var closed = _v5.a;
						var effects = _v5.b;
						if ((!_Utils_eq(closed.a.D, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(picker.a7, scope)) || (!_Utils_eq(picker.cx, generation)))) {
							return _Utils_Tuple2(closed, effects);
						} else {
							var _v6 = A2(
								$author$project$Desktop$windowBase,
								$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
								closed);
							var refreshing = _v6.a;
							var commands = _v6.b;
							return _Utils_Tuple2(
								_Utils_update(
									refreshing,
									{
										w: $elm$core$Maybe$Just(
											{
												c: binding,
												t: picker.t,
												v: A2(
													$elm$core$Maybe$map,
													A2(
														$elm$core$Basics$composeR,
														function ($) {
															return $.am;
														},
														function ($) {
															return $.v;
														}),
													model.a.b.aE.aS)
											})
									}),
								_Utils_ap(
									A2(
										$elm$core$List$filter,
										function (effect) {
											if (effect.$ === 4) {
												return false;
											} else {
												return true;
											}
										},
										effects),
									commands));
						}
					} else {
						return A2($author$project$Desktop$windowBase, message, model);
					}
				case 2:
					var scope = message.a;
					var generation = message.b;
					var root = message.c;
					var _v8 = _Utils_Tuple3(model.a.D, model.a.b.c, model.a.b.aE.aS);
					if (((!_v8.a.$) && (!_v8.b.$)) && (!_v8.c.$)) {
						var picker = _v8.a.a;
						var binding = _v8.b.a;
						var observed = _v8.c.a;
						if ((!_Utils_eq(model.s, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(picker.a7, scope)) || ((!_Utils_eq(picker.cx, generation)) || ((!_Utils_eq(
							$author$project$Shell$capture(model.a.b),
							$elm$core$Maybe$Just(scope))) || (!$author$project$Shell$available(model.a.b)))))) {
							return _Utils_Tuple2(model, _List_Nil);
						} else {
							var _v9 = $elm$core$List$head(
								A2(
									$elm$core$List$filter,
									function (family) {
										return _Utils_eq(family.ai, root) && family.bc;
									},
									A2(
										$elm$core$List$concatMap,
										function ($) {
											return $.aH;
										},
										A2(
											$elm$core$List$filter,
											function (group) {
												return _Utils_eq(group.t, picker.t);
											},
											$author$project$TaskbarShell$groups(model.a)))));
							if (_v9.$ === 1) {
								return _Utils_Tuple2(model, _List_Nil);
							} else {
								var family = _v9.a;
								var windows = model.a;
								var _v10 = A2(
									$author$project$Desktop$windowBase,
									$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
									_Utils_update(
										model,
										{
											E: '',
											a: _Utils_update(
												windows,
												{D: $elm$core$Maybe$Nothing})
										}));
								var next = _v10.a;
								var effects = _v10.b;
								var _v11 = next.a.b.k;
								if (!_v11.$) {
									var request = _v11.a;
									var token = A2($author$project$Desktop$ChoiceToken, binding, request);
									return _Utils_Tuple2(
										_Utils_update(
											next,
											{
												s: $elm$core$Maybe$Just(
													{bb: family.bb, c: binding, v: observed.am.v, ai: root, ba: token})
											}),
										_Utils_ap(
											effects,
											_List_fromArray(
												[
													$author$project$Desktop$ArmChoice(token)
												])));
								} else {
									return _Utils_Tuple2(next, effects);
								}
							}
						}
					} else {
						return _Utils_Tuple2(model, _List_Nil);
					}
				default:
					break _v0$3;
			}
		}
		var matchingProjection = function () {
			if ((!message.$) && (!message.a.$)) {
				var raw = message.a.a;
				return A2(
					$elm$core$Result$withDefault,
					false,
					A2(
						$elm$core$Result$map,
						function (_v22) {
							var kind = _v22.a;
							var request = _v22.b;
							return (kind === 'action-projection') && _Utils_eq(
								model.a.b.k,
								$elm$core$Maybe$Just(request));
						},
						A2(
							$elm$json$Json$Decode$decodeValue,
							A3(
								$elm$json$Json$Decode$map2,
								$elm$core$Tuple$pair,
								A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
								A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder)),
							raw)));
			} else {
				return false;
			}
		}();
		var base = function () {
			if ((!message.$) && (!message.a.$)) {
				return model;
			} else {
				return _Utils_update(
					model,
					{w: $elm$core$Maybe$Nothing});
			}
		}();
		var _v12 = A2($author$project$Desktop$windowBase, message, base);
		var updated = _v12.a;
		var ordinaryEffects = _v12.b;
		var _v13 = function () {
			var _v14 = updated.w;
			if (!_v14.$) {
				var target = _v14.a;
				if ((!matchingProjection) || (!$author$project$Shell$available(updated.a.b))) {
					return _Utils_Tuple2(updated, ordinaryEffects);
				} else {
					var retired = _Utils_update(
						updated,
						{w: $elm$core$Maybe$Nothing});
					var exists = A2(
						$elm$core$List$any,
						function (group) {
							return _Utils_eq(group.t, target.t) && A2(
								$elm$core$List$any,
								function ($) {
									return $.bc;
								},
								group.aH);
						},
						$author$project$TaskbarShell$groups(retired.a));
					if (retired.C || ((!_Utils_eq(retired.a.D, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(
						$author$project$MenuBridge$menuSnapshot(retired.a.ac).ap,
						$elm$core$Maybe$Nothing)) || ((!_Utils_eq(
						retired.a.b.c,
						$elm$core$Maybe$Just(target.c))) || (_Utils_eq(target.v, $elm$core$Maybe$Nothing) || ((!_Utils_eq(
						A2(
							$elm$core$Maybe$map,
							A2(
								$elm$core$Basics$composeR,
								function ($) {
									return $.am;
								},
								function ($) {
									return $.v;
								}),
							retired.a.b.aE.aS),
						target.v)) || (!exists))))))) {
						return _Utils_Tuple2(retired, ordinaryEffects);
					} else {
						var _v15 = $author$project$Shell$capture(retired.a.b);
						if (!_v15.$) {
							var scope = _v15.a;
							return _Utils_Tuple2(
								retired,
								_Utils_ap(
									ordinaryEffects,
									_List_fromArray(
										[
											$author$project$Desktop$Focus(
											'group:' + ($author$project$Shell$stampKey(scope) + (':' + target.t)))
										])));
						} else {
							return _Utils_Tuple2(retired, ordinaryEffects);
						}
					}
				}
			} else {
				return _Utils_Tuple2(updated, ordinaryEffects);
			}
		}();
		var next = _v13.a;
		var effects = _v13.b;
		var _v16 = next.s;
		if (!_v16.$) {
			var pending = _v16.a;
			if ((!matchingProjection) || (!$author$project$Shell$available(next.a.b))) {
				return _Utils_Tuple2(next, effects);
			} else {
				var retired = _Utils_update(
					next,
					{s: $elm$core$Maybe$Nothing, E: 'The window changed. Choose again.'});
				var output = A2(
					$elm$core$Maybe$map,
					A2(
						$elm$core$Basics$composeR,
						function ($) {
							return $.am;
						},
						function ($) {
							return $.v;
						}),
					next.a.b.aE.aS);
				var family = $elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (item) {
							return _Utils_eq(item.ai, pending.ai) && (_Utils_eq(item.bb, pending.bb) && item.bc);
						},
						A2(
							$elm$core$List$concatMap,
							function ($) {
								return $.aH;
							},
							$author$project$TaskbarShell$groups(next.a))));
				if ((!_Utils_eq(
					next.a.b.c,
					$elm$core$Maybe$Just(pending.c))) || (!_Utils_eq(
					output,
					$elm$core$Maybe$Just(pending.v)))) {
					return _Utils_Tuple2(retired, effects);
				} else {
					var _v17 = _Utils_Tuple2(
						$author$project$Shell$capture(next.a.b),
						family);
					if ((!_v17.a.$) && (!_v17.b.$)) {
						var scope = _v17.a.a;
						var selected = _v17.b.a;
						var _v18 = $author$project$Taskbar$selection(selected);
						if (_v18.$ === 2) {
							var operation = _v18.a;
							var root = _v18.b;
							var _v19 = A2(
								$author$project$Desktop$windowBase,
								$author$project$TaskbarShell$Native(
									A3($author$project$Shell$Act, scope, operation, root)),
								_Utils_update(
									retired,
									{E: ''}));
							var applied = _v19.a;
							var commands = _v19.b;
							return _Utils_Tuple2(
								applied,
								_Utils_ap(effects, commands));
						} else {
							return _Utils_Tuple2(retired, effects);
						}
					} else {
						return _Utils_Tuple2(retired, effects);
					}
				}
			}
		} else {
			return _Utils_Tuple2(next, effects);
		}
	});
var $author$project$Desktop$update = F2(
	function (message, model) {
		switch (message.$) {
			case 8:
				var token = message.a;
				return (!_Utils_eq(
					A2(
						$elm$core$Maybe$map,
						function ($) {
							return $.ba;
						},
						model.s),
					$elm$core$Maybe$Just(token))) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
					_Utils_update(
						model,
						{s: $elm$core$Maybe$Nothing, E: 'Window information took too long. Refresh windows, then choose again.'}),
					_List_Nil);
			case 9:
				return ((!_Utils_eq(model.s, $elm$core$Maybe$Nothing)) || $elm$core$String$isEmpty(model.E)) ? _Utils_Tuple2(model, _List_Nil) : A2(
					$author$project$Desktop$windowBase,
					$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
					_Utils_update(
						model,
						{E: ''}));
			case 2:
				var raw = message.a;
				var positive = A2(
					$elm$json$Json$Decode$andThen,
					function (counter) {
						return _Utils_eq(counter, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero owner identity') : $elm$json$Json$Decode$succeed(counter);
					},
					$author$project$UInt64$decoder);
				var decoder = A2(
					$author$project$Desktop$strict,
					_List_fromArray(
						['surfaceProtocol', 'kind', 'outputId', 'providerId']),
					A5(
						$elm$json$Json$Decode$map4,
						F4(
							function (protocol, kind, output, provider) {
								return _Utils_Tuple3(
									protocol,
									kind,
									{bi: output, bm: provider});
							}),
						A2($elm$json$Json$Decode$field, 'surfaceProtocol', $elm$json$Json$Decode$int),
						A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
						A2($elm$json$Json$Decode$field, 'outputId', positive),
						A2($elm$json$Json$Decode$field, 'providerId', positive)));
				var _v1 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
				if (((!_v1.$) && (_v1.a.a === 2)) && (_v1.a.b === 'surface-owner')) {
					var _v2 = _v1.a;
					var owner = _v2.c;
					if (model.aT) {
						return _Utils_Tuple2(model, _List_Nil);
					} else {
						var _v3 = model.as;
						if (_v3.$ === 1) {
							return _Utils_Tuple2(
								_Utils_update(
									model,
									{
										as: $elm$core$Maybe$Just(owner)
									}),
								_List_Nil);
						} else {
							var previous = _v3.a;
							if (_Utils_eq(previous, owner)) {
								return _Utils_Tuple2(model, _List_Nil);
							} else {
								var retired = function () {
									var _v4 = $author$project$MenuBridge$currentProvider(model.a.ac);
									if (_v4.$ === 1) {
										return model;
									} else {
										var provider = _v4.a;
										return A2(
											$author$project$Desktop$windowBase,
											$author$project$TaskbarShell$MenuEvent(
												$author$project$Menu$Invalidate(
													$author$project$Provider$getBinding(provider))),
											model).a;
									}
								}();
								return _Utils_Tuple2(
									_Utils_update(
										retired,
										{J: $elm$core$Maybe$Nothing, aT: true, as: $elm$core$Maybe$Nothing, w: $elm$core$Maybe$Nothing}),
									_List_Nil);
							}
						}
					}
				} else {
					return _Utils_Tuple2(model, _List_Nil);
				}
			case 1:
				var stamp = message.a;
				var root = message.b;
				if (model.aT || ((!_Utils_eq(model.s, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(
					$author$project$Shell$capture(model.a.b),
					$elm$core$Maybe$Just(stamp))) || (!$author$project$Shell$available(model.a.b))))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v5 = model.a.b.aE.aS;
					if (_v5.$ === 1) {
						return _Utils_Tuple2(model, _List_Nil);
					} else {
						var observed = _v5.a;
						var _v6 = model.as;
						if (_v6.$ === 1) {
							return _Utils_Tuple2(model, _List_Nil);
						} else {
							var owner = _v6.a;
							var _v7 = A3(
								$author$project$NativeProvider$fromShell,
								{cp: observed.am.cP, bi: owner.bi, bm: owner.bm},
								root,
								model.a.b);
							if (_v7.$ === 1) {
								return _Utils_Tuple2(model, _List_Nil);
							} else {
								var provider = _v7.a;
								var _v8 = A2(
									$author$project$Desktop$windowBase,
									$author$project$TaskbarShell$OpenMenu(provider),
									model);
								var next = _v8.a;
								var effects = _v8.b;
								return _Utils_eq(
									$author$project$MenuBridge$menuSnapshot(next.a.ac).ap,
									$author$project$MenuBridge$menuSnapshot(model.a.ac).ap) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
									_Utils_update(
										next,
										{
											k: $elm$core$Maybe$Nothing,
											J: A2(
												$elm$core$Maybe$andThen,
												function (binding) {
													return A2(
														$elm$core$Maybe$map,
														function (group) {
															return {
																c: binding,
																t: group.t,
																v: $elm$core$Maybe$Just(observed.am.v)
															};
														},
														$elm$core$List$head(
															A2(
																$elm$core$List$filter,
																function (group) {
																	return A2(
																		$elm$core$List$any,
																		function (family) {
																			return _Utils_eq(family.ai, root);
																		},
																		group.aH);
																},
																$author$project$TaskbarShell$groups(model.a))));
												},
												model.a.b.c),
											C: false,
											w: $elm$core$Maybe$Nothing
										}),
									effects);
							}
						}
					}
				}
			case 0:
				var value = message.a;
				var _v9 = A2($author$project$Desktop$window, value, model);
				var next = _v9.a;
				var effects = _v9.b;
				return ((!_Utils_eq(next.a.D, $elm$core$Maybe$Nothing)) && (!_Utils_eq(next.a.D, model.a.D))) ? _Utils_Tuple2(
					_Utils_update(
						next,
						{k: $elm$core$Maybe$Nothing, J: $elm$core$Maybe$Nothing, C: false, w: $elm$core$Maybe$Nothing}),
					effects) : _Utils_Tuple2(next, effects);
			case 3:
				var raw = message.a;
				var _v10 = A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
					raw);
				_v10$2:
				while (true) {
					if (!_v10.$) {
						switch (_v10.a) {
							case 'application-catalog':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'snapshot']),
									A5(
										$elm$json$Json$Decode$map4,
										F4(
											function (_v13, binding, request, snapshot) {
												return _Utils_Tuple3(binding, request, snapshot);
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'snapshot', $elm$json$Json$Decode$value)));
								var _v11 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v11.$) {
									var _v12 = _v11.a;
									var binding = _v12.a;
									var request = _v12.b;
									var snapshot = _v12.c;
									if ((!(!model.a.b.aU)) && (_Utils_eq(
										model.a.b.c,
										$elm$core$Maybe$Just(binding)) && _Utils_eq(
										model.k,
										$elm$core$Maybe$Just(request)))) {
										var next = $author$project$Desktop$advance(
											_Utils_update(
												model,
												{
													P: $elm$core$Result$toMaybe(
														$author$project$Catalog$decode(snapshot)),
													k: $elm$core$Maybe$Nothing,
													d: A2($author$project$Launch$catalog, snapshot, model.d)
												}));
										var target = A2(
											$elm$core$Maybe$withDefault,
											A2($author$project$Desktop$key, next, 'control:close'),
											A2(
												$elm$core$Maybe$map,
												function (entry) {
													return A2(
														$author$project$Desktop$key,
														next,
														'entry:' + $author$project$Catalog$id(entry.bK));
												},
												$elm$core$List$head(
													A2(
														$elm$core$Maybe$withDefault,
														_List_Nil,
														A2(
															$elm$core$Maybe$map,
															$author$project$Catalog$entries,
															A2(
																$elm$core$List$member,
																$author$project$Launch$status(next.d),
																_List_fromArray(
																	['Pending', 'Unknown'])) ? $elm$core$Maybe$Nothing : next.P)))));
										return _Utils_Tuple2(
											next,
											next.C ? _List_fromArray(
												[
													$author$project$Desktop$Focus(target)
												]) : _List_Nil);
									} else {
										return _Utils_Tuple2(model, _List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'application-launch-outcome':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'outcome']),
									A4(
										$elm$json$Json$Decode$map3,
										F3(
											function (_v16, binding, outcome) {
												return _Utils_Tuple2(binding, outcome);
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'outcome', $elm$json$Json$Decode$value)));
								var _v14 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v14.$) {
									var _v15 = _v14.a;
									var binding = _v15.a;
									var outcome = _v15.b;
									return ((!(!model.a.b.aU)) && _Utils_eq(
										model.a.b.c,
										$elm$core$Maybe$Just(binding))) ? _Utils_Tuple2(
										_Utils_update(
											model,
											{
												d: A3(
													$author$project$Launch$receive,
													$author$project$Desktop$host(binding),
													outcome,
													model.d)
											}),
										_List_Nil) : _Utils_Tuple2(model, _List_Nil);
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							default:
								break _v10$2;
						}
					} else {
						break _v10$2;
					}
				}
				return A2(
					$author$project$Desktop$window,
					$author$project$TaskbarShell$Native(
						$author$project$Shell$Incoming(raw)),
					model);
			case 4:
				var stamp = message.a;
				if (!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var base = function () {
						var _v18 = $author$project$MenuBridge$menuSnapshot(model.a.ac).ap;
						if (_v18.$ === 1) {
							return model;
						} else {
							var menu = _v18.a;
							return A2(
								$author$project$Desktop$windowBase,
								$author$project$TaskbarShell$MenuEvent(
									$author$project$Menu$Dismiss(menu.bJ)),
								model).a;
						}
					}();
					var windows = base.a;
					var retired = $author$project$Desktop$advance(
						_Utils_update(
							base,
							{
								P: $elm$core$Maybe$Nothing,
								k: $elm$core$Maybe$Nothing,
								d: A2($author$project$Launch$catalog, $elm$json$Json$Encode$null, model.d),
								J: $elm$core$Maybe$Nothing,
								C: true,
								w: $elm$core$Maybe$Nothing,
								a: _Utils_update(
									windows,
									{D: $elm$core$Maybe$Nothing})
							}));
					var _v17 = _Utils_Tuple2(
						model.a.b.c,
						$author$project$UInt64$next(model.a6));
					if ((!_v17.a.$) && (!_v17.b.$)) {
						var binding = _v17.a.a;
						var request = _v17.b.a;
						return ((!model.a.b.aU) || _Utils_eq(retired.X, $elm$core$Maybe$Nothing)) ? _Utils_Tuple2(retired, _List_Nil) : _Utils_Tuple2(
							_Utils_update(
								retired,
								{
									k: $elm$core$Maybe$Just(request),
									a6: request
								}),
							_List_fromArray(
								[
									$author$project$Desktop$Send(
									$elm$json$Json$Encode$object(
										_List_fromArray(
											[
												_Utils_Tuple2(
												'protocolVersion',
												$elm$json$Json$Encode$int(3)),
												_Utils_Tuple2(
												'kind',
												$elm$json$Json$Encode$string('catalog-request')),
												_Utils_Tuple2(
												'binding',
												$author$project$Binding$encode(binding)),
												_Utils_Tuple2(
												'requestId',
												$elm$json$Json$Encode$string(
													$author$project$UInt64$string(request)))
											]))),
									$author$project$Desktop$Focus(
									A2($author$project$Desktop$key, retired, 'control:close'))
								]));
					} else {
						return _Utils_Tuple2(retired, _List_Nil);
					}
				}
			case 5:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.C)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var next = $author$project$Desktop$advance(
						_Utils_update(
							model,
							{k: $elm$core$Maybe$Nothing, C: false}));
					return _Utils_Tuple2(
						next,
						_List_fromArray(
							[
								$author$project$Desktop$Focus(
								A2($author$project$Desktop$key, next, 'control:opener'))
							]));
				}
			case 6:
				var selection = message.a;
				var _v19 = A2($author$project$Launch$start, selection, model.d);
				var launch = _v19.a;
				var intent = _v19.b;
				var _v20 = _Utils_Tuple2(intent, model.a.b.c);
				if ((!_v20.a.$) && (!_v20.b.$)) {
					var wire = _v20.a.a;
					var binding = _v20.b.a;
					return _Utils_Tuple2(
						_Utils_update(
							model,
							{k: $elm$core$Maybe$Nothing, d: launch, C: false}),
						A2(
							$elm$core$List$cons,
							$author$project$Desktop$Send(
								$elm$json$Json$Encode$object(
									_List_fromArray(
										[
											_Utils_Tuple2(
											'protocolVersion',
											$elm$json$Json$Encode$int(3)),
											_Utils_Tuple2(
											'kind',
											$elm$json$Json$Encode$string('application-launch')),
											_Utils_Tuple2(
											'binding',
											$author$project$Binding$encode(binding)),
											_Utils_Tuple2('intent', wire)
										]))),
							A2(
								$elm$core$Maybe$withDefault,
								_List_Nil,
								A2(
									$elm$core$Maybe$map,
									A2($elm$core$Basics$composeR, $author$project$Desktop$Arm, $elm$core$List$singleton),
									$author$project$Launch$pending(launch)))));
				} else {
					return _Utils_Tuple2(
						_Utils_update(
							model,
							{d: launch}),
						_List_Nil);
				}
			case 7:
				var token = message.a;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							d: A2($author$project$Launch$timeout, token, model.d)
						}),
					_List_Nil);
			default:
				var token = message.a;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							d: A2($author$project$Launch$acknowledgeUnknown, token, model.d)
						}),
					_List_Nil);
		}
	});
var $author$project$SurfaceController$apply = F2(
	function (message, current) {
		var model = current;
		if (model.F) {
			return _Utils_Tuple2(current, _List_Nil);
		} else {
			var oldMode = $author$project$Surface$mode(model.h);
			var _v0 = A2($author$project$Desktop$update, message, model.h);
			var next = _v0.a;
			var effects = _v0.b;
			var changed = !_Utils_eq(next, model.h);
			var nextMode = $author$project$Surface$mode(next);
			var newLease = (nextMode !== 'closed') && ((!_Utils_eq(nextMode, oldMode)) || ((!_Utils_eq(
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.bJ;
					},
					$author$project$MenuBridge$menuSnapshot(model.h.a.ac).ap),
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.bJ;
					},
					$author$project$MenuBridge$menuSnapshot(next.a.ac).ap))) || ((nextMode === 'picker') && (!_Utils_eq(
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.cx;
					},
					model.h.a.D),
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.cx;
					},
					next.a.D))))));
			var lease = newLease ? $author$project$UInt64$next(model.I) : $elm$core$Maybe$Just(model.I);
			if ((!changed) && $elm$core$List$isEmpty(effects)) {
				return _Utils_Tuple2(current, _List_Nil);
			} else {
				var _v1 = _Utils_Tuple2(
					$author$project$UInt64$next(model.ag),
					lease);
				if ((!_v1.a.$) && (!_v1.b.$)) {
					var publication = _v1.a.a;
					var token = _v1.b.a;
					var result = _Utils_update(
						model,
						{h: next, I: token, ag: publication});
					return _Utils_Tuple2(
						result,
						A2(
							$elm$core$List$cons,
							$author$project$SurfaceController$Publish(
								$author$project$SurfaceController$frame(result)),
							A2($elm$core$List$map, $author$project$SurfaceController$DesktopEffect, effects)));
				} else {
					return _Utils_Tuple2(
						_Utils_update(
							model,
							{F: true}),
						_List_Nil);
				}
			}
		}
	});
var $author$project$Menu$Down = 1;
var $author$project$Menu$End = 3;
var $author$project$Menu$Home = 2;
var $author$project$Menu$Navigate = F2(
	function (a, b) {
		return {$: 2, a: a, b: b};
	});
var $author$project$Desktop$OpenWindowMenu = F2(
	function (a, b) {
		return {$: 1, a: a, b: b};
	});
var $author$project$Menu$Up = 0;
var $author$project$Surface$resolveAction = F4(
	function (publication, lease, raw, model) {
		var strict = function (child) {
			return A2(
				$elm$json$Json$Decode$andThen,
				function (pairs) {
					return _Utils_eq(
						$elm$core$List$sort(
							A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
						_List_fromArray(
							['id', 'kind', 'lease', 'publication', 'surface', 'surfaceProtocol'])) ? child : $elm$json$Json$Decode$fail('Surface action fields');
				},
				$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
		};
		var decoder = strict(
			A7(
				$elm$json$Json$Decode$map6,
				F6(
					function (version, kind, shown, scoped, identity, role) {
						return {bK: identity, bN: kind, bn: role, b4: scoped, b6: shown, ca: version};
					}),
				A2($elm$json$Json$Decode$field, 'surfaceProtocol', $elm$json$Json$Decode$int),
				A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
				A2($elm$json$Json$Decode$field, 'publication', $author$project$UInt64$decoder),
				A2($elm$json$Json$Decode$field, 'lease', $author$project$UInt64$decoder),
				A2($elm$json$Json$Decode$field, 'id', $elm$json$Json$Decode$string),
				A2($elm$json$Json$Decode$field, 'surface', $elm$json$Json$Decode$string)));
		var _v0 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
		if (!_v0.$) {
			var event = _v0.a;
			return ((event.ca !== 2) || ((event.bN !== 'surface-action') || ((!_Utils_eq(event.b6, publication)) || (!_Utils_eq(event.b4, lease))))) ? $elm$core$Maybe$Nothing : A2(
				$elm$core$Maybe$andThen,
				function ($) {
					return $.m;
				},
				$elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (control) {
							return _Utils_eq(control.bJ, event.bK) && control.aF;
						},
						(event.bn === 'bar') ? $author$project$Surface$barControls(model) : ((event.bn === 'popup') ? $author$project$Surface$controls(model) : _List_Nil))));
		} else {
			return $elm$core$Maybe$Nothing;
		}
	});
var $author$project$Surface$resolve = F4(
	function (publication, lease, raw, model) {
		var strict = F2(
			function (fields, child) {
				return A2(
					$elm$json$Json$Decode$andThen,
					function (pairs) {
						return _Utils_eq(
							$elm$core$List$sort(
								A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
							$elm$core$List$sort(fields)) ? child : $elm$json$Json$Decode$fail('Surface event fields');
					},
					$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
			});
		var scopes = function (child) {
			return A2(
				$elm$json$Json$Decode$andThen,
				function (_v4) {
					var valid = _v4.a;
					var role = _v4.b;
					return valid ? child(role) : $elm$json$Json$Decode$fail('Stale surface event');
				},
				A5(
					$elm$json$Json$Decode$map4,
					F4(
						function (version, shown, scoped, role) {
							return _Utils_Tuple2(
								(version === 2) && (_Utils_eq(shown, publication) && _Utils_eq(scoped, lease)),
								role);
						}),
					A2($elm$json$Json$Decode$field, 'surfaceProtocol', $elm$json$Json$Decode$int),
					A2($elm$json$Json$Decode$field, 'publication', $author$project$UInt64$decoder),
					A2($elm$json$Json$Decode$field, 'lease', $author$project$UInt64$decoder),
					A2($elm$json$Json$Decode$field, 'surface', $elm$json$Json$Decode$string)));
		};
		var navigation = A2(
			strict,
			_List_fromArray(
				['surfaceProtocol', 'kind', 'surface', 'publication', 'lease', 'key']),
			scopes(
				function (role) {
					return ((role === 'popup') && ($author$project$Surface$mode(model) === 'menu')) ? A2($elm$json$Json$Decode$field, 'key', $elm$json$Json$Decode$string) : $elm$json$Json$Decode$fail('No menu');
				}));
		var menuMessage = function (key) {
			return A2(
				$elm$core$Maybe$andThen,
				function (menu) {
					var send = A2(
						$elm$core$Basics$composeL,
						A2($elm$core$Basics$composeL, $elm$core$Maybe$Just, $author$project$Desktop$Window),
						$author$project$TaskbarShell$MenuEvent);
					switch (key) {
						case 'Escape':
							return send(
								$author$project$Menu$Dismiss(menu.bJ));
						case 'ArrowUp':
							return send(
								A2($author$project$Menu$Navigate, menu.bJ, 0));
						case 'ArrowDown':
							return send(
								A2($author$project$Menu$Navigate, menu.bJ, 1));
						case 'Home':
							return send(
								A2($author$project$Menu$Navigate, menu.bJ, 2));
						case 'End':
							return send(
								A2($author$project$Menu$Navigate, menu.bJ, 3));
						case 'Enter':
							return ($author$project$Shell$available(model.a.b) && _Utils_eq(menu.x, $author$project$Menu$Ready)) ? A2(
								$elm$core$Maybe$map,
								function (index) {
									return $author$project$Desktop$Window(
										$author$project$TaskbarShell$MenuEvent(
											A3($author$project$Menu$Activate, menu.bJ, menu.c, index)));
								},
								menu.aj) : $elm$core$Maybe$Nothing;
						default:
							return $elm$core$Maybe$Nothing;
					}
				},
				$author$project$MenuBridge$menuSnapshot(model.a.ac).ap);
		};
		var context = A2(
			strict,
			_List_fromArray(
				['surfaceProtocol', 'kind', 'surface', 'publication', 'lease', 'id', 'trigger', 'x', 'y']),
			scopes(
				function (role) {
					return A5(
						$elm$json$Json$Decode$map4,
						F4(
							function (identity, trigger, x, y) {
								return _Utils_Tuple3(role, identity, trigger);
							}),
						A2($elm$json$Json$Decode$field, 'id', $elm$json$Json$Decode$string),
						A2($elm$json$Json$Decode$field, 'trigger', $elm$json$Json$Decode$string),
						A2($elm$json$Json$Decode$field, 'x', $elm$json$Json$Decode$int),
						A2($elm$json$Json$Decode$field, 'y', $elm$json$Json$Decode$int));
				}));
		var _v0 = A2(
			$elm$json$Json$Decode$decodeValue,
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			raw);
		_v0$3:
		while (true) {
			if (!_v0.$) {
				switch (_v0.a) {
					case 'surface-action':
						return A4($author$project$Surface$resolveAction, publication, lease, raw, model);
					case 'surface-menu-navigation':
						return A2(
							$elm$core$Maybe$andThen,
							menuMessage,
							$elm$core$Result$toMaybe(
								A2($elm$json$Json$Decode$decodeValue, navigation, raw)));
					case 'surface-context':
						return A2(
							$elm$core$Maybe$andThen,
							function (_v1) {
								var role = _v1.a;
								var identity = _v1.b;
								var trigger = _v1.c;
								return ((!A2(
									$elm$core$List$member,
									trigger,
									_List_fromArray(
										['pointer', 'keyboard']))) || (!_Utils_eq(model.s, $elm$core$Maybe$Nothing))) ? $elm$core$Maybe$Nothing : A2(
									$elm$core$Maybe$andThen,
									function (stamp) {
										return (role === 'bar') ? A2(
											$elm$core$Maybe$andThen,
											function (group) {
												var _v2 = group.aH;
												if (_v2.b && (!_v2.b.b)) {
													var family = _v2.a;
													return family.bc ? $elm$core$Maybe$Just(
														A2($author$project$Desktop$OpenWindowMenu, stamp, family.ai)) : $elm$core$Maybe$Nothing;
												} else {
													return _Utils_eq(
														A2($author$project$Taskbar$primary, false, group.aH),
														$author$project$Taskbar$Picker) ? $elm$core$Maybe$Just(
														$author$project$Desktop$Window(
															A2($author$project$TaskbarShell$Primary, stamp, group.t))) : $elm$core$Maybe$Nothing;
												}
											},
											$elm$core$List$head(
												A2(
													$elm$core$List$filter,
													function (group) {
														return _Utils_eq('bar:group:' + group.t, identity);
													},
													$author$project$TaskbarShell$groups(model.a)))) : (((role === 'popup') && ($author$project$Surface$mode(model) === 'picker')) ? A2(
											$elm$core$Maybe$andThen,
											function (picker) {
												return (!_Utils_eq(picker.a7, stamp)) ? $elm$core$Maybe$Nothing : A2(
													$elm$core$Maybe$map,
													function (family) {
														return A2($author$project$Desktop$OpenWindowMenu, stamp, family.ai);
													},
													$elm$core$List$head(
														A2(
															$elm$core$List$filter,
															function (family) {
																return _Utils_eq(
																	'family:' + $author$project$UInt64$string(family.ai),
																	identity) && family.bc;
															},
															A2(
																$elm$core$List$concatMap,
																function ($) {
																	return $.aH;
																},
																A2(
																	$elm$core$List$filter,
																	function (group) {
																		return _Utils_eq(group.t, picker.t);
																	},
																	$author$project$TaskbarShell$groups(model.a))))));
											},
											model.a.D) : $elm$core$Maybe$Nothing);
									},
									$author$project$Shell$capture(model.a.b));
							},
							$elm$core$Result$toMaybe(
								A2($elm$json$Json$Decode$decodeValue, context, raw)));
					default:
						break _v0$3;
				}
			} else {
				break _v0$3;
			}
		}
		return $elm$core$Maybe$Nothing;
	});
var $author$project$SurfaceController$update = F2(
	function (event, current) {
		var model = current;
		if (model.F) {
			return _Utils_Tuple2(current, _List_Nil);
		} else {
			switch (event.$) {
				case 0:
					var message = event.a;
					return A2($author$project$SurfaceController$apply, message, current);
				case 1:
					var raw = event.a;
					return A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (message) {
								return A2($author$project$SurfaceController$apply, message, current);
							},
							A4($author$project$Surface$resolve, model.ag, model.I, raw, model.h)));
				case 3:
					var lease = event.a;
					if ((!_Utils_eq(lease, model.I)) || ($author$project$Surface$mode(model.h) === 'closed')) {
						return _Utils_Tuple2(current, _List_Nil);
					} else {
						var _v1 = _Utils_Tuple2(
							$author$project$UInt64$next(model.I),
							$author$project$UInt64$next(model.ag));
						if ((!_v1.a.$) && (!_v1.b.$)) {
							var token = _v1.a.a;
							var shown = _v1.b.a;
							var refreshed = _Utils_update(
								model,
								{I: token, ag: shown});
							var _v2 = A2(
								$author$project$SurfaceController$apply,
								$author$project$Desktop$Window(
									$author$project$TaskbarShell$Native($author$project$Shell$Refresh)),
								refreshed);
							var result = _v2.a;
							var effects = _v2.b;
							return _Utils_Tuple2(
								result,
								A2(
									$elm$core$List$cons,
									$author$project$SurfaceController$Publish(
										$author$project$SurfaceController$frame(result)),
									effects));
						} else {
							return _Utils_Tuple2(
								_Utils_update(
									model,
									{F: true}),
								_List_Nil);
						}
					}
				default:
					var lease = event.a;
					return ((!_Utils_eq(lease, model.I)) || ($author$project$Surface$mode(model.h) === 'closed')) ? _Utils_Tuple2(current, _List_Nil) : (($author$project$Surface$mode(model.h) === 'menu') ? A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (menu) {
								return A2(
									$author$project$SurfaceController$apply,
									$author$project$Desktop$Window(
										$author$project$TaskbarShell$MenuEvent(
											$author$project$Menu$Dismiss(menu.bJ))),
									current);
							},
							$author$project$MenuBridge$menuSnapshot(model.h.a.ac).ap)) : (model.h.C ? A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (stamp) {
								return A2(
									$author$project$SurfaceController$apply,
									$author$project$Desktop$CloseApplications(stamp),
									current);
							},
							$author$project$Desktop$capture(model.h))) : A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (picker) {
								return A2(
									$author$project$SurfaceController$apply,
									$author$project$Desktop$Window(
										A2($author$project$TaskbarShell$Close, picker.a7, picker.cx)),
									current);
							},
							model.h.a.D))));
			}
		}
	});
var $author$project$MenuSurfaceReplay$apply = F2(
	function (raw, _v0) {
		var model = _v0.a;
		var rows = _v0.b;
		var value = function (name) {
			return A2(
				$elm$core$Result$withDefault,
				$elm$json$Json$Encode$null,
				A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, name, $elm$json$Json$Decode$value),
					raw));
		};
		var scopeValue = function (owner) {
			return $elm$json$Json$Encode$object(
				_List_fromArray(
					[
						_Utils_Tuple2(
						'outputId',
						$elm$json$Json$Encode$string(
							$author$project$UInt64$string(owner.bi))),
						_Utils_Tuple2(
						'providerId',
						$elm$json$Json$Encode$string(
							$author$project$UInt64$string(owner.bm)))
					]));
		};
		var kind = A2(
			$elm$core$Result$withDefault,
			'',
			A2(
				$elm$json$Json$Decode$decodeValue,
				A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
				raw));
		var event = function () {
			switch (kind) {
				case 'geometry-attach':
					return $elm$core$Maybe$Just(
						$author$project$SurfaceController$Interaction(
							$author$project$Desktop$Window(
								$author$project$TaskbarShell$Native($author$project$Shell$GeometryAttach))));
				case 'geometry-refresh':
					return $elm$core$Maybe$Just(
						$author$project$SurfaceController$Interaction(
							$author$project$Desktop$Window(
								$author$project$TaskbarShell$Native($author$project$Shell$GeometryRefresh))));
				case 'owner':
					return $elm$core$Maybe$Just(
						$author$project$SurfaceController$Interaction(
							$author$project$Desktop$OwnerScope(
								value('frame'))));
				case 'choice-deadline':
					return A2(
						$elm$core$Maybe$map,
						A2($elm$core$Basics$composeR, $author$project$Desktop$ChoiceDeadline, $author$project$SurfaceController$Interaction),
						$author$project$Desktop$choiceToken(
							$author$project$SurfaceController$desktop(model)));
				case 'native':
					return $elm$core$Maybe$Just(
						$author$project$SurfaceController$Interaction(
							$author$project$Desktop$Incoming(
								value('frame'))));
				case 'action':
					return $elm$core$Maybe$Just(
						$author$project$SurfaceController$Renderer(
							value('action')));
				case 'reflow':
					return A2(
						$elm$core$Maybe$map,
						$author$project$SurfaceController$NativeReflow,
						$elm$core$Result$toMaybe(
							A2(
								$elm$json$Json$Decode$decodeValue,
								A2($elm$json$Json$Decode$field, 'lease', $author$project$UInt64$decoder),
								raw)));
				case 'dismiss':
					return A2(
						$elm$core$Maybe$map,
						$author$project$SurfaceController$NativeDismiss,
						$elm$core$Result$toMaybe(
							A2(
								$elm$json$Json$Decode$decodeValue,
								A2($elm$json$Json$Decode$field, 'lease', $author$project$UInt64$decoder),
								raw)));
				case 'open':
					return A2(
						$elm$core$Maybe$map,
						A2($elm$core$Basics$composeR, $author$project$Desktop$OpenApplications, $author$project$SurfaceController$Interaction),
						$author$project$Desktop$capture(
							$author$project$SurfaceController$desktop(model)));
				default:
					return $elm$core$Maybe$Nothing;
			}
		}();
		var _v1 = A2(
			$elm$core$Maybe$withDefault,
			_Utils_Tuple2(model, _List_Nil),
			A2(
				$elm$core$Maybe$map,
				function (message) {
					return A2($author$project$SurfaceController$update, message, model);
				},
				event));
		var next = _v1.a;
		var effects = _v1.b;
		var focus = A2(
			$elm$core$List$filterMap,
			function (effect) {
				if ((!effect.$) && (effect.a.$ === 4)) {
					var target = effect.a.a;
					return $elm$core$Maybe$Just(target);
				} else {
					return $elm$core$Maybe$Nothing;
				}
			},
			effects);
		var order = A2(
			$elm$core$List$map,
			function (effect) {
				if (effect.$ === 1) {
					return 'publish';
				} else {
					if (effect.a.$ === 1) {
						return 'send';
					} else {
						return 'local';
					}
				}
			},
			effects);
		var wires = A2(
			$elm$core$List$filterMap,
			function (effect) {
				_v5$3:
				while (true) {
					if (!effect.$) {
						switch (effect.a.$) {
							case 1:
								var wire = effect.a.a;
								return $elm$core$Maybe$Just(wire);
							case 0:
								if (!effect.a.a.$) {
									var wire = effect.a.a.a;
									return $elm$core$Maybe$Just(wire);
								} else {
									var _v6 = effect.a.a;
									return $elm$core$Maybe$Just(
										$elm$json$Json$Encode$object(
											_List_fromArray(
												[
													_Utils_Tuple2(
													'protocolVersion',
													$elm$json$Json$Encode$int(3)),
													_Utils_Tuple2(
													'kind',
													$elm$json$Json$Encode$string('host-reconnect'))
												])));
								}
							default:
								break _v5$3;
						}
					} else {
						break _v5$3;
					}
				}
				return $elm$core$Maybe$Nothing;
			},
			effects);
		var packet = $author$project$SurfaceController$frame(next);
		var valid = A2(
			$elm$core$Result$withDefault,
			false,
			A2(
				$elm$core$Result$map,
				function (_v4) {
					return true;
				},
				$author$project$SurfaceRenderer$decode(
					(kind === 'validate') ? value('frame') : packet)));
		var windows = $author$project$SurfaceController$desktop(next).a;
		var geometry = A2(
			$elm$core$Maybe$withDefault,
			$elm$json$Json$Encode$null,
			A2(
				$elm$core$Maybe$map,
				function (observed) {
					return $elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'revision',
								$elm$json$Json$Encode$string(
									$author$project$UInt64$string(observed.am.cP))),
								_Utils_Tuple2(
								'output',
								$elm$json$Json$Encode$string(
									$author$project$UInt64$string(observed.am.v))),
								_Utils_Tuple2(
								'windows',
								A2(
									$elm$json$Json$Encode$list,
									function (w) {
										return $elm$json$Json$Encode$object(
											_List_fromArray(
												[
													_Utils_Tuple2(
													'incarnation',
													$elm$json$Json$Encode$string(
														$author$project$UInt64$string(w.A))),
													_Utils_Tuple2(
													'mode',
													$elm$json$Json$Encode$string(
														$author$project$GeometryProjection$modeName(w.bV))),
													_Utils_Tuple2(
													'minimized',
													$elm$json$Json$Encode$bool(w.aq))
												]));
									},
									observed.a))
							]));
				},
				windows.b.bG));
		var scope = A2(
			$elm$core$Maybe$map,
			$author$project$Provider$presentationScope,
			$author$project$MenuBridge$currentProvider(windows.ac));
		var snapshot = $author$project$MenuBridge$menuSnapshot(windows.ac);
		var menu = function () {
			var _v2 = snapshot.ap;
			if (_v2.$ === 1) {
				return $elm$json$Json$Encode$null;
			} else {
				var current = _v2.a;
				return $elm$json$Json$Encode$object(
					_List_fromArray(
						[
							_Utils_Tuple2(
							'id',
							$elm$json$Json$Encode$int(
								$author$project$Menu$menuNumber(current.bJ))),
							_Utils_Tuple2(
							'selected',
							A2(
								$elm$core$Maybe$withDefault,
								$elm$json$Json$Encode$null,
								A2($elm$core$Maybe$map, $elm$json$Json$Encode$int, current.aj))),
							_Utils_Tuple2(
							'status',
							$elm$json$Json$Encode$string(
								function () {
									var _v3 = current.x;
									switch (_v3.$) {
										case 0:
											return 'ready';
										case 1:
											return 'pending';
										case 4:
											return 'unknown';
										case 2:
											return 'refused';
										default:
											return 'cancelled';
									}
								}()))
						]));
			}
		}();
		var unresolved = A2(
			$elm$json$Json$Encode$list,
			function (t) {
				return $elm$json$Json$Encode$object(
					_List_fromArray(
						[
							_Utils_Tuple2(
							'effectProtocol',
							$elm$json$Json$Encode$int(t.aa)),
							_Utils_Tuple2(
							'intent',
							$author$project$Effects$encodeIntent(t.G)),
							_Utils_Tuple2(
							'status',
							$elm$json$Json$Encode$string(
								$author$project$Effects$statusName(t.x)))
						]));
			},
			windows.b.aE.f);
		var row = $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2('geometry', geometry),
					_Utils_Tuple2('unresolved', unresolved),
					_Utils_Tuple2(
					'providerScope',
					A2(
						$elm$core$Maybe$withDefault,
						$elm$json$Json$Encode$null,
						A2($elm$core$Maybe$map, scopeValue, scope))),
					_Utils_Tuple2(
					'ownerScope',
					A2(
						$elm$core$Maybe$withDefault,
						$elm$json$Json$Encode$null,
						A2(
							$elm$core$Maybe$map,
							scopeValue,
							$author$project$SurfaceController$desktop(next).as))),
					_Utils_Tuple2(
					'ownerExhausted',
					$elm$json$Json$Encode$bool(
						$author$project$SurfaceController$desktop(next).aT)),
					_Utils_Tuple2(
					'focus',
					A2($elm$json$Json$Encode$list, $elm$json$Json$Encode$string, focus)),
					_Utils_Tuple2(
					'order',
					A2($elm$json$Json$Encode$list, $elm$json$Json$Encode$string, order)),
					_Utils_Tuple2('frame', packet),
					_Utils_Tuple2(
					'rendererAdmitted',
					$elm$json$Json$Encode$bool(valid)),
					_Utils_Tuple2(
					'requests',
					A2($elm$json$Json$Encode$list, $elm$core$Basics$identity, wires)),
					_Utils_Tuple2(
					'shell',
					$author$project$Shell$encode(windows.b)),
					_Utils_Tuple2(
					'outstanding',
					$elm$json$Json$Encode$int(snapshot.j)),
					_Utils_Tuple2(
					'registry',
					$elm$json$Json$Encode$int(
						$author$project$MenuBridge$receiptCount(windows.ac))),
					_Utils_Tuple2('menu', menu)
				]));
		return _Utils_Tuple2(
			next,
			A2($elm$core$List$cons, row, rows));
	});
var $author$project$MenuSurfaceReplay$incoming = _Platform_incomingPort('incoming', $elm$json$Json$Decode$value);
var $author$project$Launch$init = {S: $elm$core$Maybe$Nothing, aU: $author$project$Launch$Idle, a6: $author$project$UInt64$zero, cP: $author$project$UInt64$zero, aw: $elm$core$Maybe$Nothing};
var $author$project$ReceiptRouter$empty = _List_Nil;
var $author$project$Menu$init = {F: false, T: _List_Nil, aN: $elm$core$Maybe$Nothing, ap: $elm$core$Maybe$Nothing, aQ: 1, aR: 1, j: _List_Nil, Z: _List_Nil};
var $author$project$MenuBridge$initial = {ap: $author$project$Menu$init, at: $elm$core$Maybe$Nothing, av: $author$project$ReceiptRouter$empty};
var $author$project$Effects$empty = {R: false, cx: $author$project$UInt64$zero, aS: $elm$core$Maybe$Nothing, a6: $author$project$UInt64$zero, r: $elm$core$Maybe$Nothing, f: _List_Nil};
var $author$project$Shell$initial = {c: $elm$core$Maybe$Nothing, aE: $author$project$Effects$empty, k: $elm$core$Maybe$Nothing, bG: $elm$core$Maybe$Nothing, cy: $elm$core$Maybe$Nothing, cz: $elm$core$Maybe$Nothing, cA: $elm$core$Maybe$Nothing, H: _List_Nil, n: 'Connecting…', ad: false, aU: 0, Y: true, au: $elm$core$Maybe$Nothing, a6: $author$project$UInt64$zero};
var $author$project$TaskbarShell$initial = {cx: $author$project$UInt64$zero, ac: $author$project$MenuBridge$initial, D: $elm$core$Maybe$Nothing, b: $author$project$Shell$initial};
var $author$project$Desktop$initial = {
	P: $elm$core$Maybe$Nothing,
	s: $elm$core$Maybe$Nothing,
	E: '',
	k: $elm$core$Maybe$Nothing,
	d: $author$project$Launch$init,
	J: $elm$core$Maybe$Nothing,
	C: false,
	aT: false,
	as: $elm$core$Maybe$Nothing,
	X: $elm$core$Maybe$Just($author$project$UInt64$zero),
	a6: $author$project$UInt64$zero,
	w: $elm$core$Maybe$Nothing,
	a: $author$project$TaskbarShell$initial
};
var $author$project$SurfaceController$initial = {h: $author$project$Desktop$initial, F: false, I: $author$project$UInt64$zero, ag: $author$project$UInt64$zero};
var $elm$core$Platform$Cmd$batch = _Platform_batch;
var $elm$core$Platform$Cmd$none = $elm$core$Platform$Cmd$batch(_List_Nil);
var $author$project$MenuSurfaceReplay$outgoing = _Platform_outgoingPort('outgoing', $elm$core$Basics$identity);
var $elm$core$Platform$worker = _Platform_worker;
var $author$project$MenuSurfaceReplay$main = $elm$core$Platform$worker(
	{
		cE: function (_v0) {
			return _Utils_Tuple2(0, $elm$core$Platform$Cmd$none);
		},
		cQ: function (_v1) {
			return $author$project$MenuSurfaceReplay$incoming($elm$core$Basics$identity);
		},
		cR: F2(
			function (_v2, _v3) {
				var raw = _v2;
				var events = A2(
					$elm$core$Result$withDefault,
					_List_Nil,
					A2(
						$elm$json$Json$Decode$decodeValue,
						$elm$json$Json$Decode$list($elm$json$Json$Decode$value),
						raw));
				var _v4 = A3(
					$elm$core$List$foldl,
					$author$project$MenuSurfaceReplay$apply,
					_Utils_Tuple2($author$project$SurfaceController$initial, _List_Nil),
					events);
				var rows = _v4.b;
				return _Utils_Tuple2(
					0,
					$author$project$MenuSurfaceReplay$outgoing(
						A2(
							$elm$json$Json$Encode$list,
							$elm$core$Basics$identity,
							$elm$core$List$reverse(rows))));
			})
	});
_Platform_export({'MenuSurfaceReplay':{'init':$author$project$MenuSurfaceReplay$main(
	$elm$json$Json$Decode$succeed(0))(0)}});}(this));