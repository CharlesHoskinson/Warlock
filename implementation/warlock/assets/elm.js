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
	if (region.cw.bx === region.cI.bx)
	{
		return 'on line ' + region.cw.bx;
	}
	return 'on lines ' + region.cw.bx + ' through ' + region.cI.bx;
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
		impl.dW,
		impl.ee,
		impl.ec,
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




// HELPERS


var _VirtualDom_divertHrefToApp;

var _VirtualDom_doc = typeof document !== 'undefined' ? document : {};


function _VirtualDom_appendChild(parent, child)
{
	parent.appendChild(child);
}

var _VirtualDom_init = F4(function(virtualNode, flagDecoder, debugMetadata, args)
{
	// NOTE: this function needs _Platform_export available to work

	/**/
	var node = args['node'];
	//*/
	/**_UNUSED/
	var node = args && args['node'] ? args['node'] : _Debug_crash(0);
	//*/

	node.parentNode.replaceChild(
		_VirtualDom_render(virtualNode, function() {}),
		node
	);

	return {};
});



// TEXT


function _VirtualDom_text(string)
{
	return {
		$: 0,
		a: string
	};
}



// NODE


var _VirtualDom_nodeNS = F2(function(namespace, tag)
{
	return F2(function(factList, kidList)
	{
		for (var kids = [], descendantsCount = 0; kidList.b; kidList = kidList.b) // WHILE_CONS
		{
			var kid = kidList.a;
			descendantsCount += (kid.b || 0);
			kids.push(kid);
		}
		descendantsCount += kids.length;

		return {
			$: 1,
			c: tag,
			d: _VirtualDom_organizeFacts(factList),
			e: kids,
			f: namespace,
			b: descendantsCount
		};
	});
});


var _VirtualDom_node = _VirtualDom_nodeNS(undefined);



// KEYED NODE


var _VirtualDom_keyedNodeNS = F2(function(namespace, tag)
{
	return F2(function(factList, kidList)
	{
		for (var kids = [], descendantsCount = 0; kidList.b; kidList = kidList.b) // WHILE_CONS
		{
			var kid = kidList.a;
			descendantsCount += (kid.b.b || 0);
			kids.push(kid);
		}
		descendantsCount += kids.length;

		return {
			$: 2,
			c: tag,
			d: _VirtualDom_organizeFacts(factList),
			e: kids,
			f: namespace,
			b: descendantsCount
		};
	});
});


var _VirtualDom_keyedNode = _VirtualDom_keyedNodeNS(undefined);



// CUSTOM


function _VirtualDom_custom(factList, model, render, diff)
{
	return {
		$: 3,
		d: _VirtualDom_organizeFacts(factList),
		g: model,
		h: render,
		i: diff
	};
}



// MAP


var _VirtualDom_map = F2(function(tagger, node)
{
	return {
		$: 4,
		j: tagger,
		k: node,
		b: 1 + (node.b || 0)
	};
});



// LAZY


function _VirtualDom_thunk(refs, thunk)
{
	return {
		$: 5,
		l: refs,
		m: thunk,
		k: undefined
	};
}

var _VirtualDom_lazy = F2(function(func, a)
{
	return _VirtualDom_thunk([func, a], function() {
		return func(a);
	});
});

var _VirtualDom_lazy2 = F3(function(func, a, b)
{
	return _VirtualDom_thunk([func, a, b], function() {
		return A2(func, a, b);
	});
});

var _VirtualDom_lazy3 = F4(function(func, a, b, c)
{
	return _VirtualDom_thunk([func, a, b, c], function() {
		return A3(func, a, b, c);
	});
});

var _VirtualDom_lazy4 = F5(function(func, a, b, c, d)
{
	return _VirtualDom_thunk([func, a, b, c, d], function() {
		return A4(func, a, b, c, d);
	});
});

var _VirtualDom_lazy5 = F6(function(func, a, b, c, d, e)
{
	return _VirtualDom_thunk([func, a, b, c, d, e], function() {
		return A5(func, a, b, c, d, e);
	});
});

var _VirtualDom_lazy6 = F7(function(func, a, b, c, d, e, f)
{
	return _VirtualDom_thunk([func, a, b, c, d, e, f], function() {
		return A6(func, a, b, c, d, e, f);
	});
});

var _VirtualDom_lazy7 = F8(function(func, a, b, c, d, e, f, g)
{
	return _VirtualDom_thunk([func, a, b, c, d, e, f, g], function() {
		return A7(func, a, b, c, d, e, f, g);
	});
});

var _VirtualDom_lazy8 = F9(function(func, a, b, c, d, e, f, g, h)
{
	return _VirtualDom_thunk([func, a, b, c, d, e, f, g, h], function() {
		return A8(func, a, b, c, d, e, f, g, h);
	});
});



// FACTS


var _VirtualDom_on = F2(function(key, handler)
{
	return {
		$: 'a0',
		n: key,
		o: handler
	};
});
var _VirtualDom_style = F2(function(key, value)
{
	return {
		$: 'a1',
		n: key,
		o: value
	};
});
var _VirtualDom_property = F2(function(key, value)
{
	return {
		$: 'a2',
		n: key,
		o: value
	};
});
var _VirtualDom_attribute = F2(function(key, value)
{
	return {
		$: 'a3',
		n: key,
		o: value
	};
});
var _VirtualDom_attributeNS = F3(function(namespace, key, value)
{
	return {
		$: 'a4',
		n: key,
		o: { f: namespace, o: value }
	};
});



// XSS ATTACK VECTOR CHECKS
//
// For some reason, tabs can appear in href protocols and it still works.
// So '\tjava\tSCRIPT:alert("!!!")' and 'javascript:alert("!!!")' are the same
// in practice. That is why _VirtualDom_RE_js and _VirtualDom_RE_js_html look
// so freaky.
//
// Pulling the regular expressions out to the top level gives a slight speed
// boost in small benchmarks (4-10%) but hoisting values to reduce allocation
// can be unpredictable in large programs where JIT may have a harder time with
// functions are not fully self-contained. The benefit is more that the js and
// js_html ones are so weird that I prefer to see them near each other.


var _VirtualDom_RE_script = /^script$/i;
var _VirtualDom_RE_on_formAction = /^(on|formAction$)/i;
var _VirtualDom_RE_js = /^\s*j\s*a\s*v\s*a\s*s\s*c\s*r\s*i\s*p\s*t\s*:/i;
var _VirtualDom_RE_js_html = /^\s*(j\s*a\s*v\s*a\s*s\s*c\s*r\s*i\s*p\s*t\s*:|d\s*a\s*t\s*a\s*:\s*t\s*e\s*x\s*t\s*\/\s*h\s*t\s*m\s*l\s*(,|;))/i;


function _VirtualDom_noScript(tag)
{
	return _VirtualDom_RE_script.test(tag) ? 'p' : tag;
}

function _VirtualDom_noOnOrFormAction(key)
{
	return _VirtualDom_RE_on_formAction.test(key) ? 'data-' + key : key;
}

function _VirtualDom_noInnerHtmlOrFormAction(key)
{
	return key == 'innerHTML' || key == 'formAction' ? 'data-' + key : key;
}

function _VirtualDom_noJavaScriptUri(value)
{
	return _VirtualDom_RE_js.test(value)
		? /**/''//*//**_UNUSED/'javascript:alert("This is an XSS vector. Please use ports or web components instead.")'//*/
		: value;
}

function _VirtualDom_noJavaScriptOrHtmlUri(value)
{
	return _VirtualDom_RE_js_html.test(value)
		? /**/''//*//**_UNUSED/'javascript:alert("This is an XSS vector. Please use ports or web components instead.")'//*/
		: value;
}

function _VirtualDom_noJavaScriptOrHtmlJson(value)
{
	return (typeof _Json_unwrap(value) === 'string' && _VirtualDom_RE_js_html.test(_Json_unwrap(value)))
		? _Json_wrap(
			/**/''//*//**_UNUSED/'javascript:alert("This is an XSS vector. Please use ports or web components instead.")'//*/
		) : value;
}



// MAP FACTS


var _VirtualDom_mapAttribute = F2(function(func, attr)
{
	return (attr.$ === 'a0')
		? A2(_VirtualDom_on, attr.n, _VirtualDom_mapHandler(func, attr.o))
		: attr;
});

function _VirtualDom_mapHandler(func, handler)
{
	var tag = $elm$virtual_dom$VirtualDom$toHandlerInt(handler);

	// 0 = Normal
	// 1 = MayStopPropagation
	// 2 = MayPreventDefault
	// 3 = Custom

	return {
		$: handler.$,
		a:
			!tag
				? A2($elm$json$Json$Decode$map, func, handler.a)
				:
			A3($elm$json$Json$Decode$map2,
				tag < 3
					? _VirtualDom_mapEventTuple
					: _VirtualDom_mapEventRecord,
				$elm$json$Json$Decode$succeed(func),
				handler.a
			)
	};
}

var _VirtualDom_mapEventTuple = F2(function(func, tuple)
{
	return _Utils_Tuple2(func(tuple.a), tuple.b);
});

var _VirtualDom_mapEventRecord = F2(function(func, record)
{
	return {
		g: func(record.g),
		cy: record.cy,
		cq: record.cq
	}
});



// ORGANIZE FACTS


function _VirtualDom_organizeFacts(factList)
{
	for (var facts = {}; factList.b; factList = factList.b) // WHILE_CONS
	{
		var entry = factList.a;

		var tag = entry.$;
		var key = entry.n;
		var value = entry.o;

		if (tag === 'a2')
		{
			(key === 'className')
				? _VirtualDom_addClass(facts, key, _Json_unwrap(value))
				: facts[key] = _Json_unwrap(value);

			continue;
		}

		var subFacts = facts[tag] || (facts[tag] = {});
		(tag === 'a3' && key === 'class')
			? _VirtualDom_addClass(subFacts, key, value)
			: subFacts[key] = value;
	}

	return facts;
}

function _VirtualDom_addClass(object, key, newClass)
{
	var classes = object[key];
	object[key] = classes ? classes + ' ' + newClass : newClass;
}



// RENDER


function _VirtualDom_render(vNode, eventNode)
{
	var tag = vNode.$;

	if (tag === 5)
	{
		return _VirtualDom_render(vNode.k || (vNode.k = vNode.m()), eventNode);
	}

	if (tag === 0)
	{
		return _VirtualDom_doc.createTextNode(vNode.a);
	}

	if (tag === 4)
	{
		var subNode = vNode.k;
		var tagger = vNode.j;

		while (subNode.$ === 4)
		{
			typeof tagger !== 'object'
				? tagger = [tagger, subNode.j]
				: tagger.push(subNode.j);

			subNode = subNode.k;
		}

		var subEventRoot = { j: tagger, p: eventNode };
		var domNode = _VirtualDom_render(subNode, subEventRoot);
		domNode.elm_event_node_ref = subEventRoot;
		return domNode;
	}

	if (tag === 3)
	{
		var domNode = vNode.h(vNode.g);
		_VirtualDom_applyFacts(domNode, eventNode, vNode.d);
		return domNode;
	}

	// at this point `tag` must be 1 or 2

	var domNode = vNode.f
		? _VirtualDom_doc.createElementNS(vNode.f, vNode.c)
		: _VirtualDom_doc.createElement(vNode.c);

	if (_VirtualDom_divertHrefToApp && vNode.c == 'a')
	{
		domNode.addEventListener('click', _VirtualDom_divertHrefToApp(domNode));
	}

	_VirtualDom_applyFacts(domNode, eventNode, vNode.d);

	for (var kids = vNode.e, i = 0; i < kids.length; i++)
	{
		_VirtualDom_appendChild(domNode, _VirtualDom_render(tag === 1 ? kids[i] : kids[i].b, eventNode));
	}

	return domNode;
}



// APPLY FACTS


function _VirtualDom_applyFacts(domNode, eventNode, facts)
{
	for (var key in facts)
	{
		var value = facts[key];

		key === 'a1'
			? _VirtualDom_applyStyles(domNode, value)
			:
		key === 'a0'
			? _VirtualDom_applyEvents(domNode, eventNode, value)
			:
		key === 'a3'
			? _VirtualDom_applyAttrs(domNode, value)
			:
		key === 'a4'
			? _VirtualDom_applyAttrsNS(domNode, value)
			:
		((key !== 'value' && key !== 'checked') || domNode[key] !== value) && (domNode[key] = value);
	}
}



// APPLY STYLES


function _VirtualDom_applyStyles(domNode, styles)
{
	var domNodeStyle = domNode.style;

	for (var key in styles)
	{
		domNodeStyle[key] = styles[key];
	}
}



// APPLY ATTRS


function _VirtualDom_applyAttrs(domNode, attrs)
{
	for (var key in attrs)
	{
		var value = attrs[key];
		typeof value !== 'undefined'
			? domNode.setAttribute(key, value)
			: domNode.removeAttribute(key);
	}
}



// APPLY NAMESPACED ATTRS


function _VirtualDom_applyAttrsNS(domNode, nsAttrs)
{
	for (var key in nsAttrs)
	{
		var pair = nsAttrs[key];
		var namespace = pair.f;
		var value = pair.o;

		typeof value !== 'undefined'
			? domNode.setAttributeNS(namespace, key, value)
			: domNode.removeAttributeNS(namespace, key);
	}
}



// APPLY EVENTS


function _VirtualDom_applyEvents(domNode, eventNode, events)
{
	var allCallbacks = domNode.elmFs || (domNode.elmFs = {});

	for (var key in events)
	{
		var newHandler = events[key];
		var oldCallback = allCallbacks[key];

		if (!newHandler)
		{
			domNode.removeEventListener(key, oldCallback);
			allCallbacks[key] = undefined;
			continue;
		}

		if (oldCallback)
		{
			var oldHandler = oldCallback.q;
			if (oldHandler.$ === newHandler.$)
			{
				oldCallback.q = newHandler;
				continue;
			}
			domNode.removeEventListener(key, oldCallback);
		}

		oldCallback = _VirtualDom_makeCallback(eventNode, newHandler);
		domNode.addEventListener(key, oldCallback,
			_VirtualDom_passiveSupported
			&& { passive: $elm$virtual_dom$VirtualDom$toHandlerInt(newHandler) < 2 }
		);
		allCallbacks[key] = oldCallback;
	}
}



// PASSIVE EVENTS


var _VirtualDom_passiveSupported;

try
{
	window.addEventListener('t', null, Object.defineProperty({}, 'passive', {
		get: function() { _VirtualDom_passiveSupported = true; }
	}));
}
catch(e) {}



// EVENT HANDLERS


function _VirtualDom_makeCallback(eventNode, initialHandler)
{
	function callback(event)
	{
		var handler = callback.q;
		var result = _Json_runHelp(handler.a, event);

		if (!$elm$core$Result$isOk(result))
		{
			return;
		}

		var tag = $elm$virtual_dom$VirtualDom$toHandlerInt(handler);

		// 0 = Normal
		// 1 = MayStopPropagation
		// 2 = MayPreventDefault
		// 3 = Custom

		var value = result.a;
		var message = !tag ? value : tag < 3 ? value.a : value.g;
		var stopPropagation = tag == 1 ? value.b : tag == 3 && value.cy;
		var currentEventNode = (
			stopPropagation && event.stopPropagation(),
			(tag == 2 ? value.b : tag == 3 && value.cq) && event.preventDefault(),
			eventNode
		);
		var tagger;
		var i;
		while (tagger = currentEventNode.j)
		{
			if (typeof tagger == 'function')
			{
				message = tagger(message);
			}
			else
			{
				for (var i = tagger.length; i--; )
				{
					message = tagger[i](message);
				}
			}
			currentEventNode = currentEventNode.p;
		}
		currentEventNode(message, stopPropagation); // stopPropagation implies isSync
	}

	callback.q = initialHandler;

	return callback;
}

function _VirtualDom_equalEvents(x, y)
{
	return x.$ == y.$ && _Json_equality(x.a, y.a);
}



// DIFF


// TODO: Should we do patches like in iOS?
//
// type Patch
//   = At Int Patch
//   | Batch (List Patch)
//   | Change ...
//
// How could it not be better?
//
function _VirtualDom_diff(x, y)
{
	var patches = [];
	_VirtualDom_diffHelp(x, y, patches, 0);
	return patches;
}


function _VirtualDom_pushPatch(patches, type, index, data)
{
	var patch = {
		$: type,
		r: index,
		s: data,
		t: undefined,
		u: undefined
	};
	patches.push(patch);
	return patch;
}


function _VirtualDom_diffHelp(x, y, patches, index)
{
	if (x === y)
	{
		return;
	}

	var xType = x.$;
	var yType = y.$;

	// Bail if you run into different types of nodes. Implies that the
	// structure has changed significantly and it's not worth a diff.
	if (xType !== yType)
	{
		if (xType === 1 && yType === 2)
		{
			y = _VirtualDom_dekey(y);
			yType = 1;
		}
		else
		{
			_VirtualDom_pushPatch(patches, 0, index, y);
			return;
		}
	}

	// Now we know that both nodes are the same $.
	switch (yType)
	{
		case 5:
			var xRefs = x.l;
			var yRefs = y.l;
			var i = xRefs.length;
			var same = i === yRefs.length;
			while (same && i--)
			{
				same = xRefs[i] === yRefs[i];
			}
			if (same)
			{
				y.k = x.k;
				return;
			}
			y.k = y.m();
			var subPatches = [];
			_VirtualDom_diffHelp(x.k, y.k, subPatches, 0);
			subPatches.length > 0 && _VirtualDom_pushPatch(patches, 1, index, subPatches);
			return;

		case 4:
			// gather nested taggers
			var xTaggers = x.j;
			var yTaggers = y.j;
			var nesting = false;

			var xSubNode = x.k;
			while (xSubNode.$ === 4)
			{
				nesting = true;

				typeof xTaggers !== 'object'
					? xTaggers = [xTaggers, xSubNode.j]
					: xTaggers.push(xSubNode.j);

				xSubNode = xSubNode.k;
			}

			var ySubNode = y.k;
			while (ySubNode.$ === 4)
			{
				nesting = true;

				typeof yTaggers !== 'object'
					? yTaggers = [yTaggers, ySubNode.j]
					: yTaggers.push(ySubNode.j);

				ySubNode = ySubNode.k;
			}

			// Just bail if different numbers of taggers. This implies the
			// structure of the virtual DOM has changed.
			if (nesting && xTaggers.length !== yTaggers.length)
			{
				_VirtualDom_pushPatch(patches, 0, index, y);
				return;
			}

			// check if taggers are "the same"
			if (nesting ? !_VirtualDom_pairwiseRefEqual(xTaggers, yTaggers) : xTaggers !== yTaggers)
			{
				_VirtualDom_pushPatch(patches, 2, index, yTaggers);
			}

			// diff everything below the taggers
			_VirtualDom_diffHelp(xSubNode, ySubNode, patches, index + 1);
			return;

		case 0:
			if (x.a !== y.a)
			{
				_VirtualDom_pushPatch(patches, 3, index, y.a);
			}
			return;

		case 1:
			_VirtualDom_diffNodes(x, y, patches, index, _VirtualDom_diffKids);
			return;

		case 2:
			_VirtualDom_diffNodes(x, y, patches, index, _VirtualDom_diffKeyedKids);
			return;

		case 3:
			if (x.h !== y.h)
			{
				_VirtualDom_pushPatch(patches, 0, index, y);
				return;
			}

			var factsDiff = _VirtualDom_diffFacts(x.d, y.d);
			factsDiff && _VirtualDom_pushPatch(patches, 4, index, factsDiff);

			var patch = y.i(x.g, y.g);
			patch && _VirtualDom_pushPatch(patches, 5, index, patch);

			return;
	}
}

// assumes the incoming arrays are the same length
function _VirtualDom_pairwiseRefEqual(as, bs)
{
	for (var i = 0; i < as.length; i++)
	{
		if (as[i] !== bs[i])
		{
			return false;
		}
	}

	return true;
}

function _VirtualDom_diffNodes(x, y, patches, index, diffKids)
{
	// Bail if obvious indicators have changed. Implies more serious
	// structural changes such that it's not worth it to diff.
	if (x.c !== y.c || x.f !== y.f)
	{
		_VirtualDom_pushPatch(patches, 0, index, y);
		return;
	}

	var factsDiff = _VirtualDom_diffFacts(x.d, y.d);
	factsDiff && _VirtualDom_pushPatch(patches, 4, index, factsDiff);

	diffKids(x, y, patches, index);
}



// DIFF FACTS


// TODO Instead of creating a new diff object, it's possible to just test if
// there *is* a diff. During the actual patch, do the diff again and make the
// modifications directly. This way, there's no new allocations. Worth it?
function _VirtualDom_diffFacts(x, y, category)
{
	var diff;

	// look for changes and removals
	for (var xKey in x)
	{
		if (xKey === 'a1' || xKey === 'a0' || xKey === 'a3' || xKey === 'a4')
		{
			var subDiff = _VirtualDom_diffFacts(x[xKey], y[xKey] || {}, xKey);
			if (subDiff)
			{
				diff = diff || {};
				diff[xKey] = subDiff;
			}
			continue;
		}

		// remove if not in the new facts
		if (!(xKey in y))
		{
			diff = diff || {};
			diff[xKey] =
				!category
					? (typeof x[xKey] === 'string' ? '' : null)
					:
				(category === 'a1')
					? ''
					:
				(category === 'a0' || category === 'a3')
					? undefined
					:
				{ f: x[xKey].f, o: undefined };

			continue;
		}

		var xValue = x[xKey];
		var yValue = y[xKey];

		// reference equal, so don't worry about it
		if (xValue === yValue && xKey !== 'value' && xKey !== 'checked'
			|| category === 'a0' && _VirtualDom_equalEvents(xValue, yValue))
		{
			continue;
		}

		diff = diff || {};
		diff[xKey] = yValue;
	}

	// add new stuff
	for (var yKey in y)
	{
		if (!(yKey in x))
		{
			diff = diff || {};
			diff[yKey] = y[yKey];
		}
	}

	return diff;
}



// DIFF KIDS


function _VirtualDom_diffKids(xParent, yParent, patches, index)
{
	var xKids = xParent.e;
	var yKids = yParent.e;

	var xLen = xKids.length;
	var yLen = yKids.length;

	// FIGURE OUT IF THERE ARE INSERTS OR REMOVALS

	if (xLen > yLen)
	{
		_VirtualDom_pushPatch(patches, 6, index, {
			v: yLen,
			i: xLen - yLen
		});
	}
	else if (xLen < yLen)
	{
		_VirtualDom_pushPatch(patches, 7, index, {
			v: xLen,
			e: yKids
		});
	}

	// PAIRWISE DIFF EVERYTHING ELSE

	for (var minLen = xLen < yLen ? xLen : yLen, i = 0; i < minLen; i++)
	{
		var xKid = xKids[i];
		_VirtualDom_diffHelp(xKid, yKids[i], patches, ++index);
		index += xKid.b || 0;
	}
}



// KEYED DIFF


function _VirtualDom_diffKeyedKids(xParent, yParent, patches, rootIndex)
{
	var localPatches = [];

	var changes = {}; // Dict String Entry
	var inserts = []; // Array { index : Int, entry : Entry }
	// type Entry = { tag : String, vnode : VNode, index : Int, data : _ }

	var xKids = xParent.e;
	var yKids = yParent.e;
	var xLen = xKids.length;
	var yLen = yKids.length;
	var xIndex = 0;
	var yIndex = 0;

	var index = rootIndex;

	while (xIndex < xLen && yIndex < yLen)
	{
		var x = xKids[xIndex];
		var y = yKids[yIndex];

		var xKey = x.a;
		var yKey = y.a;
		var xNode = x.b;
		var yNode = y.b;

		var newMatch = undefined;
		var oldMatch = undefined;

		// check if keys match

		if (xKey === yKey)
		{
			index++;
			_VirtualDom_diffHelp(xNode, yNode, localPatches, index);
			index += xNode.b || 0;

			xIndex++;
			yIndex++;
			continue;
		}

		// look ahead 1 to detect insertions and removals.

		var xNext = xKids[xIndex + 1];
		var yNext = yKids[yIndex + 1];

		if (xNext)
		{
			var xNextKey = xNext.a;
			var xNextNode = xNext.b;
			oldMatch = yKey === xNextKey;
		}

		if (yNext)
		{
			var yNextKey = yNext.a;
			var yNextNode = yNext.b;
			newMatch = xKey === yNextKey;
		}


		// swap x and y
		if (newMatch && oldMatch)
		{
			index++;
			_VirtualDom_diffHelp(xNode, yNextNode, localPatches, index);
			_VirtualDom_insertNode(changes, localPatches, xKey, yNode, yIndex, inserts);
			index += xNode.b || 0;

			index++;
			_VirtualDom_removeNode(changes, localPatches, xKey, xNextNode, index);
			index += xNextNode.b || 0;

			xIndex += 2;
			yIndex += 2;
			continue;
		}

		// insert y
		if (newMatch)
		{
			index++;
			_VirtualDom_insertNode(changes, localPatches, yKey, yNode, yIndex, inserts);
			_VirtualDom_diffHelp(xNode, yNextNode, localPatches, index);
			index += xNode.b || 0;

			xIndex += 1;
			yIndex += 2;
			continue;
		}

		// remove x
		if (oldMatch)
		{
			index++;
			_VirtualDom_removeNode(changes, localPatches, xKey, xNode, index);
			index += xNode.b || 0;

			index++;
			_VirtualDom_diffHelp(xNextNode, yNode, localPatches, index);
			index += xNextNode.b || 0;

			xIndex += 2;
			yIndex += 1;
			continue;
		}

		// remove x, insert y
		if (xNext && xNextKey === yNextKey)
		{
			index++;
			_VirtualDom_removeNode(changes, localPatches, xKey, xNode, index);
			_VirtualDom_insertNode(changes, localPatches, yKey, yNode, yIndex, inserts);
			index += xNode.b || 0;

			index++;
			_VirtualDom_diffHelp(xNextNode, yNextNode, localPatches, index);
			index += xNextNode.b || 0;

			xIndex += 2;
			yIndex += 2;
			continue;
		}

		break;
	}

	// eat up any remaining nodes with removeNode and insertNode

	while (xIndex < xLen)
	{
		index++;
		var x = xKids[xIndex];
		var xNode = x.b;
		_VirtualDom_removeNode(changes, localPatches, x.a, xNode, index);
		index += xNode.b || 0;
		xIndex++;
	}

	while (yIndex < yLen)
	{
		var endInserts = endInserts || [];
		var y = yKids[yIndex];
		_VirtualDom_insertNode(changes, localPatches, y.a, y.b, undefined, endInserts);
		yIndex++;
	}

	if (localPatches.length > 0 || inserts.length > 0 || endInserts)
	{
		_VirtualDom_pushPatch(patches, 8, rootIndex, {
			w: localPatches,
			x: inserts,
			y: endInserts
		});
	}
}



// CHANGES FROM KEYED DIFF


var _VirtualDom_POSTFIX = '_elmW6BL';


function _VirtualDom_insertNode(changes, localPatches, key, vnode, yIndex, inserts)
{
	var entry = changes[key];

	// never seen this key before
	if (!entry)
	{
		entry = {
			c: 0,
			z: vnode,
			r: yIndex,
			s: undefined
		};

		inserts.push({ r: yIndex, A: entry });
		changes[key] = entry;

		return;
	}

	// this key was removed earlier, a match!
	if (entry.c === 1)
	{
		inserts.push({ r: yIndex, A: entry });

		entry.c = 2;
		var subPatches = [];
		_VirtualDom_diffHelp(entry.z, vnode, subPatches, entry.r);
		entry.r = yIndex;
		entry.s.s = {
			w: subPatches,
			A: entry
		};

		return;
	}

	// this key has already been inserted or moved, a duplicate!
	_VirtualDom_insertNode(changes, localPatches, key + _VirtualDom_POSTFIX, vnode, yIndex, inserts);
}


function _VirtualDom_removeNode(changes, localPatches, key, vnode, index)
{
	var entry = changes[key];

	// never seen this key before
	if (!entry)
	{
		var patch = _VirtualDom_pushPatch(localPatches, 9, index, undefined);

		changes[key] = {
			c: 1,
			z: vnode,
			r: index,
			s: patch
		};

		return;
	}

	// this key was inserted earlier, a match!
	if (entry.c === 0)
	{
		entry.c = 2;
		var subPatches = [];
		_VirtualDom_diffHelp(vnode, entry.z, subPatches, index);

		_VirtualDom_pushPatch(localPatches, 9, index, {
			w: subPatches,
			A: entry
		});

		return;
	}

	// this key has already been removed or moved, a duplicate!
	_VirtualDom_removeNode(changes, localPatches, key + _VirtualDom_POSTFIX, vnode, index);
}



// ADD DOM NODES
//
// Each DOM node has an "index" assigned in order of traversal. It is important
// to minimize our crawl over the actual DOM, so these indexes (along with the
// descendantsCount of virtual nodes) let us skip touching entire subtrees of
// the DOM if we know there are no patches there.


function _VirtualDom_addDomNodes(domNode, vNode, patches, eventNode)
{
	_VirtualDom_addDomNodesHelp(domNode, vNode, patches, 0, 0, vNode.b, eventNode);
}


// assumes `patches` is non-empty and indexes increase monotonically.
function _VirtualDom_addDomNodesHelp(domNode, vNode, patches, i, low, high, eventNode)
{
	var patch = patches[i];
	var index = patch.r;

	while (index === low)
	{
		var patchType = patch.$;

		if (patchType === 1)
		{
			_VirtualDom_addDomNodes(domNode, vNode.k, patch.s, eventNode);
		}
		else if (patchType === 8)
		{
			patch.t = domNode;
			patch.u = eventNode;

			var subPatches = patch.s.w;
			if (subPatches.length > 0)
			{
				_VirtualDom_addDomNodesHelp(domNode, vNode, subPatches, 0, low, high, eventNode);
			}
		}
		else if (patchType === 9)
		{
			patch.t = domNode;
			patch.u = eventNode;

			var data = patch.s;
			if (data)
			{
				data.A.s = domNode;
				var subPatches = data.w;
				if (subPatches.length > 0)
				{
					_VirtualDom_addDomNodesHelp(domNode, vNode, subPatches, 0, low, high, eventNode);
				}
			}
		}
		else
		{
			patch.t = domNode;
			patch.u = eventNode;
		}

		i++;

		if (!(patch = patches[i]) || (index = patch.r) > high)
		{
			return i;
		}
	}

	var tag = vNode.$;

	if (tag === 4)
	{
		var subNode = vNode.k;

		while (subNode.$ === 4)
		{
			subNode = subNode.k;
		}

		return _VirtualDom_addDomNodesHelp(domNode, subNode, patches, i, low + 1, high, domNode.elm_event_node_ref);
	}

	// tag must be 1 or 2 at this point

	var vKids = vNode.e;
	var childNodes = domNode.childNodes;
	for (var j = 0; j < vKids.length; j++)
	{
		low++;
		var vKid = tag === 1 ? vKids[j] : vKids[j].b;
		var nextLow = low + (vKid.b || 0);
		if (low <= index && index <= nextLow)
		{
			i = _VirtualDom_addDomNodesHelp(childNodes[j], vKid, patches, i, low, nextLow, eventNode);
			if (!(patch = patches[i]) || (index = patch.r) > high)
			{
				return i;
			}
		}
		low = nextLow;
	}
	return i;
}



// APPLY PATCHES


function _VirtualDom_applyPatches(rootDomNode, oldVirtualNode, patches, eventNode)
{
	if (patches.length === 0)
	{
		return rootDomNode;
	}

	_VirtualDom_addDomNodes(rootDomNode, oldVirtualNode, patches, eventNode);
	return _VirtualDom_applyPatchesHelp(rootDomNode, patches);
}

function _VirtualDom_applyPatchesHelp(rootDomNode, patches)
{
	for (var i = 0; i < patches.length; i++)
	{
		var patch = patches[i];
		var localDomNode = patch.t
		var newNode = _VirtualDom_applyPatch(localDomNode, patch);
		if (localDomNode === rootDomNode)
		{
			rootDomNode = newNode;
		}
	}
	return rootDomNode;
}

function _VirtualDom_applyPatch(domNode, patch)
{
	switch (patch.$)
	{
		case 0:
			return _VirtualDom_applyPatchRedraw(domNode, patch.s, patch.u);

		case 4:
			_VirtualDom_applyFacts(domNode, patch.u, patch.s);
			return domNode;

		case 3:
			domNode.replaceData(0, domNode.length, patch.s);
			return domNode;

		case 1:
			return _VirtualDom_applyPatchesHelp(domNode, patch.s);

		case 2:
			if (domNode.elm_event_node_ref)
			{
				domNode.elm_event_node_ref.j = patch.s;
			}
			else
			{
				domNode.elm_event_node_ref = { j: patch.s, p: patch.u };
			}
			return domNode;

		case 6:
			var data = patch.s;
			for (var i = 0; i < data.i; i++)
			{
				domNode.removeChild(domNode.childNodes[data.v]);
			}
			return domNode;

		case 7:
			var data = patch.s;
			var kids = data.e;
			var i = data.v;
			var theEnd = domNode.childNodes[i];
			for (; i < kids.length; i++)
			{
				domNode.insertBefore(_VirtualDom_render(kids[i], patch.u), theEnd);
			}
			return domNode;

		case 9:
			var data = patch.s;
			if (!data)
			{
				domNode.parentNode.removeChild(domNode);
				return domNode;
			}
			var entry = data.A;
			if (typeof entry.r !== 'undefined')
			{
				domNode.parentNode.removeChild(domNode);
			}
			entry.s = _VirtualDom_applyPatchesHelp(domNode, data.w);
			return domNode;

		case 8:
			return _VirtualDom_applyPatchReorder(domNode, patch);

		case 5:
			return patch.s(domNode);

		default:
			_Debug_crash(10); // 'Ran into an unknown patch!'
	}
}


function _VirtualDom_applyPatchRedraw(domNode, vNode, eventNode)
{
	var parentNode = domNode.parentNode;
	var newNode = _VirtualDom_render(vNode, eventNode);

	if (!newNode.elm_event_node_ref)
	{
		newNode.elm_event_node_ref = domNode.elm_event_node_ref;
	}

	if (parentNode && newNode !== domNode)
	{
		parentNode.replaceChild(newNode, domNode);
	}
	return newNode;
}


function _VirtualDom_applyPatchReorder(domNode, patch)
{
	var data = patch.s;

	// remove end inserts
	var frag = _VirtualDom_applyPatchReorderEndInsertsHelp(data.y, patch);

	// removals
	domNode = _VirtualDom_applyPatchesHelp(domNode, data.w);

	// inserts
	var inserts = data.x;
	for (var i = 0; i < inserts.length; i++)
	{
		var insert = inserts[i];
		var entry = insert.A;
		var node = entry.c === 2
			? entry.s
			: _VirtualDom_render(entry.z, patch.u);
		domNode.insertBefore(node, domNode.childNodes[insert.r]);
	}

	// add end inserts
	if (frag)
	{
		_VirtualDom_appendChild(domNode, frag);
	}

	return domNode;
}


function _VirtualDom_applyPatchReorderEndInsertsHelp(endInserts, patch)
{
	if (!endInserts)
	{
		return;
	}

	var frag = _VirtualDom_doc.createDocumentFragment();
	for (var i = 0; i < endInserts.length; i++)
	{
		var insert = endInserts[i];
		var entry = insert.A;
		_VirtualDom_appendChild(frag, entry.c === 2
			? entry.s
			: _VirtualDom_render(entry.z, patch.u)
		);
	}
	return frag;
}


function _VirtualDom_virtualize(node)
{
	// TEXT NODES

	if (node.nodeType === 3)
	{
		return _VirtualDom_text(node.textContent);
	}


	// WEIRD NODES

	if (node.nodeType !== 1)
	{
		return _VirtualDom_text('');
	}


	// ELEMENT NODES

	var attrList = _List_Nil;
	var attrs = node.attributes;
	for (var i = attrs.length; i--; )
	{
		var attr = attrs[i];
		var name = attr.name;
		var value = attr.value;
		attrList = _List_Cons( A2(_VirtualDom_attribute, name, value), attrList );
	}

	var tag = node.tagName.toLowerCase();
	var kidList = _List_Nil;
	var kids = node.childNodes;

	for (var i = kids.length; i--; )
	{
		kidList = _List_Cons(_VirtualDom_virtualize(kids[i]), kidList);
	}
	return A3(_VirtualDom_node, tag, attrList, kidList);
}

function _VirtualDom_dekey(keyedNode)
{
	var keyedKids = keyedNode.e;
	var len = keyedKids.length;
	var kids = new Array(len);
	for (var i = 0; i < len; i++)
	{
		kids[i] = keyedKids[i].b;
	}

	return {
		$: 1,
		c: keyedNode.c,
		d: keyedNode.d,
		e: kids,
		f: keyedNode.f,
		b: keyedNode.b
	};
}




// ELEMENT


var _Debugger_element;

var _Browser_element = _Debugger_element || F4(function(impl, flagDecoder, debugMetadata, args)
{
	return _Platform_initialize(
		flagDecoder,
		args,
		impl.dW,
		impl.ee,
		impl.ec,
		function(sendToApp, initialModel) {
			var view = impl.ef;
			/**/
			var domNode = args['node'];
			//*/
			/**_UNUSED/
			var domNode = args && args['node'] ? args['node'] : _Debug_crash(0);
			//*/
			var currNode = _VirtualDom_virtualize(domNode);

			return _Browser_makeAnimator(initialModel, function(model)
			{
				var nextNode = view(model);
				var patches = _VirtualDom_diff(currNode, nextNode);
				domNode = _VirtualDom_applyPatches(domNode, currNode, patches, sendToApp);
				currNode = nextNode;
			});
		}
	);
});



// DOCUMENT


var _Debugger_document;

var _Browser_document = _Debugger_document || F4(function(impl, flagDecoder, debugMetadata, args)
{
	return _Platform_initialize(
		flagDecoder,
		args,
		impl.dW,
		impl.ee,
		impl.ec,
		function(sendToApp, initialModel) {
			var divertHrefToApp = impl.cv && impl.cv(sendToApp)
			var view = impl.ef;
			var title = _VirtualDom_doc.title;
			var bodyNode = _VirtualDom_doc.body;
			var currNode = _VirtualDom_virtualize(bodyNode);
			return _Browser_makeAnimator(initialModel, function(model)
			{
				_VirtualDom_divertHrefToApp = divertHrefToApp;
				var doc = view(model);
				var nextNode = _VirtualDom_node('body')(_List_Nil)(doc.dF);
				var patches = _VirtualDom_diff(currNode, nextNode);
				bodyNode = _VirtualDom_applyPatches(bodyNode, currNode, patches, sendToApp);
				currNode = nextNode;
				_VirtualDom_divertHrefToApp = 0;
				(title !== doc.dr) && (_VirtualDom_doc.title = title = doc.dr);
			});
		}
	);
});



// ANIMATION


var _Browser_cancelAnimationFrame =
	typeof cancelAnimationFrame !== 'undefined'
		? cancelAnimationFrame
		: function(id) { clearTimeout(id); };

var _Browser_requestAnimationFrame =
	typeof requestAnimationFrame !== 'undefined'
		? requestAnimationFrame
		: function(callback) { return setTimeout(callback, 1000 / 60); };


function _Browser_makeAnimator(model, draw)
{
	draw(model);

	var state = 0;

	function updateIfNeeded()
	{
		state = state === 1
			? 0
			: ( _Browser_requestAnimationFrame(updateIfNeeded), draw(model), 1 );
	}

	return function(nextModel, isSync)
	{
		model = nextModel;

		isSync
			? ( draw(model),
				state === 2 && (state = 1)
				)
			: ( state === 0 && _Browser_requestAnimationFrame(updateIfNeeded),
				state = 2
				);
	};
}



// APPLICATION


function _Browser_application(impl)
{
	var onUrlChange = impl.d$;
	var onUrlRequest = impl.d0;
	var key = function() { key.a(onUrlChange(_Browser_getUrl())); };

	return _Browser_document({
		cv: function(sendToApp)
		{
			key.a = sendToApp;
			_Browser_window.addEventListener('popstate', key);
			_Browser_window.navigator.userAgent.indexOf('Trident') < 0 || _Browser_window.addEventListener('hashchange', key);

			return F2(function(domNode, event)
			{
				if (!event.ctrlKey && !event.metaKey && !event.shiftKey && event.button < 1 && !domNode.target && !domNode.hasAttribute('download'))
				{
					event.preventDefault();
					var href = domNode.href;
					var curr = _Browser_getUrl();
					var next = $elm$url$Url$fromString(href).a;
					sendToApp(onUrlRequest(
						(next
							&& curr.b_ === next.b_
							&& curr.aG === next.aG
							&& curr.c9.a === next.c9.a
						)
							? $elm$browser$Browser$Internal(next)
							: $elm$browser$Browser$External(href)
					));
				}
			});
		},
		dW: function(flags)
		{
			return A3(impl.dW, flags, _Browser_getUrl(), key);
		},
		ef: impl.ef,
		ee: impl.ee,
		ec: impl.ec
	});
}

function _Browser_getUrl()
{
	return $elm$url$Url$fromString(_VirtualDom_doc.location.href).a || _Debug_crash(1);
}

var _Browser_go = F2(function(key, n)
{
	return A2($elm$core$Task$perform, $elm$core$Basics$never, _Scheduler_binding(function() {
		n && history.go(n);
		key();
	}));
});

var _Browser_pushUrl = F2(function(key, url)
{
	return A2($elm$core$Task$perform, $elm$core$Basics$never, _Scheduler_binding(function() {
		history.pushState({}, '', url);
		key();
	}));
});

var _Browser_replaceUrl = F2(function(key, url)
{
	return A2($elm$core$Task$perform, $elm$core$Basics$never, _Scheduler_binding(function() {
		history.replaceState({}, '', url);
		key();
	}));
});



// GLOBAL EVENTS


var _Browser_fakeNode = { addEventListener: function() {}, removeEventListener: function() {} };
var _Browser_doc = typeof document !== 'undefined' ? document : _Browser_fakeNode;
var _Browser_window = typeof window !== 'undefined' ? window : _Browser_fakeNode;

var _Browser_on = F3(function(node, eventName, sendToSelf)
{
	return _Scheduler_spawn(_Scheduler_binding(function(callback)
	{
		function handler(event)	{ _Scheduler_rawSpawn(sendToSelf(event)); }
		node.addEventListener(eventName, handler, _VirtualDom_passiveSupported && { passive: true });
		return function() { node.removeEventListener(eventName, handler); };
	}));
});

var _Browser_decodeEvent = F2(function(decoder, event)
{
	var result = _Json_runHelp(decoder, event);
	return $elm$core$Result$isOk(result) ? $elm$core$Maybe$Just(result.a) : $elm$core$Maybe$Nothing;
});



// PAGE VISIBILITY


function _Browser_visibilityInfo()
{
	return (typeof _VirtualDom_doc.hidden !== 'undefined')
		? { dS: 'hidden', dH: 'visibilitychange' }
		:
	(typeof _VirtualDom_doc.mozHidden !== 'undefined')
		? { dS: 'mozHidden', dH: 'mozvisibilitychange' }
		:
	(typeof _VirtualDom_doc.msHidden !== 'undefined')
		? { dS: 'msHidden', dH: 'msvisibilitychange' }
		:
	(typeof _VirtualDom_doc.webkitHidden !== 'undefined')
		? { dS: 'webkitHidden', dH: 'webkitvisibilitychange' }
		: { dS: 'hidden', dH: 'visibilitychange' };
}



// ANIMATION FRAMES


function _Browser_rAF()
{
	return _Scheduler_binding(function(callback)
	{
		var id = _Browser_requestAnimationFrame(function() {
			callback(_Scheduler_succeed(Date.now()));
		});

		return function() {
			_Browser_cancelAnimationFrame(id);
		};
	});
}


function _Browser_now()
{
	return _Scheduler_binding(function(callback)
	{
		callback(_Scheduler_succeed(Date.now()));
	});
}



// DOM STUFF


function _Browser_withNode(id, doStuff)
{
	return _Scheduler_binding(function(callback)
	{
		_Browser_requestAnimationFrame(function() {
			var node = document.getElementById(id);
			callback(node
				? _Scheduler_succeed(doStuff(node))
				: _Scheduler_fail($elm$browser$Browser$Dom$NotFound(id))
			);
		});
	});
}


function _Browser_withWindow(doStuff)
{
	return _Scheduler_binding(function(callback)
	{
		_Browser_requestAnimationFrame(function() {
			callback(_Scheduler_succeed(doStuff()));
		});
	});
}


// FOCUS and BLUR


var _Browser_call = F2(function(functionName, id)
{
	return _Browser_withNode(id, function(node) {
		node[functionName]();
		return _Utils_Tuple0;
	});
});



// WINDOW VIEWPORT


function _Browser_getViewport()
{
	return {
		dk: _Browser_getScene(),
		dt: {
			ax: _Browser_window.pageXOffset,
			ay: _Browser_window.pageYOffset,
			aw: _Browser_doc.documentElement.clientWidth,
			an: _Browser_doc.documentElement.clientHeight
		}
	};
}

function _Browser_getScene()
{
	var body = _Browser_doc.body;
	var elem = _Browser_doc.documentElement;
	return {
		aw: Math.max(body.scrollWidth, body.offsetWidth, elem.scrollWidth, elem.offsetWidth, elem.clientWidth),
		an: Math.max(body.scrollHeight, body.offsetHeight, elem.scrollHeight, elem.offsetHeight, elem.clientHeight)
	};
}

var _Browser_setViewport = F2(function(x, y)
{
	return _Browser_withWindow(function()
	{
		_Browser_window.scroll(x, y);
		return _Utils_Tuple0;
	});
});



// ELEMENT VIEWPORT


function _Browser_getViewportOf(id)
{
	return _Browser_withNode(id, function(node)
	{
		return {
			dk: {
				aw: node.scrollWidth,
				an: node.scrollHeight
			},
			dt: {
				ax: node.scrollLeft,
				ay: node.scrollTop,
				aw: node.clientWidth,
				an: node.clientHeight
			}
		};
	});
}


var _Browser_setViewportOf = F3(function(id, x, y)
{
	return _Browser_withNode(id, function(node)
	{
		node.scrollLeft = x;
		node.scrollTop = y;
		return _Utils_Tuple0;
	});
});



// ELEMENT


function _Browser_getElement(id)
{
	return _Browser_withNode(id, function(node)
	{
		var rect = node.getBoundingClientRect();
		var x = _Browser_window.pageXOffset;
		var y = _Browser_window.pageYOffset;
		return {
			dk: _Browser_getScene(),
			dt: {
				ax: x,
				ay: y,
				aw: _Browser_doc.documentElement.clientWidth,
				an: _Browser_doc.documentElement.clientHeight
			},
			dJ: {
				ax: x + rect.left,
				ay: y + rect.top,
				aw: rect.width,
				an: rect.height
			}
		};
	});
}



// LOAD and RELOAD


function _Browser_reload(skipCache)
{
	return A2($elm$core$Task$perform, $elm$core$Basics$never, _Scheduler_binding(function(callback)
	{
		_VirtualDom_doc.location.reload(skipCache);
	}));
}

function _Browser_load(url)
{
	return A2($elm$core$Task$perform, $elm$core$Basics$never, _Scheduler_binding(function(callback)
	{
		try
		{
			_Browser_window.location = url;
		}
		catch(err)
		{
			// Only Firefox can throw a NS_ERROR_MALFORMED_URI exception here.
			// Other browsers reload the page, so let's be consistent about that.
			_VirtualDom_doc.location.reload(false);
		}
	}));
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
var $author$project$Main$Action = function (a) {
	return {$: 2, a: a};
};
var $author$project$Main$Dismiss = function (a) {
	return {$: 3, a: a};
};
var $author$project$Main$Disposition = function (a) {
	return {$: 0, a: a};
};
var $author$project$Main$Native = function (a) {
	return {$: 1, a: a};
};
var $author$project$Main$Reflow = function (a) {
	return {$: 4, a: a};
};
var $author$project$Main$Topology = function (a) {
	return {$: 5, a: a};
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
var $elm$core$Basics$False = 1;
var $elm$core$Basics$add = _Basics_add;
var $elm$core$Maybe$Just = function (a) {
	return {$: 0, a: a};
};
var $elm$core$Maybe$Nothing = {$: 1};
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
		if (!builder.x) {
			return A4(
				$elm$core$Array$Array_elm_builtin,
				$elm$core$Elm$JsArray$length(builder.B),
				$elm$core$Array$shiftStep,
				$elm$core$Elm$JsArray$empty,
				builder.B);
		} else {
			var treeLen = builder.x * $elm$core$Array$branchFactor;
			var depth = $elm$core$Basics$floor(
				A2($elm$core$Basics$logBase, $elm$core$Array$branchFactor, treeLen - 1));
			var correctNodeList = reverseNodeList ? $elm$core$List$reverse(builder.D) : builder.D;
			var tree = A2($elm$core$Array$treeFromBuilder, correctNodeList, builder.x);
			return A4(
				$elm$core$Array$Array_elm_builtin,
				$elm$core$Elm$JsArray$length(builder.B) + treeLen,
				A2($elm$core$Basics$max, 5, depth * $elm$core$Array$shiftStep),
				tree,
				builder.B);
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
					{D: nodeList, x: (len / $elm$core$Array$branchFactor) | 0, B: tail});
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
var $elm$core$Basics$True = 0;
var $elm$core$Result$isOk = function (result) {
	if (!result.$) {
		return true;
	} else {
		return false;
	}
};
var $elm$core$Platform$Sub$batch = _Platform_batch;
var $elm$json$Json$Decode$bool = _Json_decodeBool;
var $elm$json$Json$Decode$map = _Json_map1;
var $elm$json$Json$Decode$map2 = _Json_map2;
var $elm$json$Json$Decode$succeed = _Json_succeed;
var $elm$virtual_dom$VirtualDom$toHandlerInt = function (handler) {
	switch (handler.$) {
		case 0:
			return 0;
		case 1:
			return 1;
		case 2:
			return 2;
		default:
			return 3;
	}
};
var $elm$browser$Browser$External = function (a) {
	return {$: 1, a: a};
};
var $elm$browser$Browser$Internal = function (a) {
	return {$: 0, a: a};
};
var $elm$core$Basics$identity = function (x) {
	return x;
};
var $elm$browser$Browser$Dom$NotFound = $elm$core$Basics$identity;
var $elm$url$Url$Http = 0;
var $elm$url$Url$Https = 1;
var $elm$url$Url$Url = F6(
	function (protocol, host, port_, path, query, fragment) {
		return {cN: fragment, aG: host, c7: path, c9: port_, b_: protocol, b$: query};
	});
var $elm$core$String$contains = _String_contains;
var $elm$core$String$length = _String_length;
var $elm$core$String$slice = _String_slice;
var $elm$core$String$dropLeft = F2(
	function (n, string) {
		return (n < 1) ? string : A3(
			$elm$core$String$slice,
			n,
			$elm$core$String$length(string),
			string);
	});
var $elm$core$String$indexes = _String_indexes;
var $elm$core$String$isEmpty = function (string) {
	return string === '';
};
var $elm$core$String$left = F2(
	function (n, string) {
		return (n < 1) ? '' : A3($elm$core$String$slice, 0, n, string);
	});
var $elm$core$String$toInt = _String_toInt;
var $elm$url$Url$chompBeforePath = F5(
	function (protocol, path, params, frag, str) {
		if ($elm$core$String$isEmpty(str) || A2($elm$core$String$contains, '@', str)) {
			return $elm$core$Maybe$Nothing;
		} else {
			var _v0 = A2($elm$core$String$indexes, ':', str);
			if (!_v0.b) {
				return $elm$core$Maybe$Just(
					A6($elm$url$Url$Url, protocol, str, $elm$core$Maybe$Nothing, path, params, frag));
			} else {
				if (!_v0.b.b) {
					var i = _v0.a;
					var _v1 = $elm$core$String$toInt(
						A2($elm$core$String$dropLeft, i + 1, str));
					if (_v1.$ === 1) {
						return $elm$core$Maybe$Nothing;
					} else {
						var port_ = _v1;
						return $elm$core$Maybe$Just(
							A6(
								$elm$url$Url$Url,
								protocol,
								A2($elm$core$String$left, i, str),
								port_,
								path,
								params,
								frag));
					}
				} else {
					return $elm$core$Maybe$Nothing;
				}
			}
		}
	});
var $elm$url$Url$chompBeforeQuery = F4(
	function (protocol, params, frag, str) {
		if ($elm$core$String$isEmpty(str)) {
			return $elm$core$Maybe$Nothing;
		} else {
			var _v0 = A2($elm$core$String$indexes, '/', str);
			if (!_v0.b) {
				return A5($elm$url$Url$chompBeforePath, protocol, '/', params, frag, str);
			} else {
				var i = _v0.a;
				return A5(
					$elm$url$Url$chompBeforePath,
					protocol,
					A2($elm$core$String$dropLeft, i, str),
					params,
					frag,
					A2($elm$core$String$left, i, str));
			}
		}
	});
var $elm$url$Url$chompBeforeFragment = F3(
	function (protocol, frag, str) {
		if ($elm$core$String$isEmpty(str)) {
			return $elm$core$Maybe$Nothing;
		} else {
			var _v0 = A2($elm$core$String$indexes, '?', str);
			if (!_v0.b) {
				return A4($elm$url$Url$chompBeforeQuery, protocol, $elm$core$Maybe$Nothing, frag, str);
			} else {
				var i = _v0.a;
				return A4(
					$elm$url$Url$chompBeforeQuery,
					protocol,
					$elm$core$Maybe$Just(
						A2($elm$core$String$dropLeft, i + 1, str)),
					frag,
					A2($elm$core$String$left, i, str));
			}
		}
	});
var $elm$url$Url$chompAfterProtocol = F2(
	function (protocol, str) {
		if ($elm$core$String$isEmpty(str)) {
			return $elm$core$Maybe$Nothing;
		} else {
			var _v0 = A2($elm$core$String$indexes, '#', str);
			if (!_v0.b) {
				return A3($elm$url$Url$chompBeforeFragment, protocol, $elm$core$Maybe$Nothing, str);
			} else {
				var i = _v0.a;
				return A3(
					$elm$url$Url$chompBeforeFragment,
					protocol,
					$elm$core$Maybe$Just(
						A2($elm$core$String$dropLeft, i + 1, str)),
					A2($elm$core$String$left, i, str));
			}
		}
	});
var $elm$core$String$startsWith = _String_startsWith;
var $elm$url$Url$fromString = function (str) {
	return A2($elm$core$String$startsWith, 'http://', str) ? A2(
		$elm$url$Url$chompAfterProtocol,
		0,
		A2($elm$core$String$dropLeft, 7, str)) : (A2($elm$core$String$startsWith, 'https://', str) ? A2(
		$elm$url$Url$chompAfterProtocol,
		1,
		A2($elm$core$String$dropLeft, 8, str)) : $elm$core$Maybe$Nothing);
};
var $elm$core$Basics$never = function (_v0) {
	never:
	while (true) {
		var nvr = _v0;
		var $temp$_v0 = nvr;
		_v0 = $temp$_v0;
		continue never;
	}
};
var $elm$core$Task$Perform = $elm$core$Basics$identity;
var $elm$core$Task$succeed = _Scheduler_succeed;
var $elm$core$Task$init = $elm$core$Task$succeed(0);
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
var $elm$core$Task$andThen = _Scheduler_andThen;
var $elm$core$Task$map = F2(
	function (func, taskA) {
		return A2(
			$elm$core$Task$andThen,
			function (a) {
				return $elm$core$Task$succeed(
					func(a));
			},
			taskA);
	});
var $elm$core$Task$map2 = F3(
	function (func, taskA, taskB) {
		return A2(
			$elm$core$Task$andThen,
			function (a) {
				return A2(
					$elm$core$Task$andThen,
					function (b) {
						return $elm$core$Task$succeed(
							A2(func, a, b));
					},
					taskB);
			},
			taskA);
	});
var $elm$core$Task$sequence = function (tasks) {
	return A3(
		$elm$core$List$foldr,
		$elm$core$Task$map2($elm$core$List$cons),
		$elm$core$Task$succeed(_List_Nil),
		tasks);
};
var $elm$core$Platform$sendToApp = _Platform_sendToApp;
var $elm$core$Task$spawnCmd = F2(
	function (router, _v0) {
		var task = _v0;
		return _Scheduler_spawn(
			A2(
				$elm$core$Task$andThen,
				$elm$core$Platform$sendToApp(router),
				task));
	});
var $elm$core$Task$onEffects = F3(
	function (router, commands, state) {
		return A2(
			$elm$core$Task$map,
			function (_v0) {
				return 0;
			},
			$elm$core$Task$sequence(
				A2(
					$elm$core$List$map,
					$elm$core$Task$spawnCmd(router),
					commands)));
	});
var $elm$core$Task$onSelfMsg = F3(
	function (_v0, _v1, _v2) {
		return $elm$core$Task$succeed(0);
	});
var $elm$core$Task$cmdMap = F2(
	function (tagger, _v0) {
		var task = _v0;
		return A2($elm$core$Task$map, tagger, task);
	});
_Platform_effectManagers['Task'] = _Platform_createManager($elm$core$Task$init, $elm$core$Task$onEffects, $elm$core$Task$onSelfMsg, $elm$core$Task$cmdMap);
var $elm$core$Task$command = _Platform_leaf('Task');
var $elm$core$Task$perform = F2(
	function (toMessage, task) {
		return $elm$core$Task$command(
			A2($elm$core$Task$map, toMessage, task));
	});
var $elm$browser$Browser$element = _Browser_element;
var $author$project$OutputController$Model = $elm$core$Basics$identity;
var $author$project$SurfaceController$Model = $elm$core$Basics$identity;
var $author$project$ReconciliationTracking$empty = {aH: $elm$core$Maybe$Nothing, aW: _List_Nil, s: _List_Nil};
var $author$project$Launch$Idle = {$: 0};
var $author$project$Launch$Model = $elm$core$Basics$identity;
var $author$project$UInt64$Counter = $elm$core$Basics$identity;
var $author$project$UInt64$zero = '0';
var $author$project$Launch$init = {aG: $elm$core$Maybe$Nothing, G: $author$project$Launch$Idle, o: $author$project$UInt64$zero, dj: $author$project$UInt64$zero, bF: $elm$core$Maybe$Nothing};
var $author$project$Pins$initial = {d_: '', d4: $elm$core$Maybe$Nothing, bF: $elm$core$Maybe$Nothing};
var $author$project$Switcher$Idle = 0;
var $author$project$Switcher$Model = $elm$core$Basics$identity;
var $elm$core$Dict$RBEmpty_elm_builtin = {$: -2};
var $elm$core$Dict$empty = $elm$core$Dict$RBEmpty_elm_builtin;
var $author$project$Switcher$initial = {aB: $elm$core$Maybe$Nothing, bp: _List_Nil, dP: $author$project$UInt64$zero, bZ: $elm$core$Maybe$Nothing, G: 0, bc: false, b1: $elm$core$Maybe$Nothing, ct: _List_Nil, eb: 0, a1: $elm$core$Dict$empty};
var $author$project$MenuBridge$Model = $elm$core$Basics$identity;
var $author$project$ReceiptRouter$Model = $elm$core$Basics$identity;
var $author$project$ReceiptRouter$empty = _List_Nil;
var $author$project$Menu$Model = $elm$core$Basics$identity;
var $author$project$Menu$init = {Z: false, ao: _List_Nil, bw: $elm$core$Maybe$Nothing, aq: $elm$core$Maybe$Nothing, bA: 1, bB: 1, d3: _List_Nil, a0: _List_Nil, at: _List_Nil};
var $author$project$MenuBridge$initial = {aq: $author$project$Menu$init, u: $elm$core$Maybe$Nothing, cp: $author$project$UInt64$zero, a_: $elm$core$Maybe$Nothing, V: $author$project$ReceiptRouter$empty};
var $author$project$Shell$Detached = 0;
var $author$project$Effects$empty = {aD: false, dP: $author$project$UInt64$zero, aa: $elm$core$Maybe$Nothing, o: $author$project$UInt64$zero, z: $elm$core$Maybe$Nothing, l: _List_Nil};
var $author$project$Shell$initial = {Q: false, d: $elm$core$Maybe$Nothing, cH: false, R: $author$project$Effects$empty, n: $elm$core$Maybe$Nothing, ad: $elm$core$Maybe$Nothing, cQ: $elm$core$Maybe$Nothing, cR: $elm$core$Maybe$Nothing, dQ: $elm$core$Maybe$Nothing, C: _List_Nil, d_: 'Connecting…', _: false, G: 0, as: false, bD: false, aP: true, be: $elm$core$Maybe$Nothing, o: $author$project$UInt64$zero, H: false};
var $author$project$TaskbarShell$initial = {dP: $author$project$UInt64$zero, k: $author$project$MenuBridge$initial, J: $elm$core$Maybe$Nothing, b: $author$project$Shell$initial};
var $author$project$Desktop$initial = {
	ak: $elm$core$Maybe$Nothing,
	aS: $elm$core$Maybe$Nothing,
	j: $elm$core$Maybe$Nothing,
	E: '',
	n: $elm$core$Maybe$Nothing,
	p: $author$project$Launch$init,
	F: $elm$core$Maybe$Nothing,
	O: $elm$core$Maybe$Nothing,
	q: false,
	t: false,
	ag: $elm$core$Maybe$Nothing,
	a9: false,
	aM: $elm$core$Maybe$Nothing,
	y: $author$project$Pins$initial,
	aO: $elm$core$Maybe$Just($author$project$UInt64$zero),
	b$: '',
	o: $author$project$UInt64$zero,
	r: $elm$core$Maybe$Nothing,
	w: $elm$core$Maybe$Nothing,
	e: $author$project$Switcher$initial,
	ai: $elm$core$Maybe$Nothing,
	aj: $elm$core$Maybe$Nothing,
	bG: $elm$core$Maybe$Nothing,
	a: $author$project$TaskbarShell$initial
};
var $author$project$SurfaceController$initial = {c: $author$project$Desktop$initial, Z: false, aI: $author$project$UInt64$zero, bC: $author$project$UInt64$zero, P: $author$project$ReconciliationTracking$empty};
var $author$project$OutputController$initial = {ab: false, W: _List_Nil, ac: false, bT: $author$project$SurfaceController$initial, bW: $author$project$UInt64$zero, dj: $author$project$UInt64$zero, eb: $elm$core$Maybe$Nothing, av: _List_Nil};
var $elm$json$Json$Decode$value = _Json_decodeValue;
var $author$project$Main$nativeBatchDispositions = _Platform_incomingPort('nativeBatchDispositions', $elm$json$Json$Decode$value);
var $author$project$Main$nativeDismissals = _Platform_incomingPort('nativeDismissals', $elm$json$Json$Decode$value);
var $author$project$Main$nativeEvents = _Platform_incomingPort('nativeEvents', $elm$json$Json$Decode$value);
var $author$project$Main$nativeReflows = _Platform_incomingPort('nativeReflows', $elm$json$Json$Decode$value);
var $author$project$Main$nativeViews = _Platform_incomingPort('nativeViews', $elm$json$Json$Decode$value);
var $elm$core$Platform$Cmd$batch = _Platform_batch;
var $elm$core$Platform$Cmd$none = $elm$core$Platform$Cmd$batch(_List_Nil);
var $author$project$Main$rendererActions = _Platform_incomingPort('rendererActions', $elm$json$Json$Decode$value);
var $elm$virtual_dom$VirtualDom$text = _VirtualDom_text;
var $elm$html$Html$text = $elm$virtual_dom$VirtualDom$text;
var $author$project$OutputController$Dismiss = function (a) {
	return {$: 4, a: a};
};
var $author$project$OutputController$Disposition = function (a) {
	return {$: 0, a: a};
};
var $author$project$Desktop$Incoming = function (a) {
	return {$: 9, a: a};
};
var $author$project$OutputController$Interaction = function (a) {
	return {$: 3, a: a};
};
var $author$project$OutputController$Reflow = function (a) {
	return {$: 5, a: a};
};
var $author$project$OutputController$Renderer = function (a) {
	return {$: 2, a: a};
};
var $author$project$OutputController$Topology = function (a) {
	return {$: 1, a: a};
};
var $author$project$Desktop$ChoiceDeadline = function (a) {
	return {$: 27, a: a};
};
var $author$project$Desktop$Deadline = function (a) {
	return {$: 26, a: a};
};
var $author$project$Main$Deadline = function (a) {
	return {$: 6, a: a};
};
var $author$project$TaskbarShell$ExpirePrepared = function (a) {
	return {$: 6, a: a};
};
var $author$project$Desktop$Window = function (a) {
	return {$: 0, a: a};
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
var $elm$core$Process$sleep = _Process_sleep;
var $author$project$Main$surfaceCommits = _Platform_outgoingPort('surfaceCommits', $elm$core$Basics$identity);
var $elm$core$Maybe$withDefault = F2(
	function (_default, maybe) {
		if (!maybe.$) {
			var value = maybe.a;
			return value;
		} else {
			return _default;
		}
	});
var $author$project$Main$commit = F2(
	function (packet, effects) {
		var timers = A2(
			$elm$core$List$filterMap,
			function (effect) {
				_v0$3:
				while (true) {
					if (!effect.$) {
						switch (effect.a.$) {
							case 0:
								if (effect.a.a.$ === 2) {
									var token = effect.a.a.a;
									return $elm$core$Maybe$Just(
										A2(
											$elm$core$Task$perform,
											function (_v1) {
												return $author$project$Main$Deadline(
													$author$project$Desktop$Window(
														$author$project$TaskbarShell$ExpirePrepared(token)));
											},
											$elm$core$Process$sleep(2000)));
								} else {
									break _v0$3;
								}
							case 3:
								var token = effect.a.a;
								return $elm$core$Maybe$Just(
									A2(
										$elm$core$Task$perform,
										function (_v2) {
											return $author$project$Main$Deadline(
												$author$project$Desktop$ChoiceDeadline(token));
										},
										$elm$core$Process$sleep(2000)));
							case 2:
								var token = effect.a.a;
								return $elm$core$Maybe$Just(
									A2(
										$elm$core$Task$perform,
										function (_v3) {
											return $author$project$Main$Deadline(
												$author$project$Desktop$Deadline(token));
										},
										$elm$core$Process$sleep(10000)));
							default:
								break _v0$3;
						}
					} else {
						break _v0$3;
					}
				}
				return $elm$core$Maybe$Nothing;
			},
			effects);
		var atomic = A2(
			$elm$core$Maybe$withDefault,
			$elm$core$Platform$Cmd$none,
			A2($elm$core$Maybe$map, $author$project$Main$surfaceCommits, packet));
		return $elm$core$Platform$Cmd$batch(
			A2($elm$core$List$cons, atomic, timers));
	});
var $author$project$OutputController$controller = function (_v0) {
	var model = _v0;
	return model.bT;
};
var $author$project$Main$inspections = _Platform_outgoingPort('inspections', $elm$core$Basics$identity);
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
var $elm$json$Json$Encode$bool = _Json_wrap;
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
	var _v0 = _Utils_Tuple2(model.d, model.R.aa);
	if ((!_v0.a.$) && (!_v0.b.$)) {
		var binding = _v0.a.a;
		var observed = _v0.b.a;
		return A3($author$project$Binding$matchesContext, observed.A.dY, observed.A.dM, binding) ? $elm$core$Maybe$Just(
			A3($author$project$Shell$Stamp, binding, observed.A.m, observed.A.dj)) : $elm$core$Maybe$Nothing;
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $elm$core$Basics$composeR = F3(
	function (f, g, x) {
		return g(
			f(x));
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
var $author$project$MenuBridge$currentProvider = function (_v0) {
	var state = _v0;
	return A2(
		$elm$core$Maybe$map,
		function ($) {
			return $.bF;
		},
		state.a_);
};
var $elm$json$Json$Decode$decodeValue = _Json_run;
var $author$project$SurfaceController$desktop = function (_v0) {
	var model = _v0;
	return model.c;
};
var $elm$json$Json$Decode$field = _Json_decodeField;
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
var $author$project$Switcher$Forward = 0;
var $author$project$TaskbarShell$Native = function (a) {
	return {$: 0, a: a};
};
var $author$project$Desktop$OpenApplications = function (a) {
	return {$: 10, a: a};
};
var $author$project$Desktop$OpenOverview = function (a) {
	return {$: 11, a: a};
};
var $author$project$Desktop$OpenSwitcher = F2(
	function (a, b) {
		return {$: 12, a: a, b: b};
	});
var $author$project$TaskbarShell$Primary = F2(
	function (a, b) {
		return {$: 1, a: a, b: b};
	});
var $author$project$Shell$Reconnect = {$: 5};
var $author$project$Desktop$RetryWindows = {$: 28};
var $author$project$Desktop$Start = function (a) {
	return {$: 25, a: a};
};
var $author$project$Taskbar$Unavailable = {$: 3};
var $elm$core$Maybe$andThen = F2(
	function (callback, maybeValue) {
		if (!maybeValue.$) {
			var value = maybeValue.a;
			return callback(value);
		} else {
			return $elm$core$Maybe$Nothing;
		}
	});
var $author$project$Shell$Ready = 2;
var $elm$core$Basics$neq = _Utils_notEqual;
var $elm$core$Basics$not = _Basics_not;
var $author$project$Effects$Pending = 0;
var $author$project$Effects$pending = function (model) {
	return A2(
		$elm$core$Maybe$withDefault,
		false,
		A2(
			$elm$core$Maybe$map,
			function (transaction) {
				return !transaction.cx;
			},
			model.z));
};
var $author$project$Shell$available = function (model) {
	return (!model.bD) && ((!model.H) && ((model.G === 2) && ((!model.Q) && ((!$author$project$Effects$pending(model.R)) && (_Utils_eq(model.cQ, $elm$core$Maybe$Nothing) && ((!A2(
		$elm$core$Maybe$withDefault,
		false,
		A2(
			$elm$core$Maybe$map,
			function ($) {
				return $.R;
			},
			model.cR))) || (_Utils_eq(model.dQ, $elm$core$Maybe$Nothing) && (!_Utils_eq(model.ad, $elm$core$Maybe$Nothing)))))))));
};
var $author$project$Desktop$ViewStamp = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$Desktop$capture = function (model) {
	return A2(
		$elm$core$Maybe$map,
		$author$project$Desktop$ViewStamp(model.a.b.d),
		model.aO);
};
var $author$project$Effects$Unknown = 4;
var $author$project$UInt64$string = function (_v0) {
	var value = _v0;
	return value;
};
var $author$project$Binding$authorityIdentity = function (_v0) {
	var lifetime = _v0.a;
	return $author$project$UInt64$string(lifetime);
};
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
				return _Utils_eq(t.K.A.dY, lifetime) && (_Utils_eq(t.K.U, incarnation) && A2(
					$elm$core$List$member,
					t.cx,
					_List_fromArray(
						[0, 4])));
			},
			model.l);
	});
var $author$project$Menu$Window = function (a) {
	return {$: 0, a: a};
};
var $author$project$Menu$hasOutstandingFor = F2(
	function (window, _v0) {
		var state = _v0;
		return A2(
			$elm$core$List$any,
			function (entry) {
				var _v1 = entry.d;
				var value = _v1;
				return _Utils_eq(
					value.ed,
					$author$project$Menu$Window(window));
			},
			state.d3);
	});
var $elm$core$Basics$compare = _Utils_compare;
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
var $author$project$Menu$snapshot = function (_v0) {
	var state = _v0;
	return {
		Z: state.Z,
		cV: $elm$core$List$length(state.ao),
		bw: state.bw,
		aq: state.aq,
		d3: $elm$core$List$length(state.d3),
		a0: $elm$core$List$length(state.a0),
		di: $elm$core$List$length(state.at)
	};
};
var $author$project$Menu$WindowId = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$Menu$windowId = $author$project$Menu$WindowId;
var $author$project$ActionProjection$windows = function (_v0) {
	var rows = _v0.c;
	return rows;
};
var $author$project$MenuBridge$blockedFor = F3(
	function (incarnation, shell, _v0) {
		var state = _v0;
		var root = A2(
			$elm$core$Maybe$andThen,
			function (observed) {
				return A2($author$project$ActionProjection$rootOf, incarnation, observed.dk);
			},
			shell.R.aa);
		var nativeBlocked = function () {
			var _v2 = _Utils_Tuple3(shell.d, shell.R.aa, root);
			if (((!_v2.a.$) && (!_v2.b.$)) && (!_v2.c.$)) {
				var observed = _v2.b.a;
				var family = _v2.c.a;
				return A2(
					$elm$core$List$any,
					function (window) {
						return A3($author$project$Effects$blocked, observed.A.dY, window.U, shell.R);
					},
					A2(
						$elm$core$List$filter,
						function (window) {
							return _Utils_eq(
								A2($author$project$ActionProjection$rootOf, window.U, observed.dk),
								$elm$core$Maybe$Just(family));
						},
						$author$project$ActionProjection$windows(observed.dk)));
			} else {
				return A2(
					$elm$core$List$any,
					function (transaction) {
						return A2(
							$elm$core$List$member,
							transaction.cx,
							_List_fromArray(
								[0, 4]));
					},
					shell.R.l);
			}
		}();
		var blocked = function () {
			var _v1 = _Utils_Tuple2(shell.d, root);
			if ((!_v1.a.$) && (!_v1.b.$)) {
				var _native = _v1.a.a;
				var family = _v1.b.a;
				return A2(
					$author$project$Menu$hasOutstandingFor,
					A2(
						$author$project$Menu$windowId,
						$author$project$Binding$authorityIdentity(_native),
						$author$project$UInt64$string(family)),
					state.aq);
			} else {
				return $author$project$Menu$snapshot(state.aq).d3 > 0;
			}
		}();
		return blocked || nativeBlocked;
	});
var $author$project$Surface$familyBlocked = F2(
	function (model, incarnation) {
		return A3($author$project$MenuBridge$blockedFor, incarnation, model.a.b, model.a.k);
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
var $author$project$ActionProjection$focused = function (_v0) {
	var focus = _v0.b;
	return focus;
};
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
					return _Utils_eq(g.ap, key);
				},
				accumulated) ? A2(
				$elm$core$List$map,
				function (g) {
					return _Utils_eq(g.ap, key) ? _Utils_update(
						g,
						{
							am: _Utils_ap(
								g.am,
								_List_fromArray(
									[entry]))
						}) : g;
				},
				accumulated) : _Utils_ap(
				accumulated,
				_List_fromArray(
					[
						{
						am: _List_fromArray(
							[entry]),
						ap: key
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
					A2($author$project$ActionProjection$rootOf, w.U, projection),
					$elm$core$Maybe$Just(root.U));
			},
			rows);
		var key = $elm$core$String$isEmpty(root.b9) ? ('window:' + $author$project$UInt64$string(root.U)) : ('application:' + root.b9);
		return _Utils_Tuple2(
			key,
			{
				dC: _Utils_eq(
					activeRoot,
					$elm$core$Maybe$Just(root.U)),
				b9: root.b9,
				ca: A2(
					$elm$core$List$all,
					function ($) {
						return $.ca;
					},
					members),
				cZ: root.cZ,
				a7: root.a7,
				v: root.U
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
						return A2($author$project$UInt64$compare, a.U, b.U);
					}),
				A2(
					$elm$core$List$filter,
					function (w) {
						return _Utils_eq(w.co, $elm$core$Maybe$Nothing);
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
					return $.dk;
				},
				$author$project$Taskbar$groups),
			model.b.R.aa));
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
var $elm$core$List$isEmpty = function (xs) {
	if (!xs.b) {
		return true;
	} else {
		return false;
	}
};
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
var $elm$json$Json$Encode$string = _Json_wrap;
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
			A2($elm$core$Maybe$map, $author$project$Desktop$host, model.a.b.d)) + (':' + (A2(
			$elm$core$Maybe$withDefault,
			'exhausted',
			A2($elm$core$Maybe$map, $author$project$UInt64$string, model.aO)) + (':' + suffix))));
	});
var $author$project$Catalog$lookup = F2(
	function (value, _v0) {
		var values = _v0.c;
		return A2($elm$core$Dict$get, value, values);
	});
var $author$project$Desktop$pinGroups = F2(
	function (identity, model) {
		var _v0 = A2(
			$elm$core$Maybe$andThen,
			$author$project$Catalog$lookup(identity),
			model.ak);
		if (_v0.$ === 1) {
			return _List_Nil;
		} else {
			var entry = _v0.a;
			return A2(
				$elm$core$List$filter,
				function (group) {
					return A2(
						$elm$core$List$any,
						function (family) {
							return _Utils_eq(family.b9, identity) || ((!$elm$core$String$isEmpty(entry.eg)) && _Utils_eq(family.b9, entry.eg));
						},
						group.am);
				},
				$author$project$TaskbarShell$groups(model.a));
		}
	});
var $author$project$Desktop$pinIdentities = function (model) {
	return A2(
		$elm$core$Maybe$withDefault,
		_List_Nil,
		A2(
			$elm$core$Maybe$map,
			function ($) {
				return $.dU;
			},
			model.y.bF));
};
var $author$project$Desktop$pinnedGroup = F2(
	function (identity, model) {
		var _v0 = A2($author$project$Desktop$pinGroups, identity, model);
		if (_v0.b && (!_v0.b.b)) {
			var group = _v0.a;
			return $elm$core$Maybe$Just(group);
		} else {
			return $elm$core$Maybe$Nothing;
		}
	});
var $author$project$Effects$Activate = {$: 2};
var $author$project$Taskbar$Apply = F2(
	function (a, b) {
		return {$: 2, a: a, b: b};
	});
var $author$project$Taskbar$Launch = {$: 0};
var $author$project$Effects$Minimize = {$: 0};
var $author$project$Taskbar$Picker = {$: 1};
var $author$project$Effects$Restore = {$: 1};
var $author$project$Taskbar$primary = F2(
	function (pinned, families) {
		if (!families.b) {
			return pinned ? $author$project$Taskbar$Launch : $author$project$Taskbar$Unavailable;
		} else {
			if (!families.b.b) {
				var entry = families.a;
				return (!entry.ca) ? $author$project$Taskbar$Unavailable : (entry.a7 ? A2($author$project$Taskbar$Apply, $author$project$Effects$Restore, entry.v) : (entry.dC ? A2($author$project$Taskbar$Apply, $author$project$Effects$Minimize, entry.v) : A2($author$project$Taskbar$Apply, $author$project$Effects$Activate, entry.v)));
			} else {
				return $author$project$Taskbar$Picker;
			}
		}
	});
var $author$project$Shell$Exhausted = 3;
var $author$project$Shell$Refresh = {$: 4};
var $author$project$Surface$recoveryControl = F2(
	function (identity, model) {
		return {
			h: 'Refresh window status; read observations without retrying actions',
			f: 'Observation only',
			i: A2($author$project$Desktop$key, model, identity),
			dL: (!(!model.a.b.G)) && ((model.a.b.G !== 3) && (!$author$project$Effects$pending(model.a.b.R))),
			bu: identity,
			cZ: 'Refresh window status',
			g: $elm$core$Maybe$Just(
				$author$project$Desktop$Window(
					$author$project$TaskbarShell$Native($author$project$Shell$Refresh)))
		};
	});
var $author$project$Effects$Refused = 2;
var $author$project$MenuBridge$menuSnapshot = function (_v0) {
	var state = _v0;
	return $author$project$Menu$snapshot(state.aq);
};
var $author$project$Surface$recoveryNeeded = function (model) {
	return A2(
		$elm$core$List$any,
		function (transaction) {
			return A2(
				$elm$core$List$member,
				transaction.cx,
				_List_fromArray(
					[0, 4]));
		},
		model.a.b.R.l) || (A2(
		$elm$core$Maybe$withDefault,
		false,
		A2(
			$elm$core$Maybe$map,
			function (transaction) {
				return A2(
					$elm$core$List$member,
					transaction.cx,
					_List_fromArray(
						[2, 4]));
			},
			model.a.b.R.z)) || ($author$project$MenuBridge$menuSnapshot(model.a.k).d3 > 0));
};
var $author$project$Launch$Selection = F5(
	function (a, b, c, d, e) {
		return {$: 0, a: a, b: b, c: c, d: d, e: e};
	});
var $author$project$Launch$identityFunction = function (value) {
	return value;
};
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
	return {dP: generation, dY: lifetime};
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
								return A5($author$project$Launch$Selection, host, model.dj, scope.dY, scope.dP, entry.bX);
							},
							A2($author$project$Catalog$lookup, identity, snapshot));
					}),
				model.aG,
				model.bF));
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
	var switcher = {
		h: 'Open window switcher',
		f: '',
		i: A2($author$project$Desktop$key, model, 'control:switcher-opener'),
		dL: $author$project$Shell$available(model.a.b) && _Utils_eq(model.j, $elm$core$Maybe$Nothing),
		bu: 'bar:switcher',
		cZ: 'Switch windows',
		g: A2(
			$elm$core$Maybe$map,
			function (stamp) {
				return A2($author$project$Desktop$OpenSwitcher, stamp, 0);
			},
			$author$project$Desktop$capture(model))
	};
	var retry = {
		h: 'Refresh windows',
		f: '',
		i: A2($author$project$Desktop$key, model, 'refresh-windows'),
		dL: _Utils_eq(model.j, $elm$core$Maybe$Nothing),
		bu: 'bar:refresh-windows',
		cZ: 'Refresh windows',
		g: $elm$core$Maybe$Just($author$project$Desktop$RetryWindows)
	};
	var reconnect = {
		h: 'Reconnect to the window system',
		f: '',
		i: 'reconnect',
		dL: !model.a.b.aP,
		bu: 'bar:reconnect',
		cZ: 'Reconnect',
		g: $elm$core$Maybe$Just(
			$author$project$Desktop$Window(
				$author$project$TaskbarShell$Native($author$project$Shell$Reconnect)))
	};
	var pinIds = $author$project$Desktop$pinIdentities(model);
	var owners = function (group) {
		return A2(
			$elm$core$List$filter,
			function (identity) {
				return A2(
					$elm$core$Maybe$withDefault,
					false,
					A2(
						$elm$core$Maybe$map,
						function (matched) {
							return _Utils_eq(matched.ap, group.ap);
						},
						A2($author$project$Desktop$pinnedGroup, identity, model)));
			},
			pinIds);
	};
	var overview = {
		h: 'Open Task View',
		f: '',
		i: A2($author$project$Desktop$key, model, 'control:overview-opener'),
		dL: $author$project$Shell$available(model.a.b) && _Utils_eq(model.j, $elm$core$Maybe$Nothing),
		bu: 'bar:overview',
		cZ: 'Task View',
		g: A2(
			$elm$core$Maybe$map,
			$author$project$Desktop$OpenOverview,
			$author$project$Desktop$capture(model))
	};
	var ordinaryGroups = A2(
		$elm$core$List$filter,
		function (group) {
			return $elm$core$List$length(
				owners(group)) !== 1;
		},
		$author$project$TaskbarShell$groups(model.a));
	var groupControl = function (group) {
		var state = function () {
			var _v6 = group.am;
			if (_v6.b && (!_v6.b.b)) {
				var family = _v6.a;
				return family.a7 ? 'Minimized' : (family.dC ? 'Active' : 'Open');
			} else {
				return $elm$core$String$fromInt(
					$elm$core$List$length(group.am)) + ' windows';
			}
		}();
		var scoped = $author$project$Shell$capture(model.a.b);
		var operation = function () {
			var _v2 = A2($author$project$Taskbar$primary, false, group.am);
			_v2$4:
			while (true) {
				switch (_v2.$) {
					case 2:
						switch (_v2.a.$) {
							case 0:
								var _v3 = _v2.a;
								return 'Minimize ';
							case 1:
								var _v4 = _v2.a;
								return 'Restore ';
							case 2:
								var _v5 = _v2.a;
								return 'Activate ';
							default:
								break _v2$4;
						}
					case 1:
						return 'Choose a window from ';
					default:
						break _v2$4;
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
					return $.cZ;
				},
				$elm$core$List$head(group.am)));
		var blocked = function () {
			var _v1 = A2($author$project$Taskbar$primary, false, group.am);
			if (_v1.$ === 2) {
				var incarnation = _v1.b;
				return A2($author$project$Surface$familyBlocked, model, incarnation);
			} else {
				return false;
			}
		}();
		var ready = $author$project$Shell$available(model.a.b) && ((!_Utils_eq(
			A2($author$project$Taskbar$primary, false, group.am),
			$author$project$Taskbar$Unavailable)) && (!blocked));
		return {
			h: _Utils_ap(
				operation,
				_Utils_ap(
					label,
					blocked ? '; awaiting native confirmation' : '')),
			f: blocked ? 'Awaiting native confirmation' : state,
			i: A2(
				$elm$core$Maybe$withDefault,
				'detached-group',
				A2(
					$elm$core$Maybe$map,
					function (stamp) {
						return 'group:' + ($author$project$Shell$stampKey(stamp) + (':' + group.ap));
					},
					scoped)),
			dL: ready,
			bu: 'bar:group:' + group.ap,
			cZ: label,
			g: ready ? A2(
				$elm$core$Maybe$map,
				function (stamp) {
					return $author$project$Desktop$Window(
						A2($author$project$TaskbarShell$Primary, stamp, group.ap));
				},
				scoped) : $elm$core$Maybe$Nothing
		};
	};
	var pinControl = function (identity) {
		var entry = A2(
			$elm$core$Maybe$andThen,
			$author$project$Catalog$lookup(identity),
			model.ak);
		var label = A2(
			$elm$core$Maybe$withDefault,
			identity,
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.cl;
				},
				entry));
		var disabled = function (reason) {
			return {
				h: _Utils_ap(reason, label),
				f: reason,
				i: A2($author$project$Desktop$key, model, 'pin:' + identity),
				dL: false,
				bu: 'bar:pin:' + identity,
				cZ: label,
				g: $elm$core$Maybe$Nothing
			};
		};
		var choice = $author$project$Shell$available(model.a.b) ? A2(
			$elm$core$Maybe$map,
			$author$project$Desktop$Start,
			A2($author$project$Launch$select, identity, model.p)) : $elm$core$Maybe$Nothing;
		var _v0 = A2($author$project$Desktop$pinnedGroup, identity, model);
		if (!_v0.$) {
			var group = _v0.a;
			if ($elm$core$List$length(
				owners(group)) === 1) {
				var control = groupControl(group);
				return _Utils_update(
					control,
					{f: 'Pinned; ' + control.f, bu: 'bar:pin:' + identity, cZ: label});
			} else {
				return disabled('Ambiguous application identity: ');
			}
		} else {
			return _Utils_eq(entry, $elm$core$Maybe$Nothing) ? disabled('Unavailable application: ') : ((!$elm$core$List$isEmpty(
				A2($author$project$Desktop$pinGroups, identity, model))) ? disabled('Ambiguous application identity: ') : {
				h: 'Open ' + label,
				f: 'Pinned launcher',
				i: A2($author$project$Desktop$key, model, 'pin:' + identity),
				dL: !_Utils_eq(choice, $elm$core$Maybe$Nothing),
				bu: 'bar:pin:' + identity,
				cZ: label,
				g: choice
			});
		}
	};
	var application = {
		h: 'Open applications',
		f: '',
		i: A2($author$project$Desktop$key, model, 'control:opener'),
		dL: !(!model.a.b.G),
		bu: 'bar:applications',
		cZ: 'Applications',
		g: A2(
			$elm$core$Maybe$map,
			$author$project$Desktop$OpenApplications,
			$author$project$Desktop$capture(model))
	};
	return A2(
		$elm$core$List$cons,
		(!model.a.b.G) ? reconnect : application,
		A2(
			$elm$core$List$cons,
			overview,
			A2(
				$elm$core$List$cons,
				switcher,
				_Utils_ap(
					A2($elm$core$List$map, pinControl, pinIds),
					_Utils_ap(
						A2($elm$core$List$map, groupControl, ordinaryGroups),
						_Utils_ap(
							((!$elm$core$String$isEmpty(model.E)) && (!(!model.a.b.G))) ? _List_fromArray(
								[retry]) : _List_Nil,
							($author$project$Surface$recoveryNeeded(model) && (!(!model.a.b.G))) ? _List_fromArray(
								[
									A2($author$project$Surface$recoveryControl, 'bar:recovery-refresh', model)
								]) : _List_Nil))))));
};
var $author$project$Desktop$Acknowledge = function (a) {
	return {$: 29, a: a};
};
var $author$project$Menu$Activate = F3(
	function (a, b, c) {
		return {$: 3, a: a, b: b, c: c};
	});
var $author$project$Desktop$ApplySnap = function (a) {
	return {$: 4, a: a};
};
var $author$project$Switcher$Browsing = 2;
var $author$project$TaskbarShell$Choose = F3(
	function (a, b, c) {
		return {$: 2, a: a, b: b, c: c};
	});
var $author$project$TaskbarShell$Close = F2(
	function (a, b) {
		return {$: 3, a: a, b: b};
	});
var $author$project$Desktop$CloseApplications = function (a) {
	return {$: 20, a: a};
};
var $author$project$Desktop$CloseOverview = function (a) {
	return {$: 17, a: a};
};
var $author$project$Desktop$CloseSnap = function (a) {
	return {$: 5, a: a};
};
var $author$project$Desktop$CloseSwitcher = function (a) {
	return {$: 16, a: a};
};
var $author$project$Desktop$CommitSwitcher = function (a) {
	return {$: 15, a: a};
};
var $author$project$Menu$Dismiss = function (a) {
	return {$: 5, a: a};
};
var $author$project$TaskbarShell$MenuEvent = function (a) {
	return {$: 5, a: a};
};
var $author$project$Desktop$MovePin = F3(
	function (a, b, c) {
		return {$: 23, a: a, b: b, c: c};
	});
var $author$project$Desktop$OpenSnap = F2(
	function (a, b) {
		return {$: 2, a: a, b: b};
	});
var $author$project$Desktop$OverviewChoose = F2(
	function (a, b) {
		return {$: 19, a: a, b: b};
	});
var $author$project$Desktop$OverviewWorkspace = F2(
	function (a, b) {
		return {$: 18, a: a, b: b};
	});
var $author$project$Menu$Ready = {$: 0};
var $author$project$Switcher$Reverse = 1;
var $author$project$Desktop$SearchQuery = F2(
	function (a, b) {
		return {$: 21, a: a, b: b};
	});
var $author$project$Desktop$SelectSnap = F2(
	function (a, b) {
		return {$: 3, a: a, b: b};
	});
var $author$project$Desktop$SwitcherChoose = F2(
	function (a, b) {
		return {$: 14, a: a, b: b};
	});
var $author$project$Desktop$SwitcherStep = F2(
	function (a, b) {
		return {$: 13, a: a, b: b};
	});
var $author$project$Desktop$TogglePin = F2(
	function (a, b) {
		return {$: 22, a: a, b: b};
	});
var $author$project$Switcher$entries = function (_v0) {
	var model = _v0;
	return model.bp;
};
var $author$project$GeometryProjection$window = F2(
	function (incarnation, snapshot) {
		return $elm$core$List$head(
			A2(
				$elm$core$List$filter,
				function (row) {
					return _Utils_eq(row.U, incarnation);
				},
				snapshot.a));
	});
var $author$project$TaskView$groups = function (shell) {
	var _v0 = _Utils_Tuple2(shell.R.aa, shell.ad);
	if ((!_v0.a.$) && (!_v0.b.$)) {
		var observed = _v0.a.a;
		var geometry = _v0.b.a;
		var rows = $author$project$ActionProjection$windows(observed.dk);
		var positive = function (workspace) {
			return (!$elm$core$String$isEmpty(workspace)) && ((!A2($elm$core$String$startsWith, '-', workspace)) && (workspace !== '0'));
		};
		var matching = function (row) {
			return A2(
				$elm$core$Maybe$withDefault,
				false,
				A2(
					$elm$core$Maybe$map,
					function (g) {
						return _Utils_eq(g.co, row.co) && _Utils_eq(g.a7, row.a7);
					},
					A2($author$project$GeometryProjection$window, row.U, geometry)));
		};
		var sameAuthority = _Utils_eq(
			shell.d,
			$elm$core$Maybe$Just(geometry.d)) && (_Utils_eq(observed.A.dY, geometry.A.dY) && (_Utils_eq(observed.A.dM, geometry.A.dM) && (_Utils_eq(observed.A.m, geometry.A.m) && (_Utils_eq(
			$author$project$ActionProjection$focused(observed.dk),
			geometry.br) && (_Utils_eq(
			$elm$core$List$length(rows),
			$elm$core$List$length(geometry.a)) && A2($elm$core$List$all, matching, rows))))));
		var focusedWorkspace = A2(
			$elm$core$Maybe$andThen,
			function ($) {
				return $.bk;
			},
			A2(
				$elm$core$Maybe$andThen,
				function (identity) {
					return A2($author$project$GeometryProjection$window, identity, geometry);
				},
				$author$project$ActionProjection$focused(observed.dk)));
		var families = A2(
			$elm$core$List$concatMap,
			function ($) {
				return $.am;
			},
			$author$project$Taskbar$groups(observed.dk));
		var add = F2(
			function (family, accumulated) {
				var _v1 = A2(
					$elm$core$Maybe$andThen,
					function ($) {
						return $.bk;
					},
					A2($author$project$GeometryProjection$window, family.v, geometry));
				if (!_v1.$) {
					var workspace = _v1.a;
					return (!positive(workspace)) ? accumulated : (A2(
						$elm$core$List$any,
						function (g) {
							return _Utils_eq(g.bX, workspace);
						},
						accumulated) ? A2(
						$elm$core$List$map,
						function (g) {
							return _Utils_eq(g.bX, workspace) ? _Utils_update(
								g,
								{
									a: _Utils_ap(
										g.a,
										_List_fromArray(
											[family]))
								}) : g;
						},
						accumulated) : _Utils_ap(
						accumulated,
						_List_fromArray(
							[
								{
								dC: _Utils_eq(
									focusedWorkspace,
									$elm$core$Maybe$Just(workspace)),
								bX: workspace,
								a: _List_fromArray(
									[family])
							}
							])));
				} else {
					return accumulated;
				}
			});
		return (!sameAuthority) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(
			A2(
				$elm$core$List$sortWith,
				F2(
					function (a, b) {
						return A2(
							$elm$core$Basics$compare,
							_Utils_Tuple2(
								$elm$core$String$length(a.bX),
								a.bX),
							_Utils_Tuple2(
								$elm$core$String$length(b.bX),
								b.bX));
					}),
				A3($elm$core$List$foldl, add, _List_Nil, families)));
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$Catalog$id = function (_v0) {
	var value = _v0;
	return value;
};
var $author$project$Snap$identity = function (region) {
	switch (region) {
		case 0:
			return 'left-half';
		case 1:
			return 'right-half';
		case 2:
			return 'top-left';
		case 3:
			return 'top-right';
		case 4:
			return 'bottom-left';
		default:
			return 'bottom-right';
	}
};
var $author$project$Provider$incarnation = function (_v0) {
	var value = _v0;
	return value.U;
};
var $author$project$Surface$menuBlocked = function (model) {
	return A2(
		$elm$core$Maybe$withDefault,
		false,
		A2(
			$elm$core$Maybe$map,
			A2(
				$elm$core$Basics$composeR,
				$author$project$Provider$incarnation,
				$author$project$Surface$familyBlocked(model)),
			$author$project$MenuBridge$currentProvider(model.a.k)));
};
var $author$project$Menu$menuNumber = function (_v0) {
	var number = _v0;
	return number;
};
var $author$project$Snap$name = function (region) {
	switch (region) {
		case 0:
			return 'Left half';
		case 1:
			return 'Right half';
		case 2:
			return 'Top left quarter';
		case 3:
			return 'Top right quarter';
		case 4:
			return 'Bottom left quarter';
		default:
			return 'Bottom right quarter';
	}
};
var $elm$core$Basics$negate = function (n) {
	return -n;
};
var $author$project$Snap$LeftHalf = 0;
var $author$project$GeometryProjection$Ordinary = 0;
var $author$project$Snap$proposal = function (choice) {
	return A2(
		$elm$core$Maybe$andThen,
		function (window) {
			var _v0 = _Utils_Tuple2(
				_Utils_Tuple2(window.bj, window.bz),
				_Utils_Tuple3(window.aL, window.bM, window.bl));
			if ((((((((((!_v0.a.a.$) && _v0.a.a.a.b) && _v0.a.a.a.b.b) && _v0.a.a.a.b.b.b) && _v0.a.a.a.b.b.b.b) && (!_v0.a.a.a.b.b.b.b.b)) && (!_v0.a.b.$)) && (!_v0.b.a.$)) && (!_v0.b.b.$)) && (!_v0.b.c.$)) {
				var _v1 = _v0.a;
				var _v2 = _v1.a.a;
				var x = _v2.a;
				var _v3 = _v2.b;
				var y = _v3.a;
				var _v4 = _v3.b;
				var width = _v4.a;
				var _v5 = _v4.b;
				var height = _v5.a;
				var monitor = _v1.b.a;
				var _v6 = _v0.b;
				var output = _v6.a.a;
				var area = _v6.b.a;
				var workspace = _v6.c.a;
				var quarter = height / 2;
				var half = width / 2;
				var geometry = function () {
					var _v7 = choice.eb;
					switch (_v7) {
						case 0:
							return _List_fromArray(
								[x, y, half, height]);
						case 1:
							return _List_fromArray(
								[x + half, y, width - half, height]);
						case 2:
							return _List_fromArray(
								[x, y, half, quarter]);
						case 3:
							return _List_fromArray(
								[x + half, y, width - half, quarter]);
						case 4:
							return _List_fromArray(
								[x, y + quarter, half, height - quarter]);
						default:
							return _List_fromArray(
								[x + half, y + quarter, width - half, height - quarter]);
					}
				}();
				return $elm$core$Maybe$Just(
					{
						A: choice.bF.A,
						ad: geometry,
						bz: monitor,
						aL: output,
						bE: $author$project$Snap$identity(choice.eb),
						bM: area,
						bl: workspace
					});
			} else {
				return $elm$core$Maybe$Nothing;
			}
		},
		A2($author$project$GeometryProjection$window, choice.ed, choice.bF));
};
var $author$project$Snap$open = F2(
	function (snapshot, target) {
		return A2(
			$elm$core$Maybe$andThen,
			function (window) {
				var choice = {eb: 0, bF: snapshot, ed: target};
				return (snapshot.dE || ((!window.dK) || (window.a7 || ((!(!window.c3)) || ((!(!window.ce)) || _Utils_eq(
					$author$project$Snap$proposal(choice),
					$elm$core$Maybe$Nothing)))))) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(choice);
			},
			A2($author$project$GeometryProjection$window, target, snapshot));
	});
var $author$project$Switcher$phase = function (_v0) {
	var model = _v0;
	return model.G;
};
var $author$project$Surface$recoveryPopup = function (model) {
	return $author$project$Surface$recoveryNeeded(model) ? _List_fromArray(
		[
			A2($author$project$Surface$recoveryControl, 'control:recovery-refresh', model)
		]) : _List_Nil;
};
var $author$project$Snap$BottomLeft = 4;
var $author$project$Snap$BottomRight = 5;
var $author$project$Snap$RightHalf = 1;
var $author$project$Snap$TopLeft = 2;
var $author$project$Snap$TopRight = 3;
var $author$project$Snap$regions = _List_fromArray(
	[0, 1, 2, 3, 4, 5]);
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
var $elm$core$String$concat = function (strings) {
	return A2($elm$core$String$join, '', strings);
};
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
var $author$project$SearchFold$exceptions = $elm$core$Dict$fromList(
	_List_fromArray(
		[
			_Utils_Tuple2('µ', 'μ'),
			_Utils_Tuple2('ß', 'ss'),
			_Utils_Tuple2('ŉ', 'ʼn'),
			_Utils_Tuple2('ſ', 's'),
			_Utils_Tuple2('ǰ', 'ǰ'),
			_Utils_Tuple2('ͅ', 'ι'),
			_Utils_Tuple2('ΐ', 'ΐ'),
			_Utils_Tuple2('ΰ', 'ΰ'),
			_Utils_Tuple2('ς', 'σ'),
			_Utils_Tuple2('ϐ', 'β'),
			_Utils_Tuple2('ϑ', 'θ'),
			_Utils_Tuple2('ϕ', 'φ'),
			_Utils_Tuple2('ϖ', 'π'),
			_Utils_Tuple2('ϰ', 'κ'),
			_Utils_Tuple2('ϱ', 'ρ'),
			_Utils_Tuple2('ϵ', 'ε'),
			_Utils_Tuple2('և', 'եւ'),
			_Utils_Tuple2('ᏸ', 'Ᏸ'),
			_Utils_Tuple2('ᏹ', 'Ᏹ'),
			_Utils_Tuple2('ᏺ', 'Ᏺ'),
			_Utils_Tuple2('ᏻ', 'Ᏻ'),
			_Utils_Tuple2('ᏼ', 'Ᏼ'),
			_Utils_Tuple2('ᏽ', 'Ᏽ'),
			_Utils_Tuple2('ᲀ', 'в'),
			_Utils_Tuple2('ᲁ', 'д'),
			_Utils_Tuple2('ᲂ', 'о'),
			_Utils_Tuple2('ᲃ', 'с'),
			_Utils_Tuple2('ᲄ', 'т'),
			_Utils_Tuple2('ᲅ', 'т'),
			_Utils_Tuple2('ᲆ', 'ъ'),
			_Utils_Tuple2('ᲇ', 'ѣ'),
			_Utils_Tuple2('ᲈ', 'ꙋ'),
			_Utils_Tuple2('ẖ', 'ẖ'),
			_Utils_Tuple2('ẗ', 'ẗ'),
			_Utils_Tuple2('ẘ', 'ẘ'),
			_Utils_Tuple2('ẙ', 'ẙ'),
			_Utils_Tuple2('ẚ', 'aʾ'),
			_Utils_Tuple2('ẛ', 'ṡ'),
			_Utils_Tuple2('ὐ', 'ὐ'),
			_Utils_Tuple2('ὒ', 'ὒ'),
			_Utils_Tuple2('ὔ', 'ὔ'),
			_Utils_Tuple2('ὖ', 'ὖ'),
			_Utils_Tuple2('ᾀ', 'ἀι'),
			_Utils_Tuple2('ᾁ', 'ἁι'),
			_Utils_Tuple2('ᾂ', 'ἂι'),
			_Utils_Tuple2('ᾃ', 'ἃι'),
			_Utils_Tuple2('ᾄ', 'ἄι'),
			_Utils_Tuple2('ᾅ', 'ἅι'),
			_Utils_Tuple2('ᾆ', 'ἆι'),
			_Utils_Tuple2('ᾇ', 'ἇι'),
			_Utils_Tuple2('ᾐ', 'ἠι'),
			_Utils_Tuple2('ᾑ', 'ἡι'),
			_Utils_Tuple2('ᾒ', 'ἢι'),
			_Utils_Tuple2('ᾓ', 'ἣι'),
			_Utils_Tuple2('ᾔ', 'ἤι'),
			_Utils_Tuple2('ᾕ', 'ἥι'),
			_Utils_Tuple2('ᾖ', 'ἦι'),
			_Utils_Tuple2('ᾗ', 'ἧι'),
			_Utils_Tuple2('ᾠ', 'ὠι'),
			_Utils_Tuple2('ᾡ', 'ὡι'),
			_Utils_Tuple2('ᾢ', 'ὢι'),
			_Utils_Tuple2('ᾣ', 'ὣι'),
			_Utils_Tuple2('ᾤ', 'ὤι'),
			_Utils_Tuple2('ᾥ', 'ὥι'),
			_Utils_Tuple2('ᾦ', 'ὦι'),
			_Utils_Tuple2('ᾧ', 'ὧι'),
			_Utils_Tuple2('ᾲ', 'ὰι'),
			_Utils_Tuple2('ᾳ', 'αι'),
			_Utils_Tuple2('ᾴ', 'άι'),
			_Utils_Tuple2('ᾶ', 'ᾶ'),
			_Utils_Tuple2('ᾷ', 'ᾶι'),
			_Utils_Tuple2('ι', 'ι'),
			_Utils_Tuple2('ῂ', 'ὴι'),
			_Utils_Tuple2('ῃ', 'ηι'),
			_Utils_Tuple2('ῄ', 'ήι'),
			_Utils_Tuple2('ῆ', 'ῆ'),
			_Utils_Tuple2('ῇ', 'ῆι'),
			_Utils_Tuple2('ῒ', 'ῒ'),
			_Utils_Tuple2('ΐ', 'ΐ'),
			_Utils_Tuple2('ῖ', 'ῖ'),
			_Utils_Tuple2('ῗ', 'ῗ'),
			_Utils_Tuple2('ῢ', 'ῢ'),
			_Utils_Tuple2('ΰ', 'ΰ'),
			_Utils_Tuple2('ῤ', 'ῤ'),
			_Utils_Tuple2('ῦ', 'ῦ'),
			_Utils_Tuple2('ῧ', 'ῧ'),
			_Utils_Tuple2('ῲ', 'ὼι'),
			_Utils_Tuple2('ῳ', 'ωι'),
			_Utils_Tuple2('ῴ', 'ώι'),
			_Utils_Tuple2('ῶ', 'ῶ'),
			_Utils_Tuple2('ῷ', 'ῶι'),
			_Utils_Tuple2('ꭰ', 'Ꭰ'),
			_Utils_Tuple2('ꭱ', 'Ꭱ'),
			_Utils_Tuple2('ꭲ', 'Ꭲ'),
			_Utils_Tuple2('ꭳ', 'Ꭳ'),
			_Utils_Tuple2('ꭴ', 'Ꭴ'),
			_Utils_Tuple2('ꭵ', 'Ꭵ'),
			_Utils_Tuple2('ꭶ', 'Ꭶ'),
			_Utils_Tuple2('ꭷ', 'Ꭷ'),
			_Utils_Tuple2('ꭸ', 'Ꭸ'),
			_Utils_Tuple2('ꭹ', 'Ꭹ'),
			_Utils_Tuple2('ꭺ', 'Ꭺ'),
			_Utils_Tuple2('ꭻ', 'Ꭻ'),
			_Utils_Tuple2('ꭼ', 'Ꭼ'),
			_Utils_Tuple2('ꭽ', 'Ꭽ'),
			_Utils_Tuple2('ꭾ', 'Ꭾ'),
			_Utils_Tuple2('ꭿ', 'Ꭿ'),
			_Utils_Tuple2('ꮀ', 'Ꮀ'),
			_Utils_Tuple2('ꮁ', 'Ꮁ'),
			_Utils_Tuple2('ꮂ', 'Ꮂ'),
			_Utils_Tuple2('ꮃ', 'Ꮃ'),
			_Utils_Tuple2('ꮄ', 'Ꮄ'),
			_Utils_Tuple2('ꮅ', 'Ꮅ'),
			_Utils_Tuple2('ꮆ', 'Ꮆ'),
			_Utils_Tuple2('ꮇ', 'Ꮇ'),
			_Utils_Tuple2('ꮈ', 'Ꮈ'),
			_Utils_Tuple2('ꮉ', 'Ꮉ'),
			_Utils_Tuple2('ꮊ', 'Ꮊ'),
			_Utils_Tuple2('ꮋ', 'Ꮋ'),
			_Utils_Tuple2('ꮌ', 'Ꮌ'),
			_Utils_Tuple2('ꮍ', 'Ꮍ'),
			_Utils_Tuple2('ꮎ', 'Ꮎ'),
			_Utils_Tuple2('ꮏ', 'Ꮏ'),
			_Utils_Tuple2('ꮐ', 'Ꮐ'),
			_Utils_Tuple2('ꮑ', 'Ꮑ'),
			_Utils_Tuple2('ꮒ', 'Ꮒ'),
			_Utils_Tuple2('ꮓ', 'Ꮓ'),
			_Utils_Tuple2('ꮔ', 'Ꮔ'),
			_Utils_Tuple2('ꮕ', 'Ꮕ'),
			_Utils_Tuple2('ꮖ', 'Ꮖ'),
			_Utils_Tuple2('ꮗ', 'Ꮗ'),
			_Utils_Tuple2('ꮘ', 'Ꮘ'),
			_Utils_Tuple2('ꮙ', 'Ꮙ'),
			_Utils_Tuple2('ꮚ', 'Ꮚ'),
			_Utils_Tuple2('ꮛ', 'Ꮛ'),
			_Utils_Tuple2('ꮜ', 'Ꮜ'),
			_Utils_Tuple2('ꮝ', 'Ꮝ'),
			_Utils_Tuple2('ꮞ', 'Ꮞ'),
			_Utils_Tuple2('ꮟ', 'Ꮟ'),
			_Utils_Tuple2('ꮠ', 'Ꮠ'),
			_Utils_Tuple2('ꮡ', 'Ꮡ'),
			_Utils_Tuple2('ꮢ', 'Ꮢ'),
			_Utils_Tuple2('ꮣ', 'Ꮣ'),
			_Utils_Tuple2('ꮤ', 'Ꮤ'),
			_Utils_Tuple2('ꮥ', 'Ꮥ'),
			_Utils_Tuple2('ꮦ', 'Ꮦ'),
			_Utils_Tuple2('ꮧ', 'Ꮧ'),
			_Utils_Tuple2('ꮨ', 'Ꮨ'),
			_Utils_Tuple2('ꮩ', 'Ꮩ'),
			_Utils_Tuple2('ꮪ', 'Ꮪ'),
			_Utils_Tuple2('ꮫ', 'Ꮫ'),
			_Utils_Tuple2('ꮬ', 'Ꮬ'),
			_Utils_Tuple2('ꮭ', 'Ꮭ'),
			_Utils_Tuple2('ꮮ', 'Ꮮ'),
			_Utils_Tuple2('ꮯ', 'Ꮯ'),
			_Utils_Tuple2('ꮰ', 'Ꮰ'),
			_Utils_Tuple2('ꮱ', 'Ꮱ'),
			_Utils_Tuple2('ꮲ', 'Ꮲ'),
			_Utils_Tuple2('ꮳ', 'Ꮳ'),
			_Utils_Tuple2('ꮴ', 'Ꮴ'),
			_Utils_Tuple2('ꮵ', 'Ꮵ'),
			_Utils_Tuple2('ꮶ', 'Ꮶ'),
			_Utils_Tuple2('ꮷ', 'Ꮷ'),
			_Utils_Tuple2('ꮸ', 'Ꮸ'),
			_Utils_Tuple2('ꮹ', 'Ꮹ'),
			_Utils_Tuple2('ꮺ', 'Ꮺ'),
			_Utils_Tuple2('ꮻ', 'Ꮻ'),
			_Utils_Tuple2('ꮼ', 'Ꮼ'),
			_Utils_Tuple2('ꮽ', 'Ꮽ'),
			_Utils_Tuple2('ꮾ', 'Ꮾ'),
			_Utils_Tuple2('ꮿ', 'Ꮿ'),
			_Utils_Tuple2('ﬀ', 'ff'),
			_Utils_Tuple2('ﬁ', 'fi'),
			_Utils_Tuple2('ﬂ', 'fl'),
			_Utils_Tuple2('ﬃ', 'ffi'),
			_Utils_Tuple2('ﬄ', 'ffl'),
			_Utils_Tuple2('ﬅ', 'st'),
			_Utils_Tuple2('ﬆ', 'st'),
			_Utils_Tuple2('ﬓ', 'մն'),
			_Utils_Tuple2('ﬔ', 'մե'),
			_Utils_Tuple2('ﬕ', 'մի'),
			_Utils_Tuple2('ﬖ', 'վն'),
			_Utils_Tuple2('ﬗ', 'մխ')
		]));
var $elm$core$String$cons = _String_cons;
var $elm$core$String$fromChar = function (_char) {
	return A2($elm$core$String$cons, _char, '');
};
var $elm$core$String$foldr = _String_foldr;
var $elm$core$String$toList = function (string) {
	return A3($elm$core$String$foldr, $elm$core$List$cons, _List_Nil, string);
};
var $elm$core$String$toLower = _String_toLower;
var $author$project$SearchFold$fold = function (value) {
	return $elm$core$String$concat(
		A2(
			$elm$core$List$map,
			function (c) {
				return A2(
					$elm$core$Maybe$withDefault,
					$elm$core$String$fromChar(c),
					A2(
						$elm$core$Dict$get,
						$elm$core$String$fromChar(c),
						$author$project$SearchFold$exceptions));
			},
			$elm$core$String$toList(
				$elm$core$String$toLower(value))));
};
var $elm$core$Tuple$second = function (_v0) {
	var y = _v0.b;
	return y;
};
var $elm$core$String$trim = _String_trim;
var $elm$core$String$words = _String_words;
var $author$project$Catalog$search = F2(
	function (raw, snapshot) {
		var query = $author$project$SearchFold$fold(
			$elm$core$String$trim(raw));
		var words = $elm$core$String$words(query);
		var rank = function (entry) {
			var tokens = A2(
				$elm$core$List$concatMap,
				A2($elm$core$Basics$composeR, $author$project$SearchFold$fold, $elm$core$String$words),
				A2(
					$elm$core$List$cons,
					entry.cl,
					A2($elm$core$List$cons, entry.cP, entry.cW)));
			var name = $author$project$SearchFold$fold(entry.cl);
			return $elm$core$String$isEmpty(query) ? $elm$core$Maybe$Just(0) : (_Utils_eq(name, query) ? $elm$core$Maybe$Just(0) : (A2($elm$core$String$startsWith, query, name) ? $elm$core$Maybe$Just(1) : (A2(
				$elm$core$List$all,
				function (word) {
					return A2(
						$elm$core$List$any,
						$elm$core$String$startsWith(word),
						tokens);
				},
				words) ? $elm$core$Maybe$Just(2) : $elm$core$Maybe$Nothing)));
		};
		var compare = F2(
			function (_v1, _v2) {
				var aRank = _v1.a;
				var a = _v1.b;
				var bRank = _v2.a;
				var b = _v2.b;
				var _v0 = A2($elm$core$Basics$compare, aRank, bRank);
				if (_v0 === 1) {
					return A2(
						$elm$core$Basics$compare,
						$author$project$Catalog$id(a.bX),
						$author$project$Catalog$id(b.bX));
				} else {
					var order = _v0;
					return order;
				}
			});
		return A2(
			$elm$core$List$map,
			$elm$core$Tuple$second,
			A2(
				$elm$core$List$sortWith,
				compare,
				A2(
					$elm$core$List$filterMap,
					function (entry) {
						return A2(
							$elm$core$Maybe$map,
							function (value) {
								return _Utils_Tuple2(value, entry);
							},
							rank(entry));
					},
					$author$project$Catalog$entries(snapshot))));
	});
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
var $author$project$Switcher$selected = function (_v0) {
	var model = _v0;
	return $elm$core$List$head(
		A2($elm$core$List$drop, model.eb, model.bp));
};
var $elm$core$List$singleton = function (value) {
	return _List_fromArray(
		[value]);
};
var $author$project$Launch$status = function (_v0) {
	var model = _v0;
	var _v1 = model.G;
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
var $author$project$Switcher$Waiting = 1;
var $author$project$Desktop$switcherOpen = function (model) {
	return A2(
		$elm$core$List$member,
		$author$project$Switcher$phase(model.e),
		_List_fromArray(
			[1, 2]));
};
var $author$project$Launch$Acknowledgement = $elm$core$Basics$identity;
var $author$project$Launch$uncertain = function (_v0) {
	var model = _v0;
	var _v1 = model.G;
	if ((_v1.$ === 2) && (_v1.b === 2)) {
		var intent = _v1.a;
		var _v2 = _v1.b;
		return $elm$core$Maybe$Just(intent);
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$Pins$writable = function (model) {
	return (!_Utils_eq(model.bF, $elm$core$Maybe$Nothing)) && _Utils_eq(model.d4, $elm$core$Maybe$Nothing);
};
var $author$project$Surface$controls = function (model) {
	if (!_Utils_eq(model.w, $elm$core$Maybe$Nothing)) {
		var _v0 = model.w;
		if (_v0.$ === 1) {
			return _List_Nil;
		} else {
			var choice = _v0.a;
			var scoped = function (message) {
				return A2(
					$elm$core$Maybe$map,
					message,
					$author$project$Desktop$capture(model));
			};
			var ready = $author$project$Shell$available(model.a.b);
			var regionControl = function (region) {
				var selected = _Utils_eq(region, choice.eb);
				var identity = 'snap:region:' + $author$project$Snap$identity(region);
				return {
					h: _Utils_ap(
						$author$project$Snap$name(region),
						selected ? '; selected preview' : ''),
					f: selected ? 'Selected' : '',
					i: A2($author$project$Desktop$key, model, identity),
					dL: ready,
					bu: identity,
					cZ: $author$project$Snap$name(region),
					g: ready ? scoped(
						function (stamp) {
							return A2($author$project$Desktop$SelectSnap, stamp, region);
						}) : $elm$core$Maybe$Nothing
				};
			};
			var placement = $author$project$Snap$proposal(choice);
			var applyReady = ready && (_Utils_eq(model.j, $elm$core$Maybe$Nothing) && (A2(
				$elm$core$Maybe$withDefault,
				false,
				A2(
					$elm$core$Maybe$map,
					function (caps) {
						return A2($elm$core$List$member, 'snap', caps.d1);
					},
					model.a.b.cR)) && (!_Utils_eq(placement, $elm$core$Maybe$Nothing))));
			var applyLabel = applyReady ? ('Snap to ' + $elm$core$String$toLower(
				$author$project$Snap$name(choice.eb))) : 'Snapping unavailable';
			return A2(
				$elm$core$List$cons,
				{
					h: 'Close snapping',
					f: '',
					i: A2($author$project$Desktop$key, model, 'snap:close'),
					dL: true,
					bu: 'control:close',
					cZ: 'Close',
					g: scoped($author$project$Desktop$CloseSnap)
				},
				_Utils_ap(
					A2($elm$core$List$map, regionControl, $author$project$Snap$regions),
					_List_fromArray(
						[
							{
							h: applyLabel,
							f: '',
							i: A2($author$project$Desktop$key, model, 'snap:apply'),
							dL: applyReady,
							bu: 'snap:apply',
							cZ: applyLabel,
							g: applyReady ? scoped($author$project$Desktop$ApplySnap) : $elm$core$Maybe$Nothing
						}
						])));
		}
	} else {
		if ($author$project$Desktop$switcherOpen(model)) {
			var selected = A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.v;
				},
				$author$project$Switcher$selected(model.e));
			var scoped = function (message) {
				return A2(
					$elm$core$Maybe$map,
					message,
					$author$project$Desktop$capture(model));
			};
			var control = F4(
				function (identity, label, enabled, message) {
					return {
						h: label,
						f: '',
						i: A2($author$project$Desktop$key, model, identity),
						dL: enabled,
						bu: identity,
						cZ: label,
						g: enabled ? scoped(message) : $elm$core$Maybe$Nothing
					};
				});
			var browsing = $author$project$Switcher$phase(model.e) === 2;
			var row = function (family) {
				var ready = browsing && (family.ca && (!A2($author$project$Surface$familyBlocked, model, family.v)));
				var identity = 'switcher:family:' + $author$project$UInt64$string(family.v);
				var detail = _Utils_eq(
					selected,
					$elm$core$Maybe$Just(family.v)) ? 'Selected' : (family.a7 ? 'Minimized' : 'Open');
				return {
					h: _Utils_ap(
						family.a7 ? 'Restore ' : 'Activate ',
						_Utils_ap(
							family.cZ,
							_Utils_eq(
								selected,
								$elm$core$Maybe$Just(family.v)) ? '; selected' : '')),
					f: detail,
					i: A2($author$project$Desktop$key, model, identity),
					dL: ready,
					bu: identity,
					cZ: family.cZ,
					g: ready ? scoped(
						function (stamp) {
							return A2($author$project$Desktop$SwitcherChoose, stamp, family.v);
						}) : $elm$core$Maybe$Nothing
				};
			};
			return _Utils_ap(
				_List_fromArray(
					[
						A4(control, 'control:close', 'Cancel window switcher', true, $author$project$Desktop$CloseSwitcher),
						A4(
						control,
						'control:reverse',
						'Previous window',
						true,
						function (stamp) {
							return A2($author$project$Desktop$SwitcherStep, stamp, 1);
						}),
						A4(
						control,
						'control:forward',
						'Next window',
						true,
						function (stamp) {
							return A2($author$project$Desktop$SwitcherStep, stamp, 0);
						}),
						A4(
						control,
						'control:commit',
						'Activate selected window',
						browsing && A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								A2(
									$elm$core$Basics$composeR,
									$author$project$Surface$familyBlocked(model),
									$elm$core$Basics$not),
								selected)),
						$author$project$Desktop$CommitSwitcher)
					]),
				A2(
					$elm$core$List$map,
					row,
					$author$project$Switcher$entries(model.e)));
		} else {
			if (model.t) {
				var scoped = function (message) {
					return A2(
						$elm$core$Maybe$map,
						message,
						$author$project$Desktop$capture(model));
				};
				var workspaceControl = function (group) {
					return {
						h: 'Browse workspace ' + (group.bX + (group.dC ? '; active workspace' : '')),
						f: _Utils_ap(
							group.dC ? 'Active workspace' : '',
							_Utils_eq(
								model.ag,
								$elm$core$Maybe$Just(group.bX)) ? ' • Selected' : ''),
						i: A2($author$project$Desktop$key, model, 'overview:workspace:' + group.bX),
						dL: true,
						bu: 'overview:workspace:' + group.bX,
						cZ: 'Workspace ' + group.bX,
						g: scoped(
							function (stamp) {
								return A2(
									$author$project$Desktop$OverviewWorkspace,
									stamp,
									$elm$core$Maybe$Just(group.bX));
							})
					};
				};
				var groups = A2(
					$elm$core$Maybe$withDefault,
					_List_Nil,
					$author$project$TaskView$groups(model.a.b));
				var familyControl = F2(
					function (group, family) {
						var ready = $author$project$Shell$available(model.a.b) && (family.ca && (!A2($author$project$Surface$familyBlocked, model, family.v)));
						var identity = 'overview:family:' + $author$project$UInt64$string(family.v);
						var detail = 'Workspace ' + (group.bX + (' • ' + (A2($author$project$Surface$familyBlocked, model, family.v) ? 'Awaiting native confirmation' : ((!family.ca) ? 'Unavailable for activation' : (family.a7 ? 'Minimized' : 'Open')))));
						return {
							h: (family.a7 ? 'Restore ' : 'Activate ') + (family.cZ + (' on workspace ' + group.bX)),
							f: detail,
							i: A2($author$project$Desktop$key, model, identity),
							dL: ready,
							bu: identity,
							cZ: family.cZ,
							g: ready ? scoped(
								function (stamp) {
									return A2($author$project$Desktop$OverviewChoose, stamp, family.v);
								}) : $elm$core$Maybe$Nothing
						};
					});
				var workspaceRows = function (group) {
					return A2(
						$elm$core$List$cons,
						workspaceControl(group),
						(_Utils_eq(model.ag, $elm$core$Maybe$Nothing) || _Utils_eq(
							model.ag,
							$elm$core$Maybe$Just(group.bX))) ? A2(
							$elm$core$List$map,
							familyControl(group),
							group.a) : _List_Nil);
				};
				return _Utils_ap(
					_List_fromArray(
						[
							{
							h: 'Close Task View and return to windows',
							f: '',
							i: A2($author$project$Desktop$key, model, 'overview:close'),
							dL: true,
							bu: 'control:close',
							cZ: 'Close Task View',
							g: scoped($author$project$Desktop$CloseOverview)
						},
							{
							h: 'Browse all workspaces',
							f: _Utils_eq(model.ag, $elm$core$Maybe$Nothing) ? 'Selected' : '',
							i: A2($author$project$Desktop$key, model, 'overview:all'),
							dL: true,
							bu: 'overview:all',
							cZ: 'All windows',
							g: scoped(
								function (stamp) {
									return A2($author$project$Desktop$OverviewWorkspace, stamp, $elm$core$Maybe$Nothing);
								})
						}
						]),
					_Utils_ap(
						A2($elm$core$List$concatMap, workspaceRows, groups),
						_List_fromArray(
							[
								A2($author$project$Surface$recoveryControl, 'overview:refresh', model)
							])));
			} else {
				if (model.q) {
					var scoped = function (build) {
						return A2(
							$elm$core$Maybe$map,
							build,
							$author$project$Desktop$capture(model));
					};
					var ready = !A2(
						$elm$core$List$member,
						$author$project$Launch$status(model.p),
						_List_fromArray(
							['Pending', 'Unknown']));
					var pinIds = $author$project$Desktop$pinIdentities(model);
					var pinAction = F5(
						function (suffix, label, detail, allowed, message) {
							return {
								h: label,
								f: detail,
								i: A2($author$project$Desktop$key, model, suffix),
								dL: $author$project$Pins$writable(model.y) && allowed,
								bu: suffix,
								cZ: label,
								g: ($author$project$Pins$writable(model.y) && allowed) ? scoped(message) : $elm$core$Maybe$Nothing
							};
						});
					var pinRows = F2(
						function (index, identity) {
							var label = A2(
								$elm$core$Maybe$withDefault,
								identity,
								A2(
									$elm$core$Maybe$map,
									function ($) {
										return $.cl;
									},
									A2(
										$elm$core$Maybe$andThen,
										$author$project$Catalog$lookup(identity),
										model.ak)));
							return _List_fromArray(
								[
									A5(
									pinAction,
									'unpin:' + identity,
									'Unpin ' + label,
									'Pinned application',
									true,
									function (stamp) {
										return A2($author$project$Desktop$TogglePin, stamp, identity);
									}),
									A5(
									pinAction,
									'pin-left:' + identity,
									'Move ' + (label + ' left'),
									'Pin order',
									index > 0,
									function (stamp) {
										return A3($author$project$Desktop$MovePin, stamp, identity, -1);
									}),
									A5(
									pinAction,
									'pin-right:' + identity,
									'Move ' + (label + ' right'),
									'Pin order',
									_Utils_cmp(
										index,
										$elm$core$List$length(pinIds) - 1) < 0,
									function (stamp) {
										return A3($author$project$Desktop$MovePin, stamp, identity, 1);
									})
								]);
						});
					var entryControl = function (entry) {
						var choice = ready ? A2(
							$elm$core$Maybe$map,
							$author$project$Desktop$Start,
							A2(
								$author$project$Launch$select,
								$author$project$Catalog$id(entry.bX),
								model.p)) : $elm$core$Maybe$Nothing;
						return {
							h: 'Open ' + entry.cl,
							f: '',
							i: A2(
								$author$project$Desktop$key,
								model,
								'entry:' + $author$project$Catalog$id(entry.bX)),
							dL: !_Utils_eq(choice, $elm$core$Maybe$Nothing),
							bu: 'entry:' + $author$project$Catalog$id(entry.bX),
							cZ: 'Open ' + entry.cl,
							g: choice
						};
					};
					var entries = A2(
						$elm$core$Maybe$withDefault,
						_List_Nil,
						A2(
							$elm$core$Maybe$map,
							$author$project$Catalog$search(model.b$),
							model.ak));
					var pinFirst = A2(
						$elm$core$Maybe$withDefault,
						_List_Nil,
						A2(
							$elm$core$Maybe$map,
							$elm$core$List$singleton,
							A2(
								$elm$core$Maybe$andThen,
								function (entry) {
									return A2(
										$elm$core$List$member,
										$author$project$Catalog$id(entry.bX),
										pinIds) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(
										A5(
											pinAction,
											'pin:' + $author$project$Catalog$id(entry.bX),
											'Pin ' + entry.cl,
											'Add to taskbar',
											true,
											function (stamp) {
												return A2(
													$author$project$Desktop$TogglePin,
													stamp,
													$author$project$Catalog$id(entry.bX));
											}));
								},
								$elm$core$List$head(entries))));
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
										h: 'I checked; allow another launch',
										f: '',
										i: A2($author$project$Desktop$key, model, 'control:acknowledge'),
										dL: true,
										bu: 'control:acknowledge',
										cZ: 'I checked; allow another launch',
										g: $elm$core$Maybe$Just(
											$author$project$Desktop$Acknowledge(token))
									};
								},
								$author$project$Launch$uncertain(model.p))));
					return _Utils_ap(
						_List_fromArray(
							[
								{
								h: 'Search applications',
								f: '',
								i: 'launcher-search',
								dL: true,
								bu: 'control:search',
								cZ: model.b$,
								g: scoped(
									function (stamp) {
										return A2($author$project$Desktop$SearchQuery, stamp, model.b$);
									})
							},
								{
								h: 'Close applications and return to windows',
								f: '',
								i: A2($author$project$Desktop$key, model, 'control:close'),
								dL: true,
								bu: 'control:close',
								cZ: 'Windows',
								g: scoped($author$project$Desktop$CloseApplications)
							},
								{
								h: 'Refresh applications',
								f: '',
								i: A2($author$project$Desktop$key, model, 'control:refresh'),
								dL: true,
								bu: 'control:refresh',
								cZ: 'Refresh',
								g: scoped($author$project$Desktop$OpenApplications)
							}
							]),
						_Utils_ap(
							acknowledge,
							_Utils_ap(
								pinFirst,
								_Utils_ap(
									$elm$core$List$concat(
										A2($elm$core$List$indexedMap, pinRows, pinIds)),
									A2($elm$core$List$map, entryControl, entries)))));
				} else {
					if (!_Utils_eq(
						$author$project$MenuBridge$menuSnapshot(model.a.k).aq,
						$elm$core$Maybe$Nothing)) {
						var _v1 = $author$project$MenuBridge$menuSnapshot(model.a.k).aq;
						if (_v1.$ === 1) {
							return _List_Nil;
						} else {
							var menu = _v1.a;
							var ready = $author$project$Shell$available(model.a.b) && (_Utils_eq(menu.cx, $author$project$Menu$Ready) && (!$author$project$Surface$menuBlocked(model)));
							var prefix = 'menu:' + ($elm$core$String$fromInt(
								$author$project$Menu$menuNumber(menu.bu)) + ':');
							var row = F2(
								function (index, item) {
									var detail = $author$project$Surface$menuBlocked(model) ? 'Awaiting native confirmation' : (_Utils_eq(
										menu.eb,
										$elm$core$Maybe$Just(index)) ? 'Selected' : '');
									return {
										h: _Utils_ap(
											item.cZ,
											$author$project$Surface$menuBlocked(model) ? ('; ' + detail) : ''),
										f: detail,
										i: _Utils_ap(
											prefix,
											$elm$core$String$fromInt(index)),
										dL: ready && item.dL,
										bu: _Utils_ap(
											prefix,
											$elm$core$String$fromInt(index)),
										cZ: item.cZ,
										g: (ready && item.dL) ? $elm$core$Maybe$Just(
											$author$project$Desktop$Window(
												$author$project$TaskbarShell$MenuEvent(
													A3($author$project$Menu$Activate, menu.bu, menu.d, index)))) : $elm$core$Maybe$Nothing
									};
								});
							var snap = A2(
								$elm$core$Maybe$andThen,
								function (provider) {
									return A2(
										$elm$core$Maybe$map,
										function (_v2) {
											return {
												h: 'Open snapping',
												f: '',
												i: prefix + 'snap',
												dL: ready,
												bu: 'control:snap-open',
												cZ: 'Snap window',
												g: ready ? A2(
													$elm$core$Maybe$map,
													function (stamp) {
														return A2(
															$author$project$Desktop$OpenSnap,
															stamp,
															$author$project$Provider$incarnation(provider));
													},
													$author$project$Desktop$capture(model)) : $elm$core$Maybe$Nothing
											};
										},
										A2(
											$elm$core$Maybe$andThen,
											function (geometry) {
												return A2(
													$author$project$Snap$open,
													geometry,
													$author$project$Provider$incarnation(provider));
											},
											model.a.b.ad));
								},
								$author$project$MenuBridge$currentProvider(model.a.k));
							return A2(
								$elm$core$List$cons,
								{
									h: 'Close window actions',
									f: '',
									i: prefix + 'close',
									dL: true,
									bu: 'control:menu-close',
									cZ: 'Close',
									g: $elm$core$Maybe$Just(
										$author$project$Desktop$Window(
											$author$project$TaskbarShell$MenuEvent(
												$author$project$Menu$Dismiss(menu.bu))))
								},
								_Utils_ap(
									A2($elm$core$List$indexedMap, row, menu.dX),
									_Utils_ap(
										A2(
											$elm$core$Maybe$withDefault,
											_List_Nil,
											A2($elm$core$Maybe$map, $elm$core$List$singleton, snap)),
										$author$project$Surface$recoveryPopup(model))));
						}
					} else {
						var _v3 = model.a.J;
						if (!_v3.$) {
							var picker = _v3.a;
							var familyControl = function (family) {
								var ready = $author$project$Shell$available(model.a.b) && (family.ca && ((!A2($author$project$Surface$familyBlocked, model, family.v)) && _Utils_eq(
									$author$project$Shell$capture(model.a.b),
									$elm$core$Maybe$Just(picker.b3))));
								var detail = A2($author$project$Surface$familyBlocked, model, family.v) ? 'Awaiting native confirmation' : (family.a7 ? 'Minimized' : 'Open');
								return {
									h: _Utils_ap(
										family.a7 ? 'Restore ' : 'Activate ',
										_Utils_ap(
											family.cZ,
											A2($author$project$Surface$familyBlocked, model, family.v) ? ('; ' + detail) : '')),
									f: detail,
									i: 'picker:' + ($author$project$Shell$stampKey(picker.b3) + (':' + ($author$project$UInt64$string(picker.dP) + (':' + $author$project$UInt64$string(family.v))))),
									dL: ready,
									bu: 'family:' + $author$project$UInt64$string(family.v),
									cZ: _Utils_ap(
										family.a7 ? 'Restore ' : 'Activate ',
										family.cZ),
									g: ready ? $elm$core$Maybe$Just(
										$author$project$Desktop$Window(
											A3($author$project$TaskbarShell$Choose, picker.b3, picker.dP, family.v))) : $elm$core$Maybe$Nothing
								};
							};
							var families = A2(
								$elm$core$List$concatMap,
								function ($) {
									return $.am;
								},
								A2(
									$elm$core$List$filter,
									function (group) {
										return _Utils_eq(group.ap, picker.ap);
									},
									$author$project$TaskbarShell$groups(model.a)));
							return A2(
								$elm$core$List$cons,
								{
									h: 'Close window picker',
									f: '',
									i: 'picker-close:' + ($author$project$Shell$stampKey(picker.b3) + (':' + $author$project$UInt64$string(picker.dP))),
									dL: true,
									bu: 'control:close',
									cZ: 'Close',
									g: $elm$core$Maybe$Just(
										$author$project$Desktop$Window(
											A2($author$project$TaskbarShell$Close, picker.b3, picker.dP)))
								},
								_Utils_ap(
									A2($elm$core$List$map, familyControl, families),
									$author$project$Surface$recoveryPopup(model)));
						} else {
							return _List_Nil;
						}
					}
				}
			}
		}
	}
};
var $elm$json$Json$Encode$int = _Json_wrap;
var $elm$json$Json$Encode$list = F2(
	function (func, entries) {
		return _Json_wrap(
			A3(
				$elm$core$List$foldl,
				_Json_addEntry(func),
				_Json_emptyArray(0),
				entries));
	});
var $author$project$Surface$mode = function (model) {
	return (!_Utils_eq(model.w, $elm$core$Maybe$Nothing)) ? 'snap' : ($author$project$Desktop$switcherOpen(model) ? 'switcher' : (model.t ? 'overview' : (model.q ? 'applications' : ((!_Utils_eq(
		$author$project$MenuBridge$menuSnapshot(model.a.k).aq,
		$elm$core$Maybe$Nothing)) ? 'menu' : ((!_Utils_eq(model.a.J, $elm$core$Maybe$Nothing)) ? 'picker' : 'closed')))));
};
var $author$project$Effects$Cancelled = 3;
var $author$project$Surface$reservationReason = 'Window action awaits native confirmation. Refresh status only reads observations; it does not retry the action.';
var $author$project$Shell$status = function (model) {
	if (model.bD) {
		return 'Window recovery history is full. Restart the shell to continue.';
	} else {
		if (model.H) {
			return 'Window transport is full or unavailable. Waiting for a verified output or capacity update.';
		} else {
			var _v0 = A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.cx;
				},
				model.R.z);
			_v0$3:
			while (true) {
				if (!_v0.$) {
					switch (_v0.a) {
						case 0:
							var _v1 = _v0.a;
							return 'Applying window change…';
						case 4:
							var _v2 = _v0.a;
							return model.d_ + ' The last request could not be confirmed.';
						case 2:
							var _v3 = _v0.a;
							return model.d_ + ' The window change was refused.';
						default:
							break _v0$3;
					}
				} else {
					break _v0$3;
				}
			}
			return model.d_;
		}
	}
};
var $author$project$Surface$windowNotice = function (model) {
	var subject = function (transaction) {
		var operation = function () {
			var _v3 = transaction.K.aK;
			switch (_v3.$) {
				case 0:
					return 'Minimize';
				case 1:
					return 'Restore';
				case 2:
					return 'Activate';
				case 3:
					return 'Maximize';
				case 4:
					return 'Restore size';
				default:
					return 'Snap';
			}
		}();
		var label = A2(
			$elm$core$Maybe$withDefault,
			'selected window',
			A2(
				$elm$core$Maybe$map,
				A2(
					$elm$core$Basics$composeR,
					function ($) {
						return $.cZ;
					},
					$elm$core$String$left(512)),
				$elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (family) {
							return _Utils_eq(family.v, transaction.K.U);
						},
						A2(
							$elm$core$List$concatMap,
							function ($) {
								return $.am;
							},
							$author$project$TaskbarShell$groups(model.a))))));
		return _Utils_Tuple2(operation, label);
	};
	var _v0 = model.a.b.R.z;
	if (!_v0.$) {
		var transaction = _v0.a;
		var _v1 = subject(transaction);
		var operation = _v1.a;
		var label = _v1.b;
		var _v2 = transaction.cx;
		switch (_v2) {
			case 0:
				return operation + (': applying to ' + (label + '…'));
			case 4:
				return operation + (': not confirmed for ' + (label + ((!model.a.b.G) ? '. Reconnect to read window status; the action will not be repeated.' : '. Check your windows; Refresh only reads status.')));
			case 2:
				return operation + (': refused for ' + (label + '. Refresh window status, then choose again.'));
			case 3:
				return operation + (': cancelled for ' + (label + '.'));
			default:
				return $author$project$Surface$recoveryNeeded(model) ? $author$project$Surface$reservationReason : $author$project$Shell$status(model.a.b);
		}
	} else {
		return ($author$project$Surface$recoveryNeeded(model) && (!(!model.a.b.G))) ? $author$project$Surface$reservationReason : $author$project$Shell$status(model.a.b);
	}
};
var $author$project$Surface$notice = function (model) {
	if ($author$project$Desktop$switcherOpen(model)) {
		return ($author$project$Switcher$phase(model.e) === 1) ? 'Loading window activation history…' : ((!_Utils_eq(model.O, $elm$core$Maybe$Nothing)) ? 'Alt+Tab: next window. Alt+Shift+Tab: previous. Release Alt: activate. Escape: cancel.' : 'Tab or Right: next window. Shift+Tab or Left: previous. Enter: activate. Escape: cancel.');
	} else {
		if (model.t) {
			if ($author$project$Surface$recoveryNeeded(model)) {
				return $author$project$Surface$windowNotice(model);
			} else {
				var _v0 = $author$project$TaskView$groups(model.a.b);
				if (_v0.$ === 1) {
					return 'Waiting for current workspace information. Refresh window status.';
				} else {
					if (!_v0.a.b) {
						return 'No windows to show. Close Task View to return.';
					} else {
						return 'Choose a window to reveal its workspace, or browse another workspace.';
					}
				}
			}
		} else {
			if ($author$project$Surface$mode(model) === 'menu') {
				var _v1 = A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.cx;
					},
					$author$project$MenuBridge$menuSnapshot(model.a.k).aq);
				_v1$3:
				while (true) {
					if (!_v1.$) {
						switch (_v1.a.$) {
							case 2:
								var reason = _v1.a.a;
								return reason;
							case 4:
								return 'The operation could not be confirmed.';
							case 1:
								return 'Working…';
							default:
								break _v1$3;
						}
					} else {
						break _v1$3;
					}
				}
				return $author$project$Surface$menuBlocked(model) ? $author$project$Surface$reservationReason : 'Window actions';
			} else {
				if (!_Utils_eq(model.j, $elm$core$Maybe$Nothing)) {
					return 'Updating your window choice…';
				} else {
					if (!$elm$core$String$isEmpty(model.E)) {
						return model.E;
					} else {
						if ((!model.q) && A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (transaction) {
									return A2(
										$elm$core$List$member,
										transaction.cx,
										_List_fromArray(
											[0, 4, 2, 3]));
								},
								model.a.b.R.z))) {
							return $author$project$Surface$windowNotice(model);
						} else {
							if ((!$elm$core$String$isEmpty(model.y.d_)) && (model.y.d_ !== 'Pin order saved.')) {
								return model.y.d_;
							} else {
								var _v2 = $author$project$Launch$status(model.p);
								switch (_v2) {
									case 'Pending':
										return 'Opening application…';
									case 'Unknown':
										return 'The launch could not be confirmed. Check your windows before opening it again.';
									case 'Submitted':
										return 'Launch submitted.';
									case 'Refused':
										return 'Launch refused. Refresh applications and choose again.';
									default:
										return (!_Utils_eq(model.aS, $elm$core$Maybe$Nothing)) ? (($author$project$Surface$recoveryNeeded(model) && (!(!model.a.b.G))) ? $author$project$Surface$reservationReason : 'Applications were not opened. Choose Applications again.') : (model.q ? ((!_Utils_eq(model.n, $elm$core$Maybe$Nothing)) ? 'Loading applications…' : (_Utils_eq(model.ak, $elm$core$Maybe$Nothing) ? 'Application list unavailable. Refresh to try again.' : (A2(
											$elm$core$Maybe$withDefault,
											false,
											A2(
												$elm$core$Maybe$map,
												A2(
													$elm$core$Basics$composeR,
													$author$project$Catalog$search(model.b$),
													$elm$core$List$isEmpty),
												model.ak)) ? 'No matching applications. Change your search or Refresh.' : ($elm$core$String$isEmpty(
											$elm$core$String$trim(model.b$)) ? 'Type to search applications.' : 'Choose a matching application.')))) : $author$project$Surface$windowNotice(model));
								}
							}
						}
					}
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
						$elm$json$Json$Encode$string(control.bu)),
						_Utils_Tuple2(
						'domId',
						$elm$json$Json$Encode$string(control.i)),
						_Utils_Tuple2(
						'label',
						$elm$json$Json$Encode$string(control.cZ)),
						_Utils_Tuple2(
						'ariaLabel',
						$elm$json$Json$Encode$string(control.h)),
						_Utils_Tuple2(
						'detail',
						$elm$json$Json$Encode$string(control.f)),
						_Utils_Tuple2(
						'enabled',
						$elm$json$Json$Encode$bool(
							control.dL && (!_Utils_eq(control.g, $elm$core$Maybe$Nothing))))
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
	return A3($author$project$Surface$packet, model.bC, model.aI, model.c);
};
var $elm$json$Json$Encode$null = _Json_encodeNull;
var $author$project$ReceiptRouter$count = function (_v0) {
	var entries = _v0;
	return $elm$core$List$length(entries);
};
var $author$project$MenuBridge$receiptCount = function (_v0) {
	var state = _v0;
	return $author$project$ReceiptRouter$count(state.V);
};
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
var $author$project$Provider$title = function (_v0) {
	var value = _v0;
	return value.dr;
};
var $elm$core$Result$withDefault = F2(
	function (def, result) {
		if (!result.$) {
			var a = result.a;
			return a;
		} else {
			return def;
		}
	});
var $author$project$Inspection$packet = function (controller) {
	var frame = $author$project$SurfaceController$frame(controller);
	var field = function (name) {
		return A2(
			$elm$core$Result$withDefault,
			$elm$json$Json$Encode$null,
			A2(
				$elm$json$Json$Decode$decodeValue,
				A2($elm$json$Json$Decode$field, name, $elm$json$Json$Decode$value),
				frame));
	};
	var desktop = $author$project$SurfaceController$desktop(controller);
	var model = desktop.a;
	var menuRecord = function (current) {
		var provider = $author$project$MenuBridge$currentProvider(model.k);
		var prefix = 'menu:' + ($elm$core$String$fromInt(
			$author$project$Menu$menuNumber(current.bu)) + ':');
		var row = F2(
			function (index, item) {
				return $elm$json$Json$Encode$object(
					_List_fromArray(
						[
							_Utils_Tuple2(
							'domId',
							$elm$json$Json$Encode$string(
								_Utils_ap(
									prefix,
									$elm$core$String$fromInt(index)))),
							_Utils_Tuple2(
							'label',
							$elm$json$Json$Encode$string(item.cZ)),
							_Utils_Tuple2(
							'enabled',
							$elm$json$Json$Encode$bool(item.dL))
						]));
			});
		return $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'id',
					$elm$json$Json$Encode$int(
						$author$project$Menu$menuNumber(current.bu))),
					_Utils_Tuple2(
					'closeId',
					$elm$json$Json$Encode$string(prefix + 'close')),
					_Utils_Tuple2(
					'incarnation',
					A2(
						$elm$core$Maybe$withDefault,
						$elm$json$Json$Encode$null,
						A2(
							$elm$core$Maybe$map,
							A2(
								$elm$core$Basics$composeR,
								$author$project$Provider$incarnation,
								A2($elm$core$Basics$composeR, $author$project$UInt64$string, $elm$json$Json$Encode$string)),
							provider))),
					_Utils_Tuple2(
					'title',
					A2(
						$elm$core$Maybe$withDefault,
						$elm$json$Json$Encode$null,
						A2(
							$elm$core$Maybe$map,
							A2($elm$core$Basics$composeR, $author$project$Provider$title, $elm$json$Json$Encode$string),
							provider))),
					_Utils_Tuple2(
					'selected',
					A2(
						$elm$core$Maybe$withDefault,
						$elm$json$Json$Encode$null,
						A2($elm$core$Maybe$map, $elm$json$Json$Encode$int, current.eb))),
					_Utils_Tuple2(
					'actions',
					A2(
						$elm$json$Json$Encode$list,
						$elm$core$Basics$identity,
						A2($elm$core$List$indexedMap, row, current.dX)))
				]));
	};
	var pickerRecord = function (current) {
		var family = function (item) {
			return $elm$json$Json$Encode$object(
				_List_fromArray(
					[
						_Utils_Tuple2(
						'incarnation',
						$elm$json$Json$Encode$string(
							$author$project$UInt64$string(item.v))),
						_Utils_Tuple2(
						'title',
						$elm$json$Json$Encode$string(item.cZ)),
						_Utils_Tuple2(
						'state',
						$elm$json$Json$Encode$string(
							item.a7 ? 'Minimized' : 'Open')),
						_Utils_Tuple2(
						'domId',
						$elm$json$Json$Encode$string(
							'picker:' + ($author$project$Shell$stampKey(current.b3) + (':' + ($author$project$UInt64$string(current.dP) + (':' + $author$project$UInt64$string(item.v)))))))
					]));
		};
		return $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'generation',
					$elm$json$Json$Encode$string(
						$author$project$UInt64$string(current.dP))),
					_Utils_Tuple2(
					'closeId',
					$elm$json$Json$Encode$string(
						'picker-close:' + ($author$project$Shell$stampKey(current.b3) + (':' + $author$project$UInt64$string(current.dP))))),
					_Utils_Tuple2(
					'selections',
					A2(
						$elm$json$Json$Encode$list,
						family,
						A2(
							$elm$core$List$concatMap,
							function ($) {
								return $.am;
							},
							A2(
								$elm$core$List$filter,
								function (item) {
									return _Utils_eq(item.ap, current.ap);
								},
								$author$project$TaskbarShell$groups(model)))))
				]));
	};
	var shell = model.b;
	var phase = function () {
		var _v0 = shell.G;
		switch (_v0) {
			case 2:
				return 'Coherent';
			case 0:
				return 'Detached';
			case 1:
				return 'Awaiting';
			default:
				return 'Exhausted';
		}
	}();
	var stamp = A2(
		$elm$core$Maybe$withDefault,
		'detached',
		A2(
			$elm$core$Maybe$map,
			$author$project$Shell$stampKey,
			$author$project$Shell$capture(shell)));
	var group = function (item) {
		return $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'key',
					$elm$json$Json$Encode$string(item.ap)),
					_Utils_Tuple2(
					'domId',
					$elm$json$Json$Encode$string('group:' + (stamp + (':' + item.ap)))),
					_Utils_Tuple2(
					'title',
					$elm$json$Json$Encode$string(
						A2(
							$elm$core$Maybe$withDefault,
							'Windows',
							A2(
								$elm$core$Maybe$map,
								function ($) {
									return $.cZ;
								},
								$elm$core$List$head(item.am))))),
					_Utils_Tuple2(
					'active',
					$elm$json$Json$Encode$bool(
						A2(
							$elm$core$List$any,
							function ($) {
								return $.dC;
							},
							item.am))),
					_Utils_Tuple2(
					'expanded',
					$elm$json$Json$Encode$bool(
						A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (picker) {
									return _Utils_eq(picker.ap, item.ap);
								},
								model.J))))
				]));
	};
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'surfaceProtocol',
				$elm$json$Json$Encode$int(2)),
				_Utils_Tuple2(
				'kind',
				$elm$json$Json$Encode$string('surface-inspection')),
				_Utils_Tuple2(
				'publication',
				field('publication')),
				_Utils_Tuple2(
				'lease',
				field('lease')),
				_Utils_Tuple2(
				'body',
				$elm$json$Json$Encode$object(
					_List_fromArray(
						[
							_Utils_Tuple2(
							'phase',
							$elm$json$Json$Encode$string(phase)),
							_Utils_Tuple2(
							'transaction',
							$elm$json$Json$Encode$string(
								A2(
									$elm$core$Maybe$withDefault,
									'Idle',
									A2(
										$elm$core$Maybe$map,
										A2(
											$elm$core$Basics$composeR,
											function ($) {
												return $.cx;
											},
											$author$project$Effects$statusName),
										shell.R.z)))),
							_Utils_Tuple2(
							'groups',
							A2(
								$elm$json$Json$Encode$list,
								group,
								$author$project$TaskbarShell$groups(model))),
							_Utils_Tuple2(
							'menu',
							A2(
								$elm$core$Maybe$withDefault,
								$elm$json$Json$Encode$null,
								A2(
									$elm$core$Maybe$map,
									menuRecord,
									$author$project$MenuBridge$menuSnapshot(model.k).aq))),
							_Utils_Tuple2(
							'mode',
							field('mode')),
							_Utils_Tuple2(
							'outstanding',
							$elm$json$Json$Encode$int(
								$author$project$MenuBridge$menuSnapshot(model.k).d3)),
							_Utils_Tuple2(
							'registry',
							$elm$json$Json$Encode$int(
								$author$project$MenuBridge$receiptCount(model.k))),
							_Utils_Tuple2(
							'picker',
							A2(
								$elm$core$Maybe$withDefault,
								$elm$json$Json$Encode$null,
								A2($elm$core$Maybe$map, pickerRecord, model.J))),
							_Utils_Tuple2(
							'openerId',
							$elm$json$Json$Encode$string(
								A2($author$project$Desktop$key, desktop, 'control:opener'))),
							_Utils_Tuple2(
							'reconnectId',
							$elm$json$Json$Encode$string('reconnect'))
						])))
			]));
};
var $author$project$TaskbarShell$CancelPrepared = function (a) {
	return {$: 7, a: a};
};
var $author$project$SurfaceController$Interaction = function (a) {
	return {$: 0, a: a};
};
var $author$project$Shell$RegistrationRefused = F2(
	function (a, b) {
		return {$: 13, a: a, b: b};
	});
var $author$project$OutputController$Scope = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$Desktop$InvalidateSnap = {$: 6};
var $author$project$SurfaceController$Publish = function (a) {
	return {$: 1, a: a};
};
var $author$project$SurfaceController$DesktopEffect = function (a) {
	return {$: 0, a: a};
};
var $author$project$Shell$ReconciliationFull = {$: 0};
var $author$project$Shell$RecoveredUnknown = F2(
	function (a, b) {
		return {$: 1, a: a, b: b};
	});
var $author$project$Shell$ReservationReleased = F4(
	function (a, b, c, d) {
		return {$: 2, a: a, b: b, c: c, d: d};
	});
var $author$project$Desktop$Send = function (a) {
	return {$: 1, a: a};
};
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
var $author$project$ReconciliationFrame$Proof = F9(
	function (protocolVersion, kind, retirementProtocol, operation, binding, requestId, queriedBinding, sequence, grantState) {
		return {d: binding, dR: grantState, cX: kind, aK: operation, d6: protocolVersion, de: queriedBinding, dh: requestId, d9: retirementProtocol, dm: sequence};
	});
var $elm$json$Json$Decode$andThen = _Json_andThen;
var $author$project$Binding$Binding = F3(
	function (a, b, c) {
		return {$: 0, a: a, b: b, c: c};
	});
var $elm$json$Json$Decode$fail = _Json_fail;
var $elm$json$Json$Decode$keyValuePairs = _Json_decodeKeyValuePairs;
var $elm$json$Json$Decode$map3 = _Json_map3;
var $elm$core$Basics$ge = _Utils_ge;
var $elm$json$Json$Decode$string = _Json_decodeString;
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
var $elm$json$Json$Decode$int = _Json_decodeInt;
var $author$project$ReconciliationFrame$exactInt = function (n) {
	return A2(
		$elm$json$Json$Decode$andThen,
		function (v) {
			return _Utils_eq(v, n) ? $elm$json$Json$Decode$succeed(v) : $elm$json$Json$Decode$fail('Unsupported protocol/schema');
		},
		$elm$json$Json$Decode$int);
};
var $author$project$ReconciliationFrame$exactString = function (n) {
	return A2(
		$elm$json$Json$Decode$andThen,
		function (v) {
			return _Utils_eq(v, n) ? $elm$json$Json$Decode$succeed(v) : $elm$json$Json$Decode$fail('Unexpected frame/status');
		},
		$elm$json$Json$Decode$string);
};
var $elm$json$Json$Decode$map8 = _Json_map8;
var $author$project$ReconciliationFrame$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return _Utils_eq(value, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero authority counter') : $elm$json$Json$Decode$succeed(value);
	},
	$author$project$UInt64$decoder);
var $author$project$ReconciliationFrame$strict = F2(
	function (fields, decoder) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? decoder : $elm$json$Json$Decode$fail('Unexpected or missing reconciliation fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$ReconciliationFrame$proofDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (proof) {
		return A2(
			$elm$json$Json$Decode$map,
			function (_v0) {
				return proof;
			},
			A2(
				$elm$json$Json$Decode$field,
				'grantState',
				$author$project$ReconciliationFrame$exactString('Retired')));
	},
	A2(
		$author$project$ReconciliationFrame$strict,
		_List_fromArray(
			['protocolVersion', 'kind', 'retirementProtocol', 'operation', 'binding', 'requestId', 'queriedBinding', 'sequence', 'grantState']),
		A9(
			$elm$json$Json$Decode$map8,
			F8(
				function (version, kind, protocol, operation, binding, request, queried, sequence) {
					return A9($author$project$ReconciliationFrame$Proof, version, kind, protocol, operation, binding, request, queried, sequence, 'Retired');
				}),
			A2(
				$elm$json$Json$Decode$field,
				'protocolVersion',
				$author$project$ReconciliationFrame$exactInt(3)),
			A2(
				$elm$json$Json$Decode$field,
				'kind',
				$author$project$ReconciliationFrame$exactString('binding-retirement')),
			A2(
				$elm$json$Json$Decode$field,
				'retirementProtocol',
				$author$project$ReconciliationFrame$exactInt(1)),
			A2(
				$elm$json$Json$Decode$field,
				'operation',
				A2(
					$elm$json$Json$Decode$andThen,
					function (v) {
						return A2(
							$elm$core$List$member,
							v,
							_List_fromArray(
								['observe', 'retire'])) ? $elm$json$Json$Decode$succeed(v) : $elm$json$Json$Decode$fail('Retirement operation');
					},
					$elm$json$Json$Decode$string)),
			A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
			A2($elm$json$Json$Decode$field, 'requestId', $author$project$ReconciliationFrame$positive),
			A2($elm$json$Json$Decode$field, 'queriedBinding', $author$project$Binding$decoder),
			A2($elm$json$Json$Decode$field, 'sequence', $author$project$ReconciliationFrame$positive))));
var $author$project$Binding$sameLifetime = F2(
	function (life, _v0) {
		var lifetime = _v0.a;
		return _Utils_eq(life, lifetime);
	});
var $author$project$ReconciliationTracking$announce = F3(
	function (current, raw, model) {
		return A2(
			$elm$core$Result$andThen,
			function (proof) {
				var newer = function (slot) {
					return A2(
						$elm$core$Maybe$withDefault,
						true,
						A2(
							$elm$core$Maybe$map,
							function (old) {
								return A2($author$project$UInt64$compare, proof.dm, old.dm) === 2;
							},
							slot.dc));
				};
				var informationalScopeChanged = A2(
					$elm$core$Maybe$withDefault,
					false,
					A2(
						$elm$core$Maybe$map,
						function (active) {
							return !_Utils_eq(active.de, proof.de);
						},
						model.aH));
				var eligible = function (slot) {
					return _Utils_eq(slot.df.d, proof.de) && A2($author$project$Binding$sameLifetime, slot.df.K.A.dY, current);
				};
				var anotherActiveScope = A2(
					$elm$core$List$any,
					function (slot) {
						return (!slot.b1) && A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (active) {
									return !_Utils_eq(active.de, proof.de);
								},
								slot.dc));
					},
					model.s);
				return (anotherActiveScope || (informationalScopeChanged || ((!_Utils_eq(proof.d, current)) || (_Utils_eq(proof.de, current) || ((!A2($elm$core$List$any, eligible, model.s)) || (!A2(
					$elm$core$List$all,
					function (slot) {
						return (!eligible(slot)) || newer(slot);
					},
					model.s))))))) ? $elm$core$Result$Err('Uncorrelated proof announcement') : $elm$core$Result$Ok(
					_Utils_update(
						model,
						{
							aH: A2(
								$elm$core$List$any,
								function (slot) {
									return eligible(slot) && (!slot.b1);
								},
								model.s) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(proof),
							s: A2(
								$elm$core$List$map,
								function (slot) {
									return eligible(slot) ? _Utils_update(
										slot,
										{
											dB: $elm$core$Maybe$Nothing,
											a3: $elm$core$Maybe$Nothing,
											ad: $elm$core$Maybe$Nothing,
											aF: $elm$core$Maybe$Nothing,
											dc: $elm$core$Maybe$Just(proof)
										}) : slot;
								},
								model.s)
						}));
			},
			A2(
				$elm$core$Result$mapError,
				$elm$json$Json$Decode$errorToString,
				A2($elm$json$Json$Decode$decodeValue, $author$project$ReconciliationFrame$proofDecoder, raw)));
	});
var $author$project$Switcher$generation = function (_v0) {
	var model = _v0;
	return model.dP;
};
var $elm$core$Char$fromCode = _Char_fromCode;
var $elm$core$String$fromList = _String_fromList;
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
var $author$project$Desktop$ArmChoice = function (a) {
	return {$: 3, a: a};
};
var $author$project$Desktop$ChoiceToken = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$Desktop$Focus = function (a) {
	return {$: 4, a: a};
};
var $author$project$Shell$Incoming = function (a) {
	return {$: 3, a: a};
};
var $author$project$Menu$Invalidate = function (a) {
	return {$: 6, a: a};
};
var $author$project$TaskbarShell$OpenMenu = function (a) {
	return {$: 4, a: a};
};
var $author$project$Desktop$OverviewOpener = {$: 1};
var $author$project$Desktop$TaskbarGroup = function (a) {
	return {$: 0, a: a};
};
var $author$project$Launch$advance = function (_v0) {
	var model = _v0;
	var _v1 = $author$project$UInt64$next(model.dj);
	if (!_v1.$) {
		var revision = _v1.a;
		return _Utils_update(
			model,
			{dj: revision});
	} else {
		return _Utils_update(
			model,
			{aG: $elm$core$Maybe$Nothing, bF: $elm$core$Maybe$Nothing});
	}
};
var $author$project$Launch$acknowledgeUnknown = F2(
	function (_v0, current) {
		var intent = _v0;
		var model = current;
		var _v1 = model.G;
		if ((_v1.$ === 2) && (_v1.b === 2)) {
			var active = _v1.a;
			var _v2 = _v1.b;
			return _Utils_eq(active, intent) ? $author$project$Launch$advance(
				_Utils_update(
					model,
					{G: $author$project$Launch$Idle})) : current;
		} else {
			return current;
		}
	});
var $author$project$TaskView$activeWorkspace = function (shell) {
	return A2(
		$elm$core$Maybe$map,
		function ($) {
			return $.bX;
		},
		A2(
			$elm$core$Maybe$andThen,
			A2(
				$elm$core$Basics$composeR,
				$elm$core$List$filter(
					function ($) {
						return $.dC;
					}),
				$elm$core$List$head),
			$author$project$TaskView$groups(shell)));
};
var $author$project$Switcher$Cancelled = 4;
var $author$project$Switcher$writable = function (model) {
	return A2(
		$elm$core$List$member,
		model.G,
		_List_fromArray(
			[1, 2]));
};
var $author$project$Switcher$cancel = F2(
	function (token, original) {
		var model = original;
		return ((!_Utils_eq(token, model.dP)) || (!$author$project$Switcher$writable(model))) ? original : _Utils_update(
			model,
			{bp: _List_Nil, G: 4});
	});
var $author$project$Desktop$retireSwitcher = function (model) {
	return _Utils_update(
		model,
		{
			e: A2(
				$author$project$Switcher$cancel,
				$author$project$Switcher$generation(model.e),
				model.e),
			ai: $elm$core$Maybe$Nothing,
			aj: $elm$core$Maybe$Nothing,
			bG: $elm$core$Maybe$Nothing
		});
};
var $author$project$Desktop$advance = function (model) {
	var _v0 = A2($elm$core$Maybe$andThen, $author$project$UInt64$next, model.aO);
	if (!_v0.$) {
		var value = _v0.a;
		return _Utils_update(
			model,
			{
				aO: $elm$core$Maybe$Just(value)
			});
	} else {
		return $author$project$Desktop$retireSwitcher(
			_Utils_update(
				model,
				{ak: $elm$core$Maybe$Nothing, n: $elm$core$Maybe$Nothing, q: false, t: false, aO: $elm$core$Maybe$Nothing}));
	}
};
var $elm$core$String$any = _String_any;
var $author$project$Desktop$canProveCatalogUnsent = F3(
	function (binding, request, model) {
		return _Utils_eq(
			model.a.b.d,
			$elm$core$Maybe$Just(binding)) && (_Utils_eq(
			model.n,
			$elm$core$Maybe$Just(request)) && ((!(!model.a.b.G)) && (model.a.b.G !== 3)));
	});
var $author$project$Catalog$Snapshot = F3(
	function (a, b, c) {
		return {$: 0, a: a, b: b, c: c};
	});
var $author$project$Catalog$Entry = F6(
	function (identity, name, iconHint, wmclass, genericName, keywords) {
		return {cP: genericName, dT: iconHint, bX: identity, cW: keywords, cl: name, eg: wmclass};
	});
var $author$project$Catalog$EntryId = $elm$core$Basics$identity;
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
		F4(
			function (identity, name, iconHint, wmclass) {
				return A6($author$project$Catalog$Entry, identity, name, iconHint, wmclass, '', _List_Nil);
			}),
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
var $elm$json$Json$Decode$list = _Json_decodeList;
var $elm$json$Json$Decode$map6 = _Json_map6;
var $author$project$Catalog$entryDecoder2 = A2(
	$author$project$Catalog$strict,
	_List_fromArray(
		['id', 'name', 'iconHint', 'wmclass', 'genericName', 'keywords']),
	A7(
		$elm$json$Json$Decode$map6,
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
			A2($author$project$Catalog$text, 512, false)),
		A2(
			$elm$json$Json$Decode$field,
			'genericName',
			A2($author$project$Catalog$text, 512, false)),
		A2(
			$elm$json$Json$Decode$field,
			'keywords',
			A2(
				$elm$json$Json$Decode$andThen,
				function (values) {
					return ($elm$core$List$length(values) <= 64) ? $elm$json$Json$Decode$succeed(values) : $elm$json$Json$Decode$fail('Keyword capacity');
				},
				$elm$json$Json$Decode$list(
					A2($author$project$Catalog$text, 128, false))))));
var $author$project$Catalog$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (!_Utils_eq(value, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Zero catalog authority');
	},
	$author$project$UInt64$decoder);
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
var $author$project$Catalog$decode = function (raw) {
	var protocol = A2(
		$elm$json$Json$Decode$andThen,
		function (value) {
			return A2(
				$elm$core$List$member,
				value,
				_List_fromArray(
					[1, 2])) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Catalog version');
		},
		A2($elm$json$Json$Decode$field, 'catalogProtocol', $elm$json$Json$Decode$int));
	var entryList = function (version) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (values) {
				return ($elm$core$List$length(values) <= 2048) ? $elm$json$Json$Decode$list(
					(version === 2) ? $author$project$Catalog$entryDecoder2 : $author$project$Catalog$entryDecoder) : $elm$json$Json$Decode$fail('Catalog capacity');
			},
			$elm$json$Json$Decode$list($elm$json$Json$Decode$value));
	};
	var decoder = A2(
		$elm$json$Json$Decode$andThen,
		function (value) {
			return A2(
				$author$project$Catalog$strict,
				_List_fromArray(
					['catalogProtocol', 'lifetime', 'generation', 'entries']),
				A4(
					$elm$json$Json$Decode$map3,
					F3(
						function (lifetime, generation, values) {
							return _Utils_Tuple3(lifetime, generation, values);
						}),
					A2($elm$json$Json$Decode$field, 'lifetime', $author$project$Catalog$positive),
					A2($elm$json$Json$Decode$field, 'generation', $author$project$Catalog$positive),
					A2(
						$elm$json$Json$Decode$field,
						'entries',
						entryList(value))));
		},
		protocol);
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
							$author$project$Catalog$id(entry.bX),
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
var $elm$core$Result$toMaybe = function (result) {
	if (!result.$) {
		var v = result.a;
		return $elm$core$Maybe$Just(v);
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$Launch$catalog = F2(
	function (raw, _v0) {
		var model = _v0;
		var snapshot = $elm$core$Result$toMaybe(
			$author$project$Catalog$decode(raw));
		var phase = function () {
			var _v1 = _Utils_Tuple2(snapshot, model.G);
			_v1$2:
			while (true) {
				if ((!_v1.a.$) && (_v1.b.$ === 2)) {
					switch (_v1.b.b) {
						case 1:
							var _v2 = _v1.b;
							var _v3 = _v2.b;
							return $author$project$Launch$Idle;
						case 0:
							var _v4 = _v1.b;
							var _v5 = _v4.b;
							return $author$project$Launch$Idle;
						default:
							break _v1$2;
					}
				} else {
					break _v1$2;
				}
			}
			return model.G;
		}();
		return $author$project$Launch$advance(
			_Utils_update(
				model,
				{G: phase, bF: snapshot}));
	});
var $author$project$Desktop$catalogRequest = F2(
	function (binding, request) {
		return $author$project$Desktop$Send(
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
					])));
	});
var $elm$core$Tuple$pair = F2(
	function (a, b) {
		return _Utils_Tuple2(a, b);
	});
var $author$project$Switcher$index = F2(
	function (root, rows) {
		return A2(
			$elm$core$Maybe$map,
			$elm$core$Tuple$first,
			$elm$core$List$head(
				A2(
					$elm$core$List$filter,
					function (_v0) {
						var row = _v0.b;
						return _Utils_eq(row.v, root);
					},
					A2($elm$core$List$indexedMap, $elm$core$Tuple$pair, rows))));
	});
var $elm$core$List$maximum = function (list) {
	if (list.b) {
		var x = list.a;
		var xs = list.b;
		return $elm$core$Maybe$Just(
			A3($elm$core$List$foldl, $elm$core$Basics$max, x, xs));
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$Switcher$lastOrdinal = function (model) {
	return A2(
		$elm$core$Maybe$withDefault,
		0,
		$elm$core$List$maximum(
			$elm$core$Dict$keys(model.a1)));
};
var $author$project$Switcher$choose = F3(
	function (token, root, original) {
		var model = original;
		return ((!_Utils_eq(token, model.dP)) || ((model.G !== 2) || (!_Utils_eq(model.b1, $elm$core$Maybe$Nothing)))) ? original : A2(
			$elm$core$Maybe$withDefault,
			original,
			A2(
				$elm$core$Maybe$map,
				function (position) {
					return _Utils_update(
						model,
						{
							aB: $elm$core$Maybe$Just(
								{
									v: root,
									b8: $author$project$Switcher$lastOrdinal(model)
								}),
							eb: position
						});
				},
				A2($author$project$Switcher$index, root, model.bp)));
	});
var $author$project$Desktop$WindowEffect = function (a) {
	return {$: 0, a: a};
};
var $author$project$Launch$PendingToken = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$Launch$pending = function (_v0) {
	var model = _v0;
	var _v1 = model.G;
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
var $author$project$Launch$Unknown = 2;
var $author$project$Launch$timeout = F2(
	function (_v0, current) {
		var host = _v0.a;
		var intent = _v0.b;
		var model = current;
		var _v1 = model.G;
		if (_v1.$ === 1) {
			var owner = _v1.a;
			var active = _v1.b;
			return (_Utils_eq(owner, host) && _Utils_eq(active, intent)) ? $author$project$Launch$advance(
				_Utils_update(
					model,
					{
						G: A2($author$project$Launch$Settled, intent, 2)
					})) : current;
		} else {
			return current;
		}
	});
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
			{aG: $elm$core$Maybe$Nothing, bF: $elm$core$Maybe$Nothing}));
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
				model.aG,
				$elm$core$Maybe$Just(host))) {
				return current;
			} else {
				var _v0 = $author$project$Launch$disconnect(current);
				var retired = _v0;
				return $author$project$Launch$advance(
					_Utils_update(
						retired,
						{
							aG: $elm$core$Maybe$Just(host)
						}));
			}
		}
	});
var $author$project$Shell$Act = F3(
	function (a, b, c) {
		return {$: 9, a: a, b: b, c: c};
	});
var $author$project$Menu$Maximize = {$: 5};
var $author$project$Menu$RestoreGeometry = {$: 1};
var $author$project$Provider$actionProtocol = function (action) {
	return (_Utils_eq(action, $author$project$Menu$Maximize) || _Utils_eq(action, $author$project$Menu$RestoreGeometry)) ? 2 : 1;
};
var $author$project$MenuBridge$answer = F4(
	function (bridge, shell, effects, error) {
		return {cC: bridge, R: effects, cK: error, b: shell};
	});
var $author$project$Menu$ReceiveFor = F3(
	function (a, b, c) {
		return {$: 4, a: a, b: b, c: c};
	});
var $author$project$Menu$Refusal = function (a) {
	return {$: 1, a: a};
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
var $author$project$Menu$Unknown = function (a) {
	return {$: 4, a: a};
};
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
					return item.dL ? $elm$core$Maybe$Just(index) : $elm$core$Maybe$Nothing;
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
		if (!value.$) {
			return value;
		} else {
			return fallback;
		}
	});
var $author$project$Menu$navigate = F2(
	function (direction, menu) {
		var enabled = $author$project$Menu$enabledIndices(menu.dX);
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
					var _v1 = menu.eb;
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
					var _v2 = menu.eb;
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
			{eb: selected});
	});
var $author$project$Menu$outputTuple = function (_v0) {
	var value = _v0;
	return _Utils_Tuple2(value.m, value.d2);
};
var $author$project$Menu$sameTarget = F2(
	function (_v0, _v1) {
		var left = _v0;
		var right = _v1;
		return _Utils_eq(left.ed, right.ed);
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
					if (A2($elm$core$List$member, item.dB, seen)) {
						return false;
					} else {
						var $temp$remaining = rest,
							$temp$seen = A2($elm$core$List$cons, item.dB, seen);
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
				$elm$core$String$length(item.cZ),
				$author$project$Menu$maxLabel) < 1) && (!$elm$core$String$isEmpty(
				$elm$core$String$trim(item.cZ)));
		},
		items) && A2(uniqueActions, items, _List_Nil));
};
var $author$project$Menu$update = F2(
	function (message, model) {
		var state = model;
		var valid = function (target) {
			return (!A2($elm$core$List$member, target, state.ao)) && (!A2(
				$elm$core$List$member,
				$author$project$Menu$outputTuple(target),
				state.at));
		};
		var unchanged = _Utils_Tuple2(model, _List_Nil);
		var editMenu = F2(
			function (id, transform) {
				var _v8 = state.aq;
				if (!_v8.$) {
					var menu = _v8.a;
					return _Utils_eq(menu.bu, id) ? _Utils_Tuple2(
						_Utils_update(
							state,
							{
								aq: transform(menu)
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
				if (state.Z || ((!valid(target)) || ((!$author$project$Menu$validItems(items)) || (state.bB > 2147483647)))) {
					return unchanged;
				} else {
					var status = function () {
						var _v1 = $elm$core$List$head(
							A2(
								$elm$core$List$filter,
								function (entry) {
									return A2($author$project$Menu$sameTarget, entry.d, target);
								},
								state.d3));
						if (_v1.$ === 1) {
							return $author$project$Menu$Ready;
						} else {
							var entry = _v1.a;
							return entry.aQ ? $author$project$Menu$Unknown(entry.bu) : $author$project$Menu$Pending(entry.bu);
						}
					}();
					var menu = {
						d: target,
						bu: state.bB,
						dX: items,
						eb: $elm$core$List$head(
							$author$project$Menu$enabledIndices(items)),
						cx: status
					};
					return _Utils_Tuple2(
						_Utils_update(
							state,
							{
								aq: $elm$core$Maybe$Just(menu),
								bB: state.bB + 1
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
						if (_Utils_eq(menu.d, target) && valid(target)) {
							var _v2 = A2($author$project$Menu$itemAt, index, menu.dX);
							if (!_v2.$) {
								var item = _v2.a;
								return item.dL ? $elm$core$Maybe$Just(
									_Utils_update(
										menu,
										{
											eb: $elm$core$Maybe$Just(index)
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
				var _v3 = state.aq;
				if (_v3.$ === 1) {
					return unchanged;
				} else {
					var menu = _v3.a;
					if (state.Z || ((!_Utils_eq(menu.bu, id)) || ((!_Utils_eq(menu.d, target)) || ((!valid(target)) || (state.bA > 2147483647))))) {
						return unchanged;
					} else {
						if (A2(
							$elm$core$List$any,
							function (entry) {
								return A2($author$project$Menu$sameTarget, entry.d, target);
							},
							state.d3)) {
							return unchanged;
						} else {
							var _v4 = A2($author$project$Menu$itemAt, index, menu.dX);
							if (!_v4.$) {
								var item = _v4.a;
								if (item.dL && (_Utils_cmp(
									$elm$core$List$length(state.d3),
									$author$project$Menu$maxOutstanding) > -1)) {
									return _Utils_Tuple2(
										_Utils_update(
											state,
											{
												aq: $elm$core$Maybe$Just(
													_Utils_update(
														menu,
														{
															cx: $author$project$Menu$Refused('Outstanding operation limit reached; reconcile existing requests.')
														}))
											}),
										_List_Nil);
								} else {
									if (item.dL) {
										var intent = state.bA;
										var entry = {d: target, bu: intent, aQ: false};
										return _Utils_Tuple2(
											_Utils_update(
												state,
												{
													aq: $elm$core$Maybe$Just(
														_Utils_update(
															menu,
															{
																eb: $elm$core$Maybe$Just(index),
																cx: $author$project$Menu$Pending(intent)
															})),
													bA: state.bA + 1,
													d3: A2($elm$core$List$cons, entry, state.d3)
												}),
											_List_fromArray(
												[
													A3($author$project$Menu$Dispatch, intent, target, item.dB)
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
							return _Utils_eq(entry.bu, intent) && _Utils_eq(entry.d, receiptBinding);
						},
						state.d3));
				if (_v5.$ === 1) {
					return unchanged;
				} else {
					var entry = _v5.a;
					var outcome = $author$project$Menu$boundedOutcome(receivedOutcome);
					var outstanding = _Utils_eq(outcome, $author$project$Menu$Uncertain) ? A2(
						$elm$core$List$map,
						function (current) {
							return _Utils_eq(current.bu, intent) ? _Utils_update(
								current,
								{aQ: true}) : current;
						},
						state.d3) : A2(
						$elm$core$List$filter,
						function (current) {
							return !_Utils_eq(current.bu, intent);
						},
						state.d3);
					var menu = A2(
						$elm$core$Maybe$andThen,
						function (current) {
							if (!A2($author$project$Menu$awaits, intent, current.cx)) {
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
													cx: $author$project$Menu$Refused(reason)
												}));
									case 2:
										return $elm$core$Maybe$Just(
											_Utils_update(
												current,
												{cx: $author$project$Menu$Cancelled}));
									default:
										return $elm$core$Maybe$Just(
											_Utils_update(
												current,
												{
													cx: $author$project$Menu$Unknown(intent)
												}));
								}
							}
						},
						state.aq);
					return _Utils_Tuple2(
						_Utils_update(
							state,
							{
								bw: $elm$core$Maybe$Just(
									_Utils_Tuple2(intent, outcome)),
								aq: menu,
								d3: outstanding
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
				if (A2($elm$core$List$member, target, state.ao) || state.Z) {
					return unchanged;
				} else {
					if (_Utils_cmp(
						$elm$core$List$length(state.ao) + $elm$core$List$length(state.at),
						$author$project$Menu$maxRetired) > -1) {
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{Z: true, aq: $elm$core$Maybe$Nothing}),
							_List_Nil);
					} else {
						var menu = A2(
							$elm$core$Maybe$andThen,
							function (current) {
								return _Utils_eq(current.d, target) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(current);
							},
							state.aq);
						var invalidated = A2($elm$core$List$cons, target, state.ao);
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{ao: invalidated, aq: menu}),
							_List_Nil);
					}
				}
			default:
				var output = message.a;
				var generation = message.b;
				var retired = _Utils_Tuple2(output, generation);
				if (A2($elm$core$List$member, retired, state.at) || state.Z) {
					return unchanged;
				} else {
					if (_Utils_cmp(
						$elm$core$List$length(state.ao) + $elm$core$List$length(state.at),
						$author$project$Menu$maxRetired) > -1) {
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{Z: true, aq: $elm$core$Maybe$Nothing}),
							_List_Nil);
					} else {
						var retiredOutputs = A2($elm$core$List$cons, retired, state.at);
						var menu = A2(
							$elm$core$Maybe$andThen,
							function (current) {
								return _Utils_eq(
									$author$project$Menu$outputTuple(current.d),
									retired) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(current);
							},
							state.aq);
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{aq: menu, at: retiredOutputs}),
							_List_Nil);
					}
				}
		}
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
			state.aq);
		var menu = _v1.a;
		return _Utils_update(
			state,
			{aq: menu});
	});
var $author$project$Shell$Reconciling = 1;
var $author$project$Shell$Send = function (a) {
	return {$: 0, a: a};
};
var $author$project$Shell$refresh = function (model) {
	var _v0 = _Utils_Tuple2(
		model.d,
		$author$project$UInt64$next(model.o));
	if ((!_v0.a.$) && (!_v0.b.$)) {
		var binding = _v0.a.a;
		var request = _v0.b.a;
		return ((!model.G) || model.H) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
			_Utils_update(
				model,
				{
					n: $elm$core$Maybe$Just(request),
					G: 1,
					as: false,
					o: request
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
				{n: $elm$core$Maybe$Nothing, d_: 'Restart the shell to continue.', G: 3, as: false}),
			_List_Nil);
	}
};
var $author$project$Shell$geometryRequest = F2(
	function (attach, model) {
		if (model.H) {
			return _Utils_Tuple2(model, _List_Nil);
		} else {
			var _v0 = _Utils_Tuple2(
				model.d,
				$author$project$UInt64$next(model.o));
			if ((!_v0.a.$) && (!_v0.b.$)) {
				var binding = _v0.a.a;
				var request = _v0.b.a;
				if ((!model.G) || ((attach && (!_Utils_eq(model.cQ, $elm$core$Maybe$Nothing))) || ((!attach) && (_Utils_eq(model.cR, $elm$core$Maybe$Nothing) || (!_Utils_eq(model.dQ, $elm$core$Maybe$Nothing)))))) {
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
													return $.dm;
												},
												$author$project$UInt64$string),
											model.ad))))
							]));
					return _Utils_Tuple2(
						_Utils_update(
							model,
							{
								Q: attach || model.Q,
								cQ: attach ? $elm$core$Maybe$Just(request) : model.cQ,
								dQ: attach ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(request),
								o: request
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
				return $.R;
			},
			model.cR));
};
var $author$project$Shell$refreshObservations = function (model) {
	if (model.H) {
		return _Utils_Tuple2(model, _List_Nil);
	} else {
		var _v0 = $author$project$Shell$refresh(
			_Utils_update(
				model,
				{_: false}));
		var legacy = _v0.a;
		var commands = _v0.b;
		if (legacy.Q) {
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
	return model.as ? (((!model.G) || ((model.G === 3) || _Utils_eq(model.d, $elm$core$Maybe$Nothing))) ? _Utils_Tuple2(
		_Utils_update(
			model,
			{as: false}),
		_List_Nil) : ((model.H || (model.cH || ($author$project$Effects$pending(model.R) || ((!_Utils_eq(model.n, $elm$core$Maybe$Nothing)) || (!_Utils_eq(model.cQ, $elm$core$Maybe$Nothing)))))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$refresh(model))) : (((!model.H) && ((!model.cH) && (model._ && ((model.G === 2) && ((!$author$project$Effects$pending(model.R)) && (_Utils_eq(model.n, $elm$core$Maybe$Nothing) && (_Utils_eq(model.dQ, $elm$core$Maybe$Nothing) && _Utils_eq(model.cQ, $elm$core$Maybe$Nothing)))))))) ? $author$project$Shell$refreshObservations(model) : _Utils_Tuple2(model, _List_Nil));
};
var $author$project$Shell$resumeNotifications = function (model) {
	return $author$project$Shell$drainNotifications(
		_Utils_update(
			model,
			{cH: false}));
};
var $author$project$MenuBridge$cancelPrepared = F3(
	function (reason, shell, model) {
		var state = model;
		var _v0 = state.u;
		if (_v0.$ === 1) {
			return A4($author$project$MenuBridge$answer, model, shell, _List_Nil, $elm$core$Maybe$Nothing);
		} else {
			var slot = _v0.a;
			var cleared = A4(
				$author$project$MenuBridge$refuse,
				slot.by,
				slot.a8,
				reason,
				_Utils_update(
					state,
					{u: $elm$core$Maybe$Nothing}));
			var _v1 = $author$project$Shell$resumeNotifications(shell);
			var resumed = _v1.a;
			var effects = _v1.b;
			return A4(
				$author$project$MenuBridge$answer,
				cleared,
				resumed,
				effects,
				$elm$core$Maybe$Just(reason));
		}
	});
var $author$project$Shell$captureGeometry = function (model) {
	return A2(
		$elm$core$Maybe$map,
		function (observed) {
			return A3($author$project$Shell$Stamp, observed.d, observed.A.m, observed.A.dj);
		},
		model.ad);
};
var $author$project$Provider$geometryObservation = function (_v0) {
	var state = _v0;
	return state.ad;
};
var $author$project$Provider$nativeBinding = function (_v0) {
	var value = _v0;
	return value.A.c2;
};
var $author$project$Provider$nativeContext = function (_v0) {
	var value = _v0;
	return {dM: value.A.cO, dY: value.A.dY, m: value.A.d2, dj: value.A.dj};
};
var $author$project$MenuBridge$compatiblePrepared = F2(
	function (slot, shell) {
		var original = slot.X.bF;
		var sameGeometry = function () {
			var _v0 = _Utils_Tuple2(
				$author$project$Provider$geometryObservation(original),
				shell.ad);
			if (_v0.a.$ === 1) {
				var _v1 = _v0.a;
				return _Utils_eq(slot.aF, $elm$core$Maybe$Nothing);
			} else {
				if (!_v0.b.$) {
					var before = _v0.a.a;
					var after = _v0.b.a;
					return _Utils_eq(before.d, after.d) && (_Utils_eq(before.A.dY, after.A.dY) && (_Utils_eq(before.A.dM, after.A.dM) && (_Utils_eq(before.A.m, after.A.m) && ((!(!A2($author$project$UInt64$compare, after.A.dj, before.A.dj))) && ((!(!A2($author$project$UInt64$compare, after.dm, before.dm))) && ((!after.dE) && _Utils_eq(before.a, after.a)))))));
				} else {
					return false;
				}
			}
		}();
		var old = $author$project$Provider$nativeContext(original);
		var legacy = shell.R.aa;
		var sameLegacy = A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (observed) {
					return _Utils_eq(observed.A.dY, old.dY) && (_Utils_eq(observed.A.dM, old.dM) && (_Utils_eq(observed.A.m, old.m) && ((!(!A2($author$project$UInt64$compare, observed.A.dj, old.dj))) && (_Utils_eq(
						$author$project$ActionProjection$windows(observed.dk),
						slot.ci) && _Utils_eq(
						A2(
							$author$project$ActionProjection$rootOf,
							$author$project$Provider$incarnation(original),
							observed.dk),
						$elm$core$Maybe$Just(
							$author$project$Provider$incarnation(original)))))));
				},
				legacy));
		return _Utils_eq(
			shell.d,
			$elm$core$Maybe$Just(
				$author$project$Provider$nativeBinding(original))) && (_Utils_eq(shell.cR, slot.cR) && (sameLegacy && sameGeometry));
	});
var $author$project$NativeProvider$counter = A2($elm$core$Basics$composeR, $author$project$UInt64$string, $elm$json$Json$Encode$string);
var $author$project$Provider$Raw = F7(
	function (provider, capabilitiesGeneration, context, target, heading, capabilities, entries) {
		return {bP: capabilities, cc: capabilitiesGeneration, A: context, bp: entries, cT: heading, a_: provider, ed: target};
	});
var $author$project$Provider$Snapshot = $elm$core$Basics$identity;
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
		return {cO: frontend, dY: lifetime, c2: _native, d2: outputGeneration, cn: outputId, dj: revision, b4: session};
	});
var $elm$json$Json$Decode$map7 = _Json_map7;
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
					bu: $author$project$UInt64$string(identity),
					bv: {dB: action, dL: enabled, cZ: label},
					cX: kind
				};
			}),
		A2($elm$json$Json$Decode$field, 'id', $author$project$Provider$nonzero),
		A2($elm$json$Json$Decode$field, 'label', $author$project$Provider$textDecoder),
		A2($elm$json$Json$Decode$field, 'enabled', $elm$json$Json$Decode$bool),
		A2($elm$json$Json$Decode$field, 'action', $author$project$Provider$actionDecoder)));
var $elm$core$Set$Set_elm_builtin = $elm$core$Basics$identity;
var $elm$core$Set$empty = $elm$core$Dict$empty;
var $elm$core$Set$insert = F2(
	function (key, _v0) {
		var dict = _v0;
		return A3($elm$core$Dict$insert, key, 0, dict);
	});
var $elm$core$Set$fromList = function (list) {
	return A3($elm$core$List$foldl, $elm$core$Set$insert, $elm$core$Set$empty, list);
};
var $author$project$Menu$OutputId = $elm$core$Basics$identity;
var $author$project$Menu$outputId = $elm$core$Basics$identity;
var $elm$core$Set$size = function (_v0) {
	var dict = _v0;
	return $elm$core$Dict$size(dict);
};
var $author$project$Provider$Target = F3(
	function (lifetime, session, incarnation) {
		return {U: incarnation, dY: lifetime, b4: session};
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
					return entry.bv.dL && (!A2($elm$core$List$member, entry.cX, raw.bP));
				},
				raw.bp);
			var identities = A2(
				$elm$core$List$map,
				function ($) {
					return $.bu;
				},
				raw.bp);
			var duplicateIds = !_Utils_eq(
				$elm$core$List$length(identities),
				$elm$core$Set$size(
					$elm$core$Set$fromList(identities)));
			var duplicateCapabilities = !_Utils_eq(
				$elm$core$List$length(raw.bP),
				$elm$core$Set$size(
					$elm$core$Set$fromList(raw.bP)));
			var coherent = _Utils_eq(raw.ed.dY, raw.A.dY) && _Utils_eq(raw.ed.b4, raw.A.b4);
			var authority = A2(
				$elm$json$Json$Encode$encode,
				0,
				A2(
					$elm$json$Json$Encode$list,
					$elm$core$Basics$identity,
					_List_fromArray(
						[
							$author$project$Binding$encode(raw.A.c2),
							$elm$json$Json$Encode$string(
							$author$project$UInt64$string(raw.a_)),
							$elm$json$Json$Encode$string(
							$author$project$UInt64$string(raw.cc))
						])));
			var actions = A2(
				$elm$core$List$map,
				A2(
					$elm$core$Basics$composeR,
					function ($) {
						return $.bv;
					},
					function ($) {
						return $.dB;
					}),
				raw.bp);
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
					d: $author$project$Menu$binding(
						{
							cB: authority,
							m: $author$project$Menu$outputId(
								$author$project$UInt64$string(raw.A.cn)),
							d2: $author$project$UInt64$string(raw.A.d2),
							dj: $author$project$UInt64$string(raw.A.dj),
							ed: $author$project$Menu$Window(
								A2(
									$author$project$Menu$windowId,
									$author$project$Binding$authorityIdentity(raw.A.c2),
									$author$project$UInt64$string(raw.ed.U)))
						}),
					dG: raw.cc,
					A: raw.A,
					ad: $elm$core$Maybe$Nothing,
					U: raw.ed.U,
					dX: A2(
						$elm$core$List$map,
						function ($) {
							return $.bv;
						},
						raw.bp),
					cr: raw.a_,
					dr: raw.cT
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
		if (_Utils_eq(scope.cn, $author$project$UInt64$zero) || (_Utils_eq(scope.cr, $author$project$UInt64$zero) || _Utils_eq(scope.dG, $author$project$UInt64$zero))) {
			return $elm$core$Result$Err('Missing registered provider/output identity');
		} else {
			if (shell.G !== 2) {
				return $elm$core$Result$Err('Native window facts are not ready');
			} else {
				var _v0 = _Utils_Tuple2(shell.d, shell.R.aa);
				if ((!_v0.a.$) && (!_v0.b.$)) {
					var binding = _v0.a.a;
					var observed = _v0.b.a;
					if (!A3($author$project$Binding$matchesContext, observed.A.dY, observed.A.dM, binding)) {
						return $elm$core$Result$Err('Native observation binding mismatch');
					} else {
						var _v1 = A2(
							$elm$core$Maybe$andThen,
							function (root) {
								return $elm$core$List$head(
									A2(
										$elm$core$List$filter,
										function (window) {
											return _Utils_eq(window.U, root);
										},
										$author$project$ActionProjection$windows(observed.dk)));
							},
							A2($author$project$ActionProjection$rootOf, incarnation, observed.dk));
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
												$author$project$NativeProvider$counter(scope.cr)),
												_Utils_Tuple2(
												'capabilityGeneration',
												$author$project$NativeProvider$counter(scope.dG)),
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
															$author$project$NativeProvider$counter(observed.A.dj)),
															_Utils_Tuple2(
															'outputId',
															$author$project$NativeProvider$counter(scope.cn)),
															_Utils_Tuple2(
															'outputGeneration',
															$author$project$NativeProvider$counter(observed.A.m))
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
															$author$project$NativeProvider$counter(window.U))
														]))),
												_Utils_Tuple2(
												'title',
												$elm$json$Json$Encode$string(
													($elm$core$String$trim(window.cZ) === '') ? 'Window actions' : window.cZ)),
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
															A4(item, '1', 'Restore', window.ca && window.a7, 'Restore'),
															A4(item, '2', 'Minimize', window.ca && (!window.a7), 'Minimize')
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
					return _Utils_eq(w.U, identity);
				},
				rows));
	});
var $author$project$ActionProjection$minimized = F2(
	function (identity, projection) {
		return A2(
			$elm$core$Maybe$map,
			function ($) {
				return $.a7;
			},
			A2(
				$author$project$ActionProjection$find,
				identity,
				$author$project$ActionProjection$windows(projection)));
	});
var $author$project$GeometryProjection$Maximized = 1;
var $author$project$Provider$withGeometry = F3(
	function (caps, observed, snapshot) {
		var state = snapshot;
		if ((!_Utils_eq(observed.d, state.A.c2)) || (!_Utils_eq(observed.A.m, state.A.d2))) {
			return $elm$core$Result$Err('Geometry/legacy authority mismatch');
		} else {
			var _v0 = A2($author$project$GeometryProjection$window, state.U, observed);
			if (_v0.$ === 1) {
				return $elm$core$Result$Err('Geometry target missing');
			} else {
				var window = _v0.a;
				var supported = function (op) {
					return caps.R && A2($elm$core$List$member, op, caps.d1);
				};
				var restoreGeometry = supported('restore-geometry') && (!window.a7);
				var ready = A2(
					$elm$core$List$any,
					function ($) {
						return $.dL;
					},
					state.dX) && ((!observed.dE) && (window.dK && (!window.dO)));
				var legacyRestore = $elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (item) {
							return _Utils_eq(item.dB, $author$project$Menu$Restore);
						},
						state.dX));
				var restore = restoreGeometry ? {dB: $author$project$Menu$RestoreGeometry, dL: ready && (window.d7 && ((window.c3 === 1) && window.d5)), cZ: 'Restore'} : A2(
					$elm$core$Maybe$withDefault,
					{dB: $author$project$Menu$Restore, dL: false, cZ: 'Restore'},
					legacyRestore);
				var legacyMinimize = $elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (item) {
							return _Utils_eq(item.dB, $author$project$Menu$Minimize);
						},
						state.dX));
				var minimize = A2(
					$elm$core$Maybe$withDefault,
					{dB: $author$project$Menu$Minimize, dL: false, cZ: 'Minimize'},
					legacyMinimize);
				var items = _Utils_ap(
					_List_fromArray(
						[restore, minimize]),
					supported('maximize') ? _List_fromArray(
						[
							{dB: $author$project$Menu$Maximize, dL: ready && (window.dZ && ((!window.a7) && (!window.c3))), cZ: 'Maximize'}
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
									$author$project$Binding$encode(state.A.c2)) + (':' + ($author$project$UInt64$string(state.cr) + (':' + ($author$project$UInt64$string(state.dG) + (':' + $author$project$UInt64$string(state.A.dj))))))),
								$elm$json$Json$Encode$string(
								$author$project$UInt64$string(observed.A.dj)),
								$elm$json$Json$Encode$string(
								$author$project$UInt64$string(observed.A.m)),
								A2($elm$json$Json$Encode$list, $elm$json$Json$Encode$string, caps.d1)
							])));
				return $elm$core$Result$Ok(
					_Utils_update(
						state,
						{
							d: $author$project$Menu$binding(
								{
									cB: authority,
									m: $author$project$Menu$outputId(
										$author$project$UInt64$string(state.A.cn)),
									d2: $author$project$UInt64$string(observed.A.m),
									dj: $author$project$UInt64$string(observed.A.dj),
									ed: $author$project$Menu$Window(
										A2(
											$author$project$Menu$windowId,
											$author$project$Binding$authorityIdentity(state.A.c2),
											$author$project$UInt64$string(state.U)))
								}),
							ad: $elm$core$Maybe$Just(observed),
							dX: items
						}));
			}
		}
	});
var $author$project$NativeProvider$fromShell = F3(
	function (scope, incarnation, shell) {
		return A2(
			$elm$core$Result$andThen,
			function (legacy) {
				var _v0 = shell.cR;
				if (_v0.$ === 1) {
					return $elm$core$Result$Ok(legacy);
				} else {
					var caps = _v0.a;
					if (!caps.R) {
						return $elm$core$Result$Ok(legacy);
					} else {
						var _v1 = _Utils_Tuple3(shell.ad, shell.dQ, shell.R.aa);
						if (((!_v1.a.$) && (_v1.b.$ === 1)) && (!_v1.c.$)) {
							var observed = _v1.a.a;
							var _v2 = _v1.b;
							var legacyObserved = _v1.c.a;
							var root = $author$project$Provider$incarnation(legacy);
							var legacyMinimized = A2($author$project$ActionProjection$minimized, root, legacyObserved.dk);
							var geometryMinimized = A2(
								$elm$core$Maybe$map,
								function ($) {
									return $.a7;
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
var $author$project$Effects$Maximize = {$: 3};
var $author$project$Effects$RestoreGeometry = {$: 4};
var $author$project$MenuBridge$operation = function (action) {
	switch (action.$) {
		case 4:
			return $elm$core$Maybe$Just($author$project$Effects$Minimize);
		case 0:
			return $elm$core$Maybe$Just($author$project$Effects$Restore);
		case 5:
			return $elm$core$Maybe$Just($author$project$Effects$Maximize);
		case 1:
			return $elm$core$Maybe$Just($author$project$Effects$RestoreGeometry);
		default:
			return $elm$core$Maybe$Nothing;
	}
};
var $author$project$Provider$presentationScope = function (_v0) {
	var value = _v0;
	return {cn: value.A.cn, cr: value.cr};
};
var $author$project$Provider$getBinding = function (_v0) {
	var value = _v0;
	return value.d;
};
var $author$project$Provider$getItems = function (_v0) {
	var value = _v0;
	return value.dX;
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
var $author$project$ReceiptRouter$Maximize = 2;
var $author$project$ReceiptRouter$Minimize = 0;
var $author$project$ReceiptRouter$Restore = 1;
var $author$project$ReceiptRouter$RestoreGeometry = 3;
var $author$project$Provider$actionContext = F2(
	function (action, snapshot) {
		var state = snapshot;
		return ($author$project$Provider$actionProtocol(action) === 2) ? A2(
			$elm$core$Maybe$withDefault,
			$author$project$Provider$nativeContext(snapshot),
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.A;
				},
				state.ad)) : $author$project$Provider$nativeContext(snapshot);
	});
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
		return {K: intent, c2: _native, b_: protocol};
	});
var $author$project$ReceiptRouter$Intent = F5(
	function (request, generation, incarnation, operation, context) {
		return {A: context, dP: generation, U: incarnation, aK: operation, o: request};
	});
var $author$project$ReceiptRouter$Context = F4(
	function (lifetime, epoch, output, revision) {
		return {dM: epoch, dY: lifetime, m: output, dj: revision};
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
var $elm$json$Json$Decode$map5 = _Json_map5;
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
			value.b_,
			((value.K.aK === 2) || (value.K.aK === 3)) ? 2 : 1) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Operation protocol mismatch');
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
					return item.dL && _Utils_eq(item.dB, action);
				},
				$author$project$Provider$getItems(provider));
			return ((!_Utils_eq(
				binding,
				$author$project$Provider$getBinding(provider))) || ((!eligible) || ((!_Utils_eq(
				$elm$core$Maybe$Just(_native.K.aK),
				expectedOperation)) || ((!_Utils_eq(
				_native.c2,
				$author$project$Provider$nativeBinding(provider))) || ((!_Utils_eq(
				_native.K.A,
				A2($author$project$Provider$actionContext, action, provider))) || ((!_Utils_eq(
				_native.b_,
				$author$project$Provider$actionProtocol(action))) || (!_Utils_eq(
				_native.K.U,
				$author$project$Provider$incarnation(provider))))))))) ? $elm$core$Result$Err('Native command does not match frozen menu action') : (A2(
				$elm$core$List$any,
				function (entry) {
					return _Utils_eq(entry.by, local) || (_Utils_eq(entry.ap, _native) || (_Utils_eq(entry.ap.c2, _native.c2) && _Utils_eq(entry.ap.K.o, _native.K.o)));
				},
				entries) ? $elm$core$Result$Err('Native/local operation already registered') : ((_Utils_cmp(
				$elm$core$List$length(entries),
				$author$project$Menu$maxOutstanding) > -1) ? $elm$core$Result$Err('Receipt registry capacity') : $elm$core$Result$Ok(
				A2(
					$elm$core$List$cons,
					{d: binding, ap: _native, by: local},
					entries))));
		}
	});
var $author$project$ReceiptRouter$registerPrepared = F5(
	function (_v0, original, fresh, value, model) {
		var local = _v0.a;
		var originalBinding = _v0.b;
		var action = _v0.c;
		var old = $author$project$Provider$nativeContext(original);
		var _new = $author$project$Provider$nativeContext(fresh);
		var geometrySame = function () {
			var _v2 = _Utils_Tuple2(
				$author$project$Provider$geometryObservation(original),
				$author$project$Provider$geometryObservation(fresh));
			_v2$2:
			while (true) {
				if (_v2.a.$ === 1) {
					if (_v2.b.$ === 1) {
						var _v3 = _v2.a;
						var _v4 = _v2.b;
						return true;
					} else {
						break _v2$2;
					}
				} else {
					if (!_v2.b.$) {
						var before = _v2.a.a;
						var after = _v2.b.a;
						return _Utils_eq(before.a, after.a) && ((!after.dE) && (_Utils_eq(before.A.m, after.A.m) && (_Utils_eq(before.d, after.d) && ((!(!A2($author$project$UInt64$compare, after.A.dj, before.A.dj))) && (!(!A2($author$project$UInt64$compare, after.dm, before.dm)))))));
					} else {
						break _v2$2;
					}
				}
			}
			return false;
		}();
		return ((!_Utils_eq(
			originalBinding,
			$author$project$Provider$getBinding(original))) || ((!_Utils_eq(
			$author$project$Provider$nativeBinding(original),
			$author$project$Provider$nativeBinding(fresh))) || ((!_Utils_eq(
			$author$project$Provider$incarnation(original),
			$author$project$Provider$incarnation(fresh))) || ((!_Utils_eq(
			$author$project$Provider$presentationScope(original),
			$author$project$Provider$presentationScope(fresh))) || ((!_Utils_eq(old.dY, _new.dY)) || ((!_Utils_eq(old.dM, _new.dM)) || ((!_Utils_eq(old.m, _new.m)) || ((!A2($author$project$UInt64$compare, _new.dj, old.dj)) || ((!geometrySame) || (!_Utils_eq(
			$author$project$Provider$getItems(original),
			$author$project$Provider$getItems(fresh)))))))))))) ? $elm$core$Result$Err('Prepared action authority changed') : A2(
			$elm$core$Result$map,
			function (_v1) {
				var entries = _v1;
				return A2(
					$elm$core$List$map,
					function (entry) {
						return _Utils_eq(entry.by, local) ? _Utils_update(
							entry,
							{d: originalBinding}) : entry;
					},
					entries);
			},
			A4(
				$author$project$ReceiptRouter$register,
				A3(
					$author$project$Menu$Dispatch,
					local,
					$author$project$Provider$getBinding(fresh),
					action),
				fresh,
				value,
				model));
	});
var $author$project$Shell$RestartBackend = {$: 1};
var $author$project$ActionProjection$actionable = F2(
	function (identity, projection) {
		return A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.ca;
				},
				A2(
					$author$project$ActionProjection$find,
					identity,
					$author$project$ActionProjection$windows(projection))));
	});
var $author$project$Effects$Context = F4(
	function (lifetime, epoch, output, revision) {
		return {dM: epoch, dY: lifetime, m: output, dj: revision};
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
		return {b9: application, ca: available, U: incarnation, cZ: label, a7: minimized, co: owner};
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
				var _v0 = w.co;
				if (_v0.$ === 1) {
					return $elm$core$Maybe$Just(w.U);
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
									return !w.a7;
								},
								A2($author$project$ActionProjection$find, identity, rows)));
					},
					focus));
			var unique = A3(
				$elm$core$List$foldl,
				F2(
					function (w, seen) {
						return A2($elm$core$List$member, w.U, seen) ? seen : A2($elm$core$List$cons, w.U, seen);
					}),
				_List_Nil,
				rows);
			var table = $elm$core$Dict$fromList(
				A2(
					$elm$core$List$map,
					function (w) {
						return _Utils_Tuple2(
							$author$project$UInt64$string(w.U),
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
										$author$project$UInt64$string(w.U),
										root,
										cache);
								}),
							accumulated,
							A3($author$project$ActionProjection$rootIn, 256, w.U, table));
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
							return _Utils_eq(root.a7, w.a7);
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
									$author$project$UInt64$string(w.U)),
								roots))));
			};
			if ((!_Utils_eq(
				$elm$core$List$length(unique),
				$elm$core$List$length(rows))) || ((!validFocus) || A2(
				$elm$core$List$any,
				function (w) {
					return !($author$project$ActionProjection$validText(w.cZ) && ($author$project$ActionProjection$validText(w.b9) && validFamily(w)));
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
var $author$project$Effects$counter = A2($elm$core$Basics$composeR, $author$project$UInt64$string, $elm$json$Json$Encode$string);
var $author$project$Effects$encodeContext = function (context) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'lifetime',
				$author$project$Effects$counter(context.dY)),
				_Utils_Tuple2(
				'epoch',
				$author$project$Effects$counter(context.dM)),
				_Utils_Tuple2(
				'output',
				$author$project$Effects$counter(context.m)),
				_Utils_Tuple2(
				'revision',
				$author$project$Effects$counter(context.dj))
			]));
};
var $elm$json$Json$Encode$float = _Json_wrap;
var $author$project$Snap$encodeProposal = function (proposed) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'region',
				$elm$json$Json$Encode$string(proposed.bE)),
				_Utils_Tuple2(
				'geometry',
				A2($elm$json$Json$Encode$list, $elm$json$Json$Encode$float, proposed.ad)),
				_Utils_Tuple2(
				'monitor',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(proposed.bz))),
				_Utils_Tuple2(
				'outputOwnershipGeneration',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(proposed.aL))),
				_Utils_Tuple2(
				'workAreaRevision',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(proposed.bM))),
				_Utils_Tuple2(
				'workspaceGeneration',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(proposed.bl)))
			]));
};
var $author$project$Effects$operationName = function (operation) {
	switch (operation.$) {
		case 0:
			return 'minimize';
		case 1:
			return 'restore';
		case 2:
			return 'activate';
		case 3:
			return 'maximize';
		case 4:
			return 'restore-geometry';
		default:
			return 'snap';
	}
};
var $author$project$Effects$encodeIntent = function (intent) {
	return $elm$json$Json$Encode$object(
		_Utils_ap(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'request',
					$author$project$Effects$counter(intent.o)),
					_Utils_Tuple2(
					'generation',
					$author$project$Effects$counter(intent.dP)),
					_Utils_Tuple2(
					'incarnation',
					$author$project$Effects$counter(intent.U)),
					_Utils_Tuple2(
					'operation',
					$elm$json$Json$Encode$string(
						$author$project$Effects$operationName(intent.aK))),
					_Utils_Tuple2(
					'context',
					$author$project$Effects$encodeContext(intent.A))
				]),
			function () {
				var _v0 = intent.aK;
				if (_v0.$ === 5) {
					var proposed = _v0.a;
					return _List_fromArray(
						[
							_Utils_Tuple2(
							'placement',
							$author$project$Snap$encodeProposal(proposed))
						]);
				} else {
					return _List_Nil;
				}
			}()));
};
var $author$project$Effects$Intent = F5(
	function (request, generation, incarnation, operation, context) {
		return {A: context, dP: generation, U: incarnation, aK: operation, o: request};
	});
var $author$project$Effects$SnapPlacement = function (a) {
	return {$: 5, a: a};
};
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
var $elm$core$Basics$abs = function (n) {
	return (n < 0) ? (-n) : n;
};
var $elm$json$Json$Decode$float = _Json_decodeFloat;
var $elm$core$Basics$isInfinite = _Basics_isInfinite;
var $elm$core$Basics$isNaN = _Basics_isNaN;
var $author$project$Snap$proposalDecoder = function (context) {
	var region = A2(
		$elm$json$Json$Decode$andThen,
		function (value) {
			return A2(
				$elm$core$List$any,
				A2(
					$elm$core$Basics$composeR,
					$author$project$Snap$identity,
					$elm$core$Basics$eq(value)),
				$author$project$Snap$regions) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Unsupported snap region');
		},
		$elm$json$Json$Decode$string);
	var rectangle = A2(
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
				return (A2(
					$elm$core$List$all,
					function (n) {
						return (!($elm$core$Basics$isNaN(n) || $elm$core$Basics$isInfinite(n))) && ($elm$core$Basics$abs(n) <= 2147483647);
					},
					values) && ((w > 0) && (h > 0))) ? $elm$json$Json$Decode$succeed(values) : $elm$json$Json$Decode$fail('Invalid snap rectangle');
			} else {
				return $elm$json$Json$Decode$fail('Invalid snap rectangle shape');
			}
		},
		$elm$json$Json$Decode$list($elm$json$Json$Decode$float));
	var positive = A2(
		$elm$json$Json$Decode$andThen,
		function (n) {
			return _Utils_eq(n, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero placement generation') : $elm$json$Json$Decode$succeed(n);
		},
		$author$project$UInt64$decoder);
	var fields = _List_fromArray(
		['region', 'geometry', 'monitor', 'outputOwnershipGeneration', 'workAreaRevision', 'workspaceGeneration']);
	return A2(
		$elm$json$Json$Decode$andThen,
		function (pairs) {
			return (!_Utils_eq(
				$elm$core$List$sort(
					A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
				$elm$core$List$sort(fields))) ? $elm$json$Json$Decode$fail('Snap placement fields') : A7(
				$elm$json$Json$Decode$map6,
				F6(
					function (regionName, geometry, monitor, output, area, workspace) {
						return {A: context, ad: geometry, bz: monitor, aL: output, bE: regionName, bM: area, bl: workspace};
					}),
				A2($elm$json$Json$Decode$field, 'region', region),
				A2($elm$json$Json$Decode$field, 'geometry', rectangle),
				A2($elm$json$Json$Decode$field, 'monitor', $author$project$UInt64$decoder),
				A2($elm$json$Json$Decode$field, 'outputOwnershipGeneration', positive),
				A2($elm$json$Json$Decode$field, 'workAreaRevision', positive),
				A2($elm$json$Json$Decode$field, 'workspaceGeneration', positive));
		},
		$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
};
var $author$project$Effects$intentDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (name) {
		return (name === 'snap') ? A2(
			$author$project$Effects$strict,
			_List_fromArray(
				['request', 'generation', 'incarnation', 'operation', 'context', 'placement']),
			A2(
				$elm$json$Json$Decode$andThen,
				function (context) {
					return A6(
						$elm$json$Json$Decode$map5,
						$author$project$Effects$Intent,
						A2($elm$json$Json$Decode$field, 'request', $author$project$Effects$identity),
						A2($elm$json$Json$Decode$field, 'generation', $author$project$Effects$identity),
						A2($elm$json$Json$Decode$field, 'incarnation', $author$project$Effects$identity),
						A2(
							$elm$json$Json$Decode$map,
							$author$project$Effects$SnapPlacement,
							A2(
								$elm$json$Json$Decode$field,
								'placement',
								$author$project$Snap$proposalDecoder(context))),
						$elm$json$Json$Decode$succeed(context));
				},
				A2($elm$json$Json$Decode$field, 'context', $author$project$Effects$contextDecoder))) : A2(
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
	},
	A2($elm$json$Json$Decode$field, 'operation', $elm$json$Json$Decode$string));
var $author$project$Effects$protocol = function (operation) {
	switch (operation.$) {
		case 3:
			return 2;
		case 4:
			return 2;
		case 5:
			return 2;
		default:
			return 1;
	}
};
var $author$project$ActionProjection$revision = function (_v0) {
	var value = _v0.a;
	return value;
};
var $author$project$Effects$sameAuthority = F2(
	function (a, b) {
		return _Utils_eq(a.dY, b.dY) && (_Utils_eq(a.dM, b.dM) && _Utils_eq(a.m, b.m));
	});
var $author$project$ActionProjection$sameState = F2(
	function (left, right) {
		var state = function (projection) {
			return A2(
				$elm$core$List$map,
				function (w) {
					return _Utils_Tuple3(
						w.U,
						_Utils_Tuple2(w.a7, w.co),
						_Utils_Tuple2(w.b9, w.ca));
				},
				A2(
					$elm$core$List$sortWith,
					F2(
						function (a, b) {
							return A2($author$project$UInt64$compare, a.U, b.U);
						}),
					$author$project$ActionProjection$windows(projection)));
		};
		return _Utils_eq(
			$author$project$ActionProjection$focused(left),
			$author$project$ActionProjection$focused(right)) && _Utils_eq(
			state(left),
			state(right));
	});
var $author$project$Effects$Committed = 1;
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
		return (!transaction.cx) ? _Utils_update(
			transaction,
			{cx: 4}) : transaction;
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
				if (_v11.$ === 1) {
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
									context.dj)) {
									return refuse('Scene/context revision mismatch');
								} else {
									var _v3 = model.aa;
									if (!_v3.$) {
										var old = _v3.a;
										return (A2($author$project$Effects$sameAuthority, old.A, context) && ((!A2($author$project$UInt64$compare, context.dj, old.A.dj)) || (_Utils_eq(context.dj, old.A.dj) && (!A2($author$project$ActionProjection$sameState, old.dk, scene))))) ? refuse('Nonincreasing snapshot') : _Utils_Tuple3(
											_Utils_update(
												model,
												{
													aD: true,
													aa: $elm$core$Maybe$Just(
														{A: context, dk: scene}),
													z: A2($author$project$Effects$sameAuthority, old.A, context) ? model.z : $author$project$Effects$unknown(model.z)
												}),
											$elm$core$Maybe$Nothing,
											$elm$core$Maybe$Nothing);
									} else {
										return _Utils_Tuple3(
											_Utils_update(
												model,
												{
													aD: true,
													aa: $elm$core$Maybe$Just(
														{A: context, dk: scene})
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
								model.aa,
								$author$project$UInt64$next(model.o),
								$author$project$UInt64$next(model.dP));
							if (((!_v5.a.$) && (!_v5.b.$)) && (!_v5.c.$)) {
								var observed = _v5.a.a;
								var request = _v5.b.a;
								var generation = _v5.c.a;
								if (!model.aD) {
									return refuse('Disconnected');
								} else {
									if ($author$project$Effects$pending(model)) {
										return refuse('Operation already pending');
									} else {
										if ($elm$core$List$length(model.l) >= 64) {
											return refuse('Unresolved operation capacity');
										} else {
											if ($author$project$Effects$protocol(operation) === 2) {
												return refuse('Geometry observation required');
											} else {
												if (A3($author$project$Effects$blocked, observed.A.dY, incarnation, model)) {
													return refuse('Unresolved native operation');
												} else {
													if (!A2($author$project$ActionProjection$actionable, incarnation, observed.dk)) {
														return refuse('Locked or unmapped target');
													} else {
														var _v6 = A2($author$project$ActionProjection$minimized, incarnation, observed.dk);
														if (_v6.$ === 1) {
															return refuse('Unknown incarnation');
														} else {
															var minimized = _v6.a;
															if ((_Utils_eq(operation, $author$project$Effects$Minimize) && minimized) || ((_Utils_eq(operation, $author$project$Effects$Restore) && (!minimized)) || (_Utils_eq(operation, $author$project$Effects$Activate) && minimized))) {
																return refuse('Already in requested native state');
															} else {
																var intent = {A: observed.A, dP: generation, U: incarnation, aK: operation, o: request};
																return _Utils_Tuple3(
																	_Utils_update(
																		model,
																		{
																			dP: generation,
																			o: request,
																			z: $elm$core$Maybe$Just(
																				{Y: 1, K: intent, cx: 0}),
																			l: A2(
																				$elm$core$List$cons,
																				{Y: 1, K: intent, cx: 0},
																				model.l)
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
								return _Utils_eq(t.Y, protocolId) && _Utils_eq(t.K, intent);
							};
							var found = A2($elm$core$List$any, exact, model.l);
							var settled = function (t) {
								return exact(t) ? _Utils_update(
									t,
									{cx: status}) : t;
							};
							var unresolved = (status === 4) ? A2($elm$core$List$map, settled, model.l) : A2(
								$elm$core$List$filter,
								A2($elm$core$Basics$composeR, exact, $elm$core$Basics$not),
								model.l);
							return ((!found) || ((!A2(
								$elm$core$List$member,
								protocolId,
								_List_fromArray(
									[1, 2]))) || (!_Utils_eq(
								$author$project$Effects$protocol(intent.aK),
								protocolId)))) ? refuse('Stale, mismatched or terminal receipt') : _Utils_Tuple3(
								_Utils_update(
									model,
									{
										z: A2(
											$elm$core$Maybe$map,
											function (t) {
												return A2(
													$elm$core$Maybe$withDefault,
													false,
													A2(
														$elm$core$Maybe$map,
														function (observed) {
															return A2($author$project$Effects$sameAuthority, observed.A, intent.A);
														},
														model.aa)) ? settled(t) : t;
											},
											model.z),
										l: unresolved
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
									return (!A2($author$project$UInt64$compare, old, _new)) ? _new : old;
								});
							return _Utils_Tuple3(
								_Utils_update(
									model,
									{
										dP: A2(maximum, model.dP, generation),
										o: A2(maximum, model.o, request)
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
								$author$project$Effects$protocol(intent.aK),
								protocolId))) {
								return refuse('Recovery operation protocol');
							} else {
								if (A2(
									$elm$core$List$any,
									function (t) {
										return _Utils_eq(t.K, intent) && _Utils_eq(t.Y, protocolId);
									},
									model.l)) {
									return _Utils_Tuple3(model, $elm$core$Maybe$Nothing, $elm$core$Maybe$Nothing);
								} else {
									if ($elm$core$List$length(model.l) >= 64) {
										return refuse('Unresolved operation capacity');
									} else {
										var transaction = {Y: protocolId, K: intent, cx: 4};
										var maximum = F2(
											function (old, _new) {
												return (!A2($author$project$UInt64$compare, old, _new)) ? _new : old;
											});
										return _Utils_Tuple3(
											_Utils_update(
												model,
												{
													dP: A2(maximum, model.dP, intent.dP),
													o: A2(maximum, model.o, intent.o),
													z: $elm$core$Maybe$Just(transaction),
													l: A2($elm$core$List$cons, transaction, model.l)
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
						function (_v10) {
							return _Utils_Tuple3(
								_Utils_update(
									model,
									{
										aD: false,
										z: $author$project$Effects$unknown(model.z),
										l: A2(
											$elm$core$List$map,
											function (t) {
												return (!t.cx) ? _Utils_update(
													t,
													{cx: 4}) : t;
											},
											model.l)
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
var $author$project$Snap$matches = F3(
	function (snapshot, target, proposed) {
		var _v0 = $elm$core$List$head(
			A2(
				$elm$core$List$filter,
				A2(
					$elm$core$Basics$composeR,
					$author$project$Snap$identity,
					$elm$core$Basics$eq(proposed.bE)),
				$author$project$Snap$regions));
		if (_v0.$ === 1) {
			return false;
		} else {
			var region = _v0.a;
			return A2(
				$elm$core$Maybe$withDefault,
				false,
				A2(
					$elm$core$Maybe$map,
					function (choice) {
						return _Utils_eq(
							$author$project$Snap$proposal(
								_Utils_update(
									choice,
									{eb: region})),
							$elm$core$Maybe$Just(proposed));
					},
					A2($author$project$Snap$open, snapshot, target)));
		}
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
					return A2($author$project$ActionProjection$actionable, incarnation, legacy.dk) && _Utils_eq(
						A2($author$project$ActionProjection$rootOf, incarnation, legacy.dk),
						$elm$core$Maybe$Just(incarnation));
				},
				model.aa));
		var _v0 = _Utils_Tuple3(
			A2($author$project$GeometryProjection$window, incarnation, observed),
			$author$project$UInt64$next(model.o),
			$author$project$UInt64$next(model.dP));
		if (((!_v0.a.$) && (!_v0.b.$)) && (!_v0.c.$)) {
			var window = _v0.a.a;
			var request = _v0.b.a;
			var generation = _v0.c.a;
			if ((!model.aD) || ((!legacyReady) || ($author$project$Effects$pending(model) || A3($author$project$Effects$blocked, observed.A.dY, incarnation, model)))) {
				return refuse('Unresolved or disconnected native operation');
			} else {
				if ($elm$core$List$length(model.l) >= 64) {
					return refuse('Unresolved operation capacity');
				} else {
					if (($author$project$Effects$protocol(operation) !== 2) || ((!caps.R) || (!A2(
						$elm$core$List$member,
						$author$project$Effects$operationName(operation),
						caps.d1)))) {
						return refuse('Geometry operation not negotiated');
					} else {
						if (observed.dE || ((!window.dK) || (window.a7 || window.dO))) {
							return refuse('Geometry target ineligible');
						} else {
							if ((_Utils_eq(operation, $author$project$Effects$Maximize) && ((!window.dZ) || (!(!window.c3)))) || (_Utils_eq(operation, $author$project$Effects$RestoreGeometry) && ((!window.d7) || ((window.c3 !== 1) || (!window.d5))))) {
								return refuse('Geometry state/capability unavailable');
							} else {
								if (function () {
									if (operation.$ === 5) {
										var proposed = operation.a;
										return !A3($author$project$Snap$matches, observed, incarnation, proposed);
									} else {
										return false;
									}
								}()) {
									return refuse('Snap output/work-area placement changed');
								} else {
									var intent = {A: observed.A, dP: generation, U: incarnation, aK: operation, o: request};
									var transaction = {Y: 2, K: intent, cx: 0};
									return _Utils_Tuple3(
										_Utils_update(
											model,
											{
												dP: generation,
												o: request,
												z: $elm$core$Maybe$Just(transaction),
												l: A2($elm$core$List$cons, transaction, model.l)
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
			}
		} else {
			return refuse('Missing geometry target or exhausted identity');
		}
	});
var $author$project$Effects$canProveUnsent = F3(
	function (protocolId, intent, model) {
		var exact = function (entry) {
			return _Utils_eq(entry.Y, protocolId) && _Utils_eq(entry.K, intent);
		};
		var currentSafe = function () {
			var _v0 = model.z;
			if (!_v0.$) {
				var entry = _v0.a;
				return (!exact(entry)) || (!entry.cx);
			} else {
				return true;
			}
		}();
		return _Utils_eq(
			$author$project$Effects$protocol(intent.aK),
			protocolId) && (currentSafe && A2(
			$elm$core$List$any,
			function (entry) {
				return exact(entry) && (!entry.cx);
			},
			model.l));
	});
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
				model.d,
				$elm$core$Maybe$Just(key.d)) && (A2(
				$elm$core$List$any,
				function (entry) {
					return _Utils_eq(entry.d, key.d) && (_Utils_eq(entry.b_, key.b_) && _Utils_eq(entry.K, key.K));
				},
				model.C) && A3($author$project$Effects$canProveUnsent, key.b_, key.K, model.R));
		};
		return (!$elm$core$List$isEmpty(operations)) && (($elm$core$List$length(operations) <= 16) && (_Utils_eq(
			$elm$core$List$length(unique),
			$elm$core$List$length(operations)) && ((!(!model.G)) && ((model.G !== 3) && A2($elm$core$List$all, known, operations)))));
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
		return (($elm$core$List$length(caps.d1) <= 3) && (A2(
			$elm$core$List$all,
			function (op) {
				return A2(
					$elm$core$List$member,
					op,
					_List_fromArray(
						['maximize', 'restore-geometry', 'snap']));
			},
			caps.d1) && (_Utils_eq(
			$elm$core$List$length(caps.d1),
			$elm$core$List$length(
				A3(
					$elm$core$List$foldl,
					F2(
						function (x, xs) {
							return A2($elm$core$List$member, x, xs) ? xs : A2($elm$core$List$cons, x, xs);
						}),
					_List_Nil,
					caps.d1))) && _Utils_eq(
			caps.R,
			!$elm$core$List$isEmpty(caps.d1))))) ? $elm$json$Json$Decode$succeed(caps) : $elm$json$Json$Decode$fail('Geometry capabilities');
	},
	A2(
		$author$project$GeometryProjection$strict,
		_List_fromArray(
			['observe', 'effects', 'effectProtocol', 'operations', 'placementCapacity', 'canonicalScene']),
		A7(
			$elm$json$Json$Decode$map6,
			F6(
				function (_v0, effects, _v1, operations, _v2, _v3) {
					return {R: effects, d1: operations};
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
var $author$project$GeometryProjection$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (x) {
		return _Utils_eq(x, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero geometry identity') : $elm$json$Json$Decode$succeed(x);
	},
	$author$project$UInt64$decoder);
var $author$project$GeometryProjection$Fullscreen = 2;
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
	var _v0 = inputs.ba;
	var ux = _v0.a;
	var uy = _v0.b;
	var _v1 = inputs.bb;
	var rx = _v1.a;
	var ry = _v1.b;
	var _v2 = inputs.a6;
	var lx = _v2.a;
	var ly = _v2.b;
	var _v3 = inputs.a5;
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
			{an: h, aw: w, ax: x, ay: y});
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$GeometrySizePolicy$roundNative = function (x) {
	return (x >= 0) ? ($elm$core$Basics$floor(x) + (((x - $elm$core$Basics$floor(x)) >= 0.5) ? 1 : 0)) : ($elm$core$Basics$ceiling(x) - ((($elm$core$Basics$ceiling(x) - x) >= 0.5) ? 1 : 0));
};
var $author$project$GeometrySizePolicy$rounded = function (value) {
	return {
		an: $author$project$GeometrySizePolicy$roundNative(value.ay + value.an) - $author$project$GeometrySizePolicy$roundNative(value.ay),
		aw: $author$project$GeometrySizePolicy$roundNative(value.ax + value.aw) - $author$project$GeometrySizePolicy$roundNative(value.ax),
		ax: $author$project$GeometrySizePolicy$roundNative(value.ax),
		ay: $author$project$GeometrySizePolicy$roundNative(value.ay)
	};
};
var $author$project$GeometrySizePolicy$within = F2(
	function (inputs, projection) {
		var axis = F6(
			function (configured, real, rawLo, rawHi, lo, hi) {
				return (configured >= 1) && ((configured <= 2147483647) && ((_Utils_cmp(configured, rawLo) > -1) && (((!rawHi) || (_Utils_cmp(configured, rawHi) < 1)) && ((_Utils_cmp(real, lo) > -1) && (_Utils_cmp(real, hi) < 1)))));
			});
		var _v0 = inputs.ba;
		var ux = _v0.a;
		var uy = _v0.b;
		var _v1 = inputs.bb;
		var rx = _v1.a;
		var ry = _v1.b;
		var _v2 = inputs.a6;
		var lx = _v2.a;
		var ly = _v2.b;
		var _v3 = inputs.a5;
		var hx = _v3.a;
		var hy = _v3.b;
		var _v4 = projection.cf;
		var cx = _v4.a;
		var cy = _v4.b;
		return _Utils_eq(
			projection.cf,
			_Utils_Tuple2(
				$elm$core$Basics$floor(projection.bd.aw),
				$elm$core$Basics$floor(projection.bd.an))) && (A6(axis, cx, projection.bd.aw, rx, ux, lx, hx) && A6(axis, cy, projection.bd.an, ry, uy, ly, hy));
	});
var $author$project$GeometrySizePolicy$projectionValid = F4(
	function (maximize, workArea, inputs, projection) {
		var real = projection.bd;
		var logical = projection.c_;
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
			projection.du,
			$elm$core$Maybe$Just(real));
		var _v0 = inputs.cz;
		var tx = _v0.a;
		var ty = _v0.b;
		var _v1 = inputs.cb;
		var bx = _v1.a;
		var by = _v1.b;
		var converted = maximize ? {an: logical.an - (ty + by), aw: logical.aw - (tx + bx), ax: logical.ax + tx, ay: logical.ay + ty} : logical;
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
				projection.du)) && (_Utils_eq(real, converted) && (A2($author$project$GeometrySizePolicy$within, inputs, projection) && (source && ((!maximize) || _Utils_eq(projection.du, $elm$core$Maybe$Nothing))))));
	});
var $author$project$GeometrySizePolicy$supported = function (policy) {
	var _v0 = policy.ch;
	if (_v0.$ === 1) {
		return false;
	} else {
		var inputs = _v0.a;
		return _Utils_eq(
			inputs.bZ,
			_Utils_Tuple2(0, 0)) && (!$author$project$GeometrySizePolicy$fixed(inputs));
	}
};
var $author$project$GeometrySizePolicy$coherent = F4(
	function (policy, workArea, constrained, fixedSize) {
		var _v0 = policy.ch;
		if (_v0.$ === 1) {
			return _Utils_eq(policy.dZ, $elm$core$Maybe$Nothing) && _Utils_eq(policy.d7, $elm$core$Maybe$Nothing);
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
					values(inputs.bb),
					values(inputs.a6))) || (A2(
				$elm$core$List$any,
				$elm$core$Basics$lt(0),
				values(inputs.ba)) || A2(
				$elm$core$List$any,
				$elm$core$Basics$gt(1.7976931348623157e308),
				values(inputs.a5)));
			return _Utils_eq(constrained, expected) && (_Utils_eq(
				fixedSize,
				$author$project$GeometrySizePolicy$fixed(inputs)) && (A2(valid, true, policy.dZ) && A2(valid, false, policy.d7)));
		}
	});
var $author$project$GeometrySizePolicy$permits = F2(
	function (maximize, policy) {
		return $author$project$GeometrySizePolicy$supported(policy) && (maximize ? (!_Utils_eq(policy.dZ, $elm$core$Maybe$Nothing)) : (!_Utils_eq(policy.d7, $elm$core$Maybe$Nothing)));
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
									return _Utils_eq(row.U, id);
								},
								rows));
						if (_v0.$ === 1) {
							return false;
						} else {
							var row = _v0.a;
							var _v1 = row.co;
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
			var sizeValid = A2(
				$elm$core$Maybe$withDefault,
				true,
				A2(
					$elm$core$Maybe$map,
					function (p) {
						return A4($author$project$GeometrySizePolicy$coherent, p, row.bj, row.bR, row.dO) && (((!row.dK) || $author$project$GeometrySizePolicy$supported(p)) && (((!row.dZ) || A2($author$project$GeometrySizePolicy$permits, true, p)) && ((!row.d7) || A2($author$project$GeometrySizePolicy$permits, false, p))));
					},
					row.b5));
			var ownership = function () {
				var _v2 = row.co;
				if (_v2.$ === 1) {
					return true;
				} else {
					return A2(walk, _List_Nil, row.U);
				}
			}();
			var known = A2(
				$elm$core$List$map,
				$elm$core$Basics$identity,
				_List_fromArray(
					[
						!_Utils_eq(row.bk, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.bl, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.bz, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.aL, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.bM, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.bj, $elm$core$Maybe$Nothing)
					]));
			var paired = A2(
				$elm$core$List$all,
				$elm$core$Basics$eq(true),
				known) || A2(
				$elm$core$List$all,
				$elm$core$Basics$eq(false),
				known);
			var eligible = (!row.dK) || ((!_Utils_eq(row.bk, $elm$core$Maybe$Nothing)) && ((!blocked) && ((!row.a7) && ((!row.bs) && ((!row.dO) && (((!_Utils_eq(row.b5, $elm$core$Maybe$Nothing)) || (!row.bR)) && (row.bq && (_Utils_eq(row.co, $elm$core$Maybe$Nothing) && (_Utils_eq(row.c3, row.ce) && (row.c3 !== 2))))))))));
			var capabilityModes = ((!row.dZ) || (row.dK && (!row.c3))) && ((!row.d7) || (row.dK && ((row.c3 === 1) && row.d5)));
			return paired && (eligible && (ownership && (sizeValid && (capabilityModes && (((!row.dZ) || A2($elm$core$List$member, 'maximize', caps.d1)) && ((!row.d7) || A2($elm$core$List$member, 'restore-geometry', caps.d1)))))));
		};
		var ids = A2(
			$elm$core$List$map,
			function ($) {
				return $.U;
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
				return (_Utils_eq(a.aL, $elm$core$Maybe$Nothing) || ((!_Utils_eq(a.aL, b.aL)) || _Utils_eq(a.bz, b.bz))) && (_Utils_eq(a.bl, $elm$core$Maybe$Nothing) || ((!_Utils_eq(a.bl, b.bl)) || (_Utils_eq(a.bk, b.bk) && (_Utils_eq(a.aL, b.aL) && (_Utils_eq(a.bM, b.bM) && _Utils_eq(a.bj, b.bj))))));
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
		return {ch: inputs, dZ: maximize, d7: restoreGeometry};
	});
var $author$project$GeometrySizePolicy$finite = function (x) {
	return !($elm$core$Basics$isNaN(x) || $elm$core$Basics$isInfinite(x));
};
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
		return ($author$project$GeometrySizePolicy$finite(inputs.b2) && ((inputs.b2 > 0) && (A3($author$project$GeometrySizePolicy$interval, true, inputs.bb, inputs.ba) && A3($author$project$GeometrySizePolicy$interval, false, inputs.a6, inputs.a5)))) ? $elm$json$Json$Decode$succeed(inputs) : $elm$json$Json$Decode$fail('Size intervals');
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
					return (profile === 'wayland-zero-origin-v1') ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Conversion profile');
				},
				A2($elm$json$Json$Decode$field, 'profile', $elm$json$Json$Decode$string)),
			A9(
				$elm$json$Json$Decode$map8,
				F8(
					function (rawMin, rawMax, layoutMin, layoutMax, origin, tl, br, scale) {
						return {cb: br, a5: layoutMax, a6: layoutMin, bZ: origin, ba: rawMax, bb: rawMin, b2: scale, cz: tl};
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
		return {cf: configure, c_: logical, bd: real, du: visual};
	});
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
				{an: h, aw: w, ax: x, ay: y}) : $elm$json$Json$Decode$fail('Prospective box');
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
				return {cE: client, cM: fixed, bq: floating, bs: grouped, c_: logical, a7: minimized, c2: _native, du: visual};
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
				return {cd: caps, cF: constrained, dK: eligible, cY: known, $7: size};
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
				return {cU: inc, c0: mon, c6: og, co: owner, dw: wa, dx: wg, dy: wr, dz: ws};
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
					return {ce: s.cE, bR: p.cF, dK: p.dK, dO: s.cM, bq: s.bq, bs: s.bs, U: i.cU, c$: s.c_, dZ: p.cd.a, a7: s.a7, bz: i.c0, c3: s.c2, aL: i.c6, co: i.co, d5: p.cY, d7: p.cd.b, b5: p.$7, dv: s.du, bj: i.dw, bM: i.dy, bk: i.dz, bl: i.dx};
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
				return (A3($author$project$GeometryProjection$validRows, caps, snapshot.dE, snapshot.a) && A2(
					$elm$core$Maybe$withDefault,
					true,
					A2(
						$elm$core$Maybe$map,
						function (id) {
							return A2(
								$elm$core$List$any,
								function (row) {
									return _Utils_eq(row.U, id);
								},
								snapshot.a);
						},
						snapshot.br))) ? $elm$json$Json$Decode$succeed(snapshot) : $elm$json$Json$Decode$fail('Geometry facts coherence');
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
									return {dM: epoch, dY: life, m: output, dj: revision};
								} else {
									return {dM: $author$project$UInt64$zero, dY: $author$project$UInt64$zero, m: output, dj: revision};
								}
							}();
							return {d: binding, dE: facts.dE, A: context, br: facts.br, o: request, dm: sequence, a: facts.a};
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
											return {dE: blocked, br: focus, a: rows};
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
		model.R);
	var effects = _v0.a;
	return _Utils_update(
		model,
		{
			Q: false,
			cH: false,
			R: effects,
			n: $elm$core$Maybe$Nothing,
			ad: $elm$core$Maybe$Nothing,
			cQ: $elm$core$Maybe$Nothing,
			cR: $elm$core$Maybe$Nothing,
			dQ: $elm$core$Maybe$Nothing,
			d_: A2(
				$elm$core$Maybe$withDefault,
				'Connection lost. Reconnect to continue.',
				A2($elm$core$Maybe$map, $author$project$Shell$recoveryNotice, model.be)),
			_: false,
			G: 0,
			as: false,
			aP: false,
			H: false
		});
};
var $author$project$Effects$locallyRefuseUnsent = F3(
	function (protocolId, intent, model) {
		var exact = function (entry) {
			return _Utils_eq(entry.Y, protocolId) && _Utils_eq(entry.K, intent);
		};
		return (!A3($author$project$Effects$canProveUnsent, protocolId, intent, model)) ? model : _Utils_update(
			model,
			{
				z: A2(
					$elm$core$Maybe$map,
					function (entry) {
						return exact(entry) ? _Utils_update(
							entry,
							{cx: 2}) : entry;
					},
					model.z),
				l: A2(
					$elm$core$List$filter,
					A2($elm$core$Basics$composeR, exact, $elm$core$Basics$not),
					model.l)
			});
	});
var $author$project$Shell$matchesUnsent = F2(
	function (observations, model) {
		var slot = function (kind) {
			switch (kind) {
				case 'projection-request':
					return model.n;
				case 'geometry-facts-request':
					return model.dQ;
				case 'geometry-attach':
					return model.cQ;
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
	return ((!model.G) || ((model.G === 3) || model.H)) ? _Utils_Tuple2(model, _List_Nil) : ((model.cH || ($author$project$Effects$pending(model.R) || ((!_Utils_eq(model.n, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(model.dQ, $elm$core$Maybe$Nothing)) || (!_Utils_eq(model.cQ, $elm$core$Maybe$Nothing)))))) ? _Utils_Tuple2(
		_Utils_update(
			model,
			{_: true}),
		_List_Nil) : $author$project$Shell$refreshObservations(model));
};
var $author$project$Shell$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (!_Utils_eq(value, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Zero displayed scope');
	},
	$author$project$UInt64$decoder);
var $author$project$Effects$recoverUnknown = F3(
	function (protocolId, intent, model) {
		var observe = function (transaction) {
			return (_Utils_eq(transaction.K, intent) && (_Utils_eq(transaction.Y, protocolId) && (!transaction.cx))) ? _Utils_update(
				transaction,
				{cx: 4}) : transaction;
		};
		var _v0 = A2(
			$author$project$Effects$apply,
			$elm$json$Json$Encode$object(
				_List_fromArray(
					[
						_Utils_Tuple2(
						'kind',
						$elm$json$Json$Encode$string('recover')),
						_Utils_Tuple2(
						'intent',
						$author$project$Effects$encodeIntent(intent)),
						_Utils_Tuple2(
						'effectProtocol',
						$elm$json$Json$Encode$int(protocolId))
					])),
			model);
		var recovered = _v0.a;
		var error = _v0.c;
		if (!error.$) {
			var reason = error.a;
			return $elm$core$Result$Err(reason);
		} else {
			return $elm$core$Result$Ok(
				_Utils_update(
					recovered,
					{
						z: A2($elm$core$Maybe$map, observe, recovered.z),
						l: A2($elm$core$List$map, observe, recovered.l)
					}));
		}
	});
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
var $author$project$Effects$releaseUnknown = F3(
	function (protocolId, intent, model) {
		return _Utils_update(
			model,
			{
				l: A2(
					$elm$core$List$filter,
					function (t) {
						return !((t.cx === 4) && (_Utils_eq(t.Y, protocolId) && _Utils_eq(t.K, intent)));
					},
					model.l)
			});
	});
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
var $author$project$NativeOutcome$intent = function (protocolId) {
	return A2(
		$elm$json$Json$Decode$andThen,
		function (original) {
			return _Utils_eq(
				$author$project$Effects$protocol(original.aK),
				protocolId) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Outcome operation protocol');
		},
		$author$project$Effects$intentDecoder);
};
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
			case 0:
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{bD: true, H: true}),
					_List_Nil);
			case 1:
				var protocolId = msg.a;
				var intent = msg.b;
				var _v1 = A3($author$project$Effects$recoverUnknown, protocolId, intent, model.R);
				if (_v1.$ === 1) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var effects = _v1.a;
					return _Utils_Tuple2(
						_Utils_update(
							model,
							{R: effects, d_: 'The previous window change could not be confirmed.'}),
						_List_Nil);
				}
			case 2:
				var preserveShared = msg.a;
				var oldBinding = msg.b;
				var protocolId = msg.c;
				var intent = msg.d;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							R: preserveShared ? model.R : A3($author$project$Effects$releaseUnknown, protocolId, intent, model.R),
							C: A2(
								$elm$core$List$filter,
								function (entry) {
									return !(_Utils_eq(entry.d, oldBinding) && (_Utils_eq(entry.b_, protocolId) && _Utils_eq(entry.K, intent)));
								},
								model.C),
							d_: 'Previous request remains unconfirmed. Choose a new window action.'
						}),
					_List_Nil);
			case 4:
				return ((!model.G) || $author$project$Effects$pending(model.R)) ? _Utils_Tuple2(model, _List_Nil) : ($author$project$Shell$geometrySupported(model) ? $author$project$Shell$notificationRefresh(model) : $author$project$Shell$refresh(model));
			case 5:
				return ((!model.G) && (!model.aP)) ? _Utils_Tuple2(
					_Utils_update(
						model,
						{d_: 'Reconnecting…', aP: true}),
					_List_fromArray(
						[$author$project$Shell$RestartBackend])) : _Utils_Tuple2(model, _List_Nil);
			case 11:
				var reissue = msg.a;
				if ((!model.G) || ((model.G === 3) || _Utils_eq(model.d, $elm$core$Maybe$Nothing))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var retired = _Utils_update(
						model,
						{cH: false, n: $elm$core$Maybe$Nothing, cQ: $elm$core$Maybe$Nothing, dQ: $elm$core$Maybe$Nothing, _: true, G: 1, as: false});
					var attach = model.Q || (!_Utils_eq(model.cQ, $elm$core$Maybe$Nothing));
					if (!reissue) {
						return _Utils_Tuple2(retired, _List_Nil);
					} else {
						var _v2 = $author$project$Shell$refreshObservations(retired);
						var fresh = _v2.a;
						var commands = _v2.b;
						var _v3 = attach ? A2($author$project$Shell$geometryRequest, true, fresh) : _Utils_Tuple2(fresh, _List_Nil);
						var attached = _v3.a;
						var attachCommands = _v3.b;
						return _Utils_Tuple2(
							attached,
							_Utils_ap(commands, attachCommands));
					}
				}
			case 13:
				var operations = msg.a;
				var observations = msg.b;
				var matches = F2(
					function (key, entry) {
						return _Utils_eq(entry.d, key.d) && (_Utils_eq(entry.b_, key.b_) && _Utils_eq(entry.K, key.K));
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
							function (_v4) {
								var name = _v4.a;
								var id = _v4.b;
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
							return A3($author$project$Effects$locallyRefuseUnsent, key.b_, key.K, state);
						}),
					model.R,
					proven);
				var retired = _Utils_update(
					model,
					{
						Q: model.Q || A2(has, 'geometry-attach', model.cQ),
						cH: false,
						R: effects,
						n: A2(has, 'projection-request', model.n) ? $elm$core$Maybe$Nothing : model.n,
						cQ: A2(has, 'geometry-attach', model.cQ) ? $elm$core$Maybe$Nothing : model.cQ,
						dQ: A2(has, 'geometry-facts-request', model.dQ) ? $elm$core$Maybe$Nothing : model.dQ,
						C: A2(
							$elm$core$List$filter,
							function (entry) {
								return !A2(
									$elm$core$List$any,
									function (key) {
										return A2(matches, key, entry);
									},
									proven);
							},
							model.C),
						d_: 'The request was not sent. Waiting for window transport recovery.',
						_: true,
						G: ((!model.G) || (model.G === 3)) ? model.G : 1,
						H: true
					});
				return _Utils_Tuple2(retired, _List_Nil);
			case 14:
				var reissue = msg.a;
				if (!model.H) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var recovered = _Utils_update(
						model,
						{H: false});
					return ((!reissue) || ((!recovered.G) || ((recovered.G === 3) || ($author$project$Effects$pending(recovered.R) || ((!_Utils_eq(recovered.n, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(recovered.dQ, $elm$core$Maybe$Nothing)) || (!_Utils_eq(recovered.cQ, $elm$core$Maybe$Nothing)))))))) ? _Utils_Tuple2(recovered, _List_Nil) : $author$project$Shell$refreshObservations(recovered);
				}
			case 12:
				var operations = msg.a;
				if (!A2($author$project$Shell$canProveUnsent, operations, model)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var matches = F2(
						function (key, entry) {
							return _Utils_eq(entry.d, key.d) && (_Utils_eq(entry.b_, key.b_) && _Utils_eq(entry.K, key.K));
						});
					var effects = A3(
						$elm$core$List$foldl,
						F2(
							function (key, state) {
								return A3($author$project$Effects$locallyRefuseUnsent, key.b_, key.K, state);
							}),
						model.R,
						operations);
					var updated = _Utils_update(
						model,
						{
							R: effects,
							C: A2(
								$elm$core$List$filter,
								function (entry) {
									return !A2(
										$elm$core$List$any,
										function (key) {
											return A2(matches, key, entry);
										},
										operations);
								},
								model.C),
							d_: 'The request was not sent. Choose again.'
						});
					return $author$project$Shell$resumeNotifications(updated);
				}
			case 10:
				var observations = msg.a;
				var valid = A2($author$project$Shell$matchesUnsent, observations, model);
				var contains = function (kind) {
					return A2(
						$elm$core$List$any,
						function (_v7) {
							var name = _v7.a;
							return _Utils_eq(name, kind);
						},
						observations);
				};
				var cleared = _Utils_update(
					model,
					{
						n: contains('projection-request') ? $elm$core$Maybe$Nothing : model.n,
						cQ: contains('geometry-attach') ? $elm$core$Maybe$Nothing : model.cQ,
						dQ: contains('geometry-facts-request') ? $elm$core$Maybe$Nothing : model.dQ,
						_: true
					});
				if ((!valid) || ((!model.G) || (model.G === 3))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					if ($author$project$Effects$pending(model.R) || (model.cH || ((!_Utils_eq(cleared.n, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(cleared.dQ, $elm$core$Maybe$Nothing)) || (!_Utils_eq(cleared.cQ, $elm$core$Maybe$Nothing)))))) {
						return _Utils_Tuple2(cleared, _List_Nil);
					} else {
						var _v5 = $author$project$Shell$refreshObservations(cleared);
						var fresh = _v5.a;
						var commands = _v5.b;
						var _v6 = contains('geometry-attach') ? A2($author$project$Shell$geometryRequest, true, fresh) : _Utils_Tuple2(fresh, _List_Nil);
						var attached = _v6.a;
						var attachCommands = _v6.b;
						return _Utils_Tuple2(
							attached,
							_Utils_ap(commands, attachCommands));
					}
				}
			case 6:
				return _Utils_Tuple2(model, _List_Nil);
			case 7:
				return A2($author$project$Shell$geometryRequest, true, model);
			case 8:
				return A2($author$project$Shell$geometryRequest, false, model);
			case 9:
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
								{d_: 'Window list changed. Choose again.'}),
							_List_Nil);
					} else {
						var _v8 = function () {
							if ($author$project$Effects$protocol(operation) === 2) {
								var _v9 = _Utils_Tuple2(model.cR, model.ad);
								if ((!_v9.a.$) && (!_v9.b.$)) {
									var caps = _v9.a.a;
									var observed = _v9.b.a;
									return ((!_Utils_eq(model.dQ, $elm$core$Maybe$Nothing)) || (!_Utils_eq(model.cQ, $elm$core$Maybe$Nothing))) ? _Utils_Tuple3(
										model.R,
										$elm$core$Maybe$Nothing,
										$elm$core$Maybe$Just('Geometry refresh pending')) : A5($author$project$Effects$beginGeometry, caps, observed, operation, incarnation, model.R);
								} else {
									return _Utils_Tuple3(
										model.R,
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
									model.R);
							}
						}();
						var effects = _v8.a;
						var command = _v8.b;
						var error = _v8.c;
						var commands = function () {
							var _v11 = _Utils_Tuple2(command, model.d);
							if ((!_v11.a.$) && (!_v11.b.$)) {
								var value = _v11.a.a;
								var binding = _v11.b.a;
								var _v12 = A2(
									$elm$json$Json$Decode$decodeValue,
									A2($elm$json$Json$Decode$field, 'intent', $elm$json$Json$Decode$value),
									value);
								if (!_v12.$) {
									var intent = _v12.a;
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
									R: effects,
									C: function () {
										var _v10 = _Utils_Tuple3(command, model.d, effects.z);
										if (((!_v10.a.$) && (!_v10.b.$)) && (!_v10.c.$)) {
											var binding = _v10.b.a;
											var transaction = _v10.c.a;
											return A2(
												$elm$core$List$cons,
												{d: binding, K: transaction.K, b_: transaction.Y},
												model.C);
										} else {
											return model.C;
										}
									}(),
									d_: A2($elm$core$Maybe$withDefault, model.d_, error)
								}),
							commands);
					}
				}
			default:
				var raw = msg.a;
				var _v13 = A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
					raw);
				_v13$13:
				while (true) {
					if (!_v13.$) {
						switch (_v13.a) {
							case 'host-recovery-failed':
								var _v14 = A2(
									$elm$json$Json$Decode$decodeValue,
									A2(
										$author$project$Shell$strict,
										_List_fromArray(
											['protocolVersion', 'kind', 'reason']),
										A3(
											$elm$json$Json$Decode$map2,
											F2(
												function (_v15, reason) {
													return reason;
												}),
											$author$project$Shell$version,
											A2($elm$json$Json$Decode$field, 'reason', $author$project$Shell$recoveryDecoder))),
									raw);
								if (!_v14.$) {
									var reason = _v14.a;
									var detached = $author$project$Shell$disconnect(model);
									return _Utils_Tuple2(
										_Utils_update(
											detached,
											{
												d_: $author$project$Shell$recoveryNotice(reason),
												be: $elm$core$Maybe$Just(reason)
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
								var _v16 = A2(
									$elm$json$Json$Decode$decodeValue,
									A2(
										$author$project$Shell$strict,
										_List_fromArray(
											['protocolVersion', 'kind']),
										$author$project$Shell$version),
									raw);
								if (!_v16.$) {
									return $author$project$Shell$notificationRefresh(model);
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'attached':
								var _v17 = A2(
									$elm$json$Json$Decode$decodeValue,
									A3(
										$elm$json$Json$Decode$map2,
										F2(
											function (_v18, binding) {
												return binding;
											}),
										$author$project$Shell$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder)),
									raw);
								if (!_v17.$) {
									var binding = _v17.a;
									if ((!(!model.G)) || ((!model.aP) || A2(
										$elm$core$Maybe$withDefault,
										false,
										A2(
											$elm$core$Maybe$map,
											A2(
												$elm$core$Basics$composeR,
												$author$project$Binding$replaces(binding),
												$elm$core$Basics$not),
											model.d)))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var detached = $author$project$Shell$disconnect(model);
										return $author$project$Shell$refresh(
											_Utils_update(
												detached,
												{
													d: $elm$core$Maybe$Just(binding),
													d_: 'Updating window information…',
													G: 1,
													aP: false,
													be: $elm$core$Maybe$Nothing
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
											function (_v21, binding, request, _v22) {
												return _Utils_Tuple2(binding, request);
											}),
										$author$project$Shell$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$Shell$positive),
										A2(
											$elm$json$Json$Decode$andThen,
											function (reason) {
												return (reason === 'scene-changed') ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Projection terminal reason');
											},
											A2($elm$json$Json$Decode$field, 'reason', $elm$json$Json$Decode$string))));
								var _v19 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (_v19.$ === 1) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var _v20 = _v19.a;
									var binding = _v20.a;
									var request = _v20.b;
									return ((!model.G) || ((model.G === 3) || ((!_Utils_eq(
										model.d,
										$elm$core$Maybe$Just(binding))) || (!_Utils_eq(
										model.n,
										$elm$core$Maybe$Just(request)))))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$drainNotifications(
										_Utils_update(
											model,
											{n: $elm$core$Maybe$Nothing, _: true, G: 1, as: true}));
								}
							case 'action-projection':
								var decoder = A2(
									$author$project$Shell$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'context', 'scene']),
									A6(
										$elm$json$Json$Decode$map5,
										F5(
											function (_v28, binding, request, life, epoch) {
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
								var _v23 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v23.$) {
									var _v24 = _v23.a;
									var binding = _v24.a;
									var request = _v24.b;
									var _v25 = _v24.c;
									var life = _v25.a;
									var epoch = _v25.b;
									if ((!model.G) || ((!_Utils_eq(
										model.d,
										$elm$core$Maybe$Just(binding))) || ((!_Utils_eq(
										model.n,
										$elm$core$Maybe$Just(request))) || (!A3($author$project$Binding$matchesContext, life, epoch, binding))))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var _v26 = A2(
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
										if (!_v26.$) {
											var snapshot = _v26.a;
											var _v27 = A2($author$project$Effects$apply, snapshot, model.R);
											var effects = _v27.a;
											var error = _v27.c;
											return $author$project$Shell$drainNotifications(
												_Utils_update(
													model,
													{
														R: effects,
														n: _Utils_eq(error, $elm$core$Maybe$Nothing) ? $elm$core$Maybe$Nothing : model.n,
														d_: _Utils_eq(error, $elm$core$Maybe$Nothing) ? 'Connected' : 'Window information could not be verified.',
														G: _Utils_eq(error, $elm$core$Maybe$Nothing) ? 2 : 1
													}));
										} else {
											return _Utils_Tuple2(model, _List_Nil);
										}
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'host-geometry-negotiate':
								var _v29 = A2(
									$elm$json$Json$Decode$decodeValue,
									A2(
										$author$project$Shell$strict,
										_List_fromArray(
											['protocolVersion', 'kind']),
										$author$project$Shell$version),
									raw);
								if (_v29.$ === 1) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									return ((!_Utils_eq(model.cR, $elm$core$Maybe$Nothing)) || (!_Utils_eq(model.cQ, $elm$core$Maybe$Nothing))) ? _Utils_Tuple2(model, _List_Nil) : A2($author$project$Shell$geometryRequest, true, model);
								}
							case 'geometry-unavailable':
								var decoder = A2(
									$author$project$Shell$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'reason']),
									A5(
										$elm$json$Json$Decode$map4,
										F4(
											function (_v31, binding, request, reason) {
												return {d: binding, b0: reason, o: request};
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
								var _v30 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (_v30.$ === 1) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var refusal = _v30.a;
									return ((!_Utils_eq(
										model.d,
										$elm$core$Maybe$Just(refusal.d))) || (!_Utils_eq(
										model.cQ,
										$elm$core$Maybe$Just(refusal.o)))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$drainNotifications(
										_Utils_update(
											model,
											{
												Q: false,
												ad: $elm$core$Maybe$Nothing,
												cQ: $elm$core$Maybe$Nothing,
												cR: $elm$core$Maybe$Just(
													{R: false, d1: _List_Nil}),
												dQ: $elm$core$Maybe$Nothing
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
											function (_v33, _v34, binding, request, caps) {
												return {d: binding, cd: caps, o: request};
											}),
										$author$project$Shell$version,
										A2(
											$elm$json$Json$Decode$andThen,
											function (v) {
												return (v === 2) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Geometry protocol');
											},
											A2($elm$json$Json$Decode$field, 'geometryProtocol', $elm$json$Json$Decode$int)),
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$Shell$positive),
										A2($elm$json$Json$Decode$field, 'capabilities', $author$project$GeometryProjection$capabilitiesDecoder)));
								var _v32 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v32.$) {
									var value = _v32.a;
									return ((!_Utils_eq(
										model.d,
										$elm$core$Maybe$Just(value.d))) || ((!_Utils_eq(
										model.cQ,
										$elm$core$Maybe$Just(value.o))) || (!model.G))) ? _Utils_Tuple2(model, _List_Nil) : A2(
										$author$project$Shell$geometryRequest,
										false,
										_Utils_update(
											model,
											{
												Q: false,
												ad: $elm$core$Maybe$Nothing,
												cQ: $elm$core$Maybe$Nothing,
												cR: $elm$core$Maybe$Just(value.cd)
											}));
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'geometry-facts':
								var _v35 = model.cR;
								if (_v35.$ === 1) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var caps = _v35.a;
									var _v36 = A2($author$project$GeometryProjection$decode, caps, raw);
									if (_v36.$ === 1) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var observed = _v36.a;
										var newer = function () {
											var _v37 = model.ad;
											if (_v37.$ === 1) {
												return true;
											} else {
												var old = _v37.a;
												return (_Utils_eq(old.A.dY, observed.A.dY) && _Utils_eq(old.A.dM, observed.A.dM)) ? ((!(!A2($author$project$UInt64$compare, observed.A.m, old.A.m))) && ((!(!A2($author$project$UInt64$compare, observed.dm, old.dm))) && ((!(!A2($author$project$UInt64$compare, observed.A.dj, old.A.dj))) && ((!_Utils_eq(observed.A.dj, old.A.dj)) || _Utils_eq(
													observed,
													_Utils_update(
														old,
														{o: observed.o, dm: observed.dm})))))) : true;
											}
										}();
										return ((!_Utils_eq(
											model.d,
											$elm$core$Maybe$Just(observed.d))) || ((!_Utils_eq(
											model.dQ,
											$elm$core$Maybe$Just(observed.o))) || ((!model.G) || (!newer)))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$drainNotifications(
											_Utils_update(
												model,
												{
													ad: $elm$core$Maybe$Just(observed),
													dQ: $elm$core$Maybe$Nothing
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
											function (_v41, binding, request, generation) {
												return _Utils_Tuple3(binding, request, generation);
											}),
										$author$project$Shell$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'request', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'generation', $author$project$UInt64$decoder)));
								var _v38 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v38.$) {
									var _v39 = _v38.a;
									var binding = _v39.a;
									var request = _v39.b;
									var generation = _v39.c;
									if ((model.G !== 1) || (!_Utils_eq(
										model.d,
										$elm$core$Maybe$Just(binding)))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var _v40 = A2(
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
											model.R);
										var effects = _v40.a;
										return _Utils_Tuple2(
											_Utils_update(
												model,
												{R: effects}),
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
													function (_v45, binding, intent) {
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
													function (_v46, binding, intent, protocolId) {
														return _Utils_Tuple3(binding, intent, protocolId);
													}),
												$author$project$Shell$version,
												A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
												A2($elm$json$Json$Decode$field, 'intent', $elm$json$Json$Decode$value),
												A2($elm$json$Json$Decode$field, 'effectProtocol', $elm$json$Json$Decode$int)))
										]));
								var _v42 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v42.$) {
									var _v43 = _v42.a;
									var binding = _v43.a;
									var intent = _v43.b;
									var protocolId = _v43.c;
									if ((!_Utils_eq(
										model.d,
										$elm$core$Maybe$Just(binding))) || ((model.G !== 1) || (!_Utils_eq(
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
										var _v44 = A2(
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
											model.R);
										var effects = _v44.a;
										var error = _v44.c;
										return (!_Utils_eq(error, $elm$core$Maybe$Nothing)) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
											_Utils_update(
												model,
												{R: effects, d_: 'The previous window change could not be confirmed.'}),
											_List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'effect-outcome':
								if (!$author$project$NativeOutcome$valid(raw)) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var _v47 = A2(
										$elm$json$Json$Decode$decodeValue,
										A5(
											$elm$json$Json$Decode$map4,
											F4(
												function (_v48, binding, protocolId, receipt) {
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
									if (!_v47.$) {
										var _v49 = _v47.a;
										var binding = _v49.a;
										var protocolId = _v49.b;
										var receipt = _v49.c;
										var receivedIntent = $elm$core$Result$toMaybe(
											A2(
												$elm$json$Json$Decode$decodeValue,
												A2($elm$json$Json$Decode$field, 'intent', $author$project$Effects$intentDecoder),
												raw));
										var exact = function (entry) {
											return _Utils_eq(entry.d, binding) && (_Utils_eq(entry.b_, protocolId) && _Utils_eq(
												$elm$core$Maybe$Just(entry.K),
												receivedIntent));
										};
										var known = A2($elm$core$List$any, exact, model.C);
										if (!known) {
											return _Utils_Tuple2(model, _List_Nil);
										} else {
											var retained = _Utils_eq(
												A2(
													$elm$json$Json$Decode$decodeValue,
													A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string),
													raw),
												$elm$core$Result$Ok('Unknown')) ? model.C : A2(
												$elm$core$List$filter,
												A2($elm$core$Basics$composeR, exact, $elm$core$Basics$not),
												model.C);
											var _v50 = A2($author$project$Effects$apply, receipt, model.R);
											var effects = _v50.a;
											var error = _v50.c;
											if (!_Utils_eq(error, $elm$core$Maybe$Nothing)) {
												return _Utils_Tuple2(model, _List_Nil);
											} else {
												var current = function () {
													var _v51 = model.R.z;
													if (_v51.$ === 1) {
														return false;
													} else {
														var transaction = _v51.a;
														return _Utils_eq(transaction.Y, protocolId) && _Utils_eq(
															$elm$core$Maybe$Just(transaction.K),
															receivedIntent);
													}
												}();
												return ((!current) || ((!model.G) || (!_Utils_eq(
													model.d,
													$elm$core$Maybe$Just(binding))))) ? _Utils_Tuple2(
													_Utils_update(
														model,
														{R: effects, C: retained}),
													_List_Nil) : $author$project$Shell$refreshObservations(
													_Utils_update(
														model,
														{R: effects, C: retained}));
											}
										}
									} else {
										return _Utils_Tuple2(model, _List_Nil);
									}
								}
							default:
								break _v13$13;
						}
					} else {
						break _v13$13;
					}
				}
				return _Utils_Tuple2(model, _List_Nil);
		}
	});
var $author$project$MenuBridge$advancePrepared = F4(
	function (message, previous, shell, model) {
		var state = model;
		var _v0 = state.u;
		if (_v0.$ === 1) {
			return A4($author$project$MenuBridge$answer, model, shell, _List_Nil, $elm$core$Maybe$Nothing);
		} else {
			var slot = _v0.a;
			if ((!shell.G) || ((shell.G === 3) || (!_Utils_eq(
				shell.d,
				$elm$core$Maybe$Just(
					$author$project$Provider$nativeBinding(slot.X.bF)))))) {
				return A3($author$project$MenuBridge$cancelPrepared, 'Selection disconnected or authority changed', shell, model);
			} else {
				var response = function () {
					if (message.$ === 3) {
						var raw = message.a;
						return $elm$core$Result$toMaybe(
							A2(
								$elm$json$Json$Decode$decodeValue,
								A4(
									$elm$json$Json$Decode$map3,
									F3(
										function (kind, _native, request) {
											return _Utils_Tuple3(kind, _native, request);
										}),
									A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
									A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
									A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder)),
								raw));
					} else {
						return $elm$core$Maybe$Nothing;
					}
				}();
				var legacyReady = slot.aX || (_Utils_eq(
					response,
					$elm$core$Maybe$Just(
						_Utils_Tuple3(
							'action-projection',
							$author$project$Provider$nativeBinding(slot.X.bF),
							slot.aJ))) && (_Utils_eq(
					previous.n,
					$elm$core$Maybe$Just(slot.aJ)) && _Utils_eq(shell.n, $elm$core$Maybe$Nothing)));
				var geometryReady = slot.aV || function () {
					var _v7 = slot.aF;
					if (_v7.$ === 1) {
						return true;
					} else {
						var request = _v7.a;
						return _Utils_eq(
							response,
							$elm$core$Maybe$Just(
								_Utils_Tuple3(
									'geometry-facts',
									$author$project$Provider$nativeBinding(slot.X.bF),
									request))) && (_Utils_eq(
							previous.dQ,
							$elm$core$Maybe$Just(request)) && _Utils_eq(shell.dQ, $elm$core$Maybe$Nothing));
					}
				}();
				var lostCorrelation = ((!legacyReady) && (!_Utils_eq(
					shell.n,
					$elm$core$Maybe$Just(slot.aJ)))) || ((!geometryReady) && (!_Utils_eq(shell.dQ, slot.aF)));
				var updatedSlot = _Utils_update(
					slot,
					{aV: geometryReady, aX: legacyReady});
				var updated = _Utils_update(
					state,
					{
						u: $elm$core$Maybe$Just(updatedSlot)
					});
				if (lostCorrelation) {
					return A3($author$project$MenuBridge$cancelPrepared, 'Post-close observation correlation changed', shell, updated);
				} else {
					if (!(legacyReady && (geometryReady && $author$project$Shell$available(shell)))) {
						return A4($author$project$MenuBridge$answer, updated, shell, _List_Nil, $elm$core$Maybe$Nothing);
					} else {
						if (!A2($author$project$MenuBridge$compatiblePrepared, updatedSlot, shell)) {
							return A3($author$project$MenuBridge$cancelPrepared, 'Window state changed. Choose again.', shell, updated);
						} else {
							var scope = $author$project$Provider$presentationScope(slot.X.bF);
							var generation = A2(
								$elm$core$Maybe$withDefault,
								$author$project$UInt64$zero,
								A2(
									$elm$core$Maybe$map,
									A2(
										$elm$core$Basics$composeR,
										function ($) {
											return $.A;
										},
										function ($) {
											return $.dj;
										}),
									shell.R.aa));
							var _v1 = A3(
								$author$project$NativeProvider$fromShell,
								{dG: generation, cn: scope.cn, cr: scope.cr},
								$author$project$Provider$incarnation(slot.X.bF),
								shell);
							if (_v1.$ === 1) {
								var reason = _v1.a;
								return A3($author$project$MenuBridge$cancelPrepared, reason, shell, updated);
							} else {
								var fresh = _v1.a;
								var _v2 = $author$project$MenuBridge$operation(slot.dB);
								if (_v2.$ === 1) {
									return A3($author$project$MenuBridge$cancelPrepared, 'Selected operation unavailable', shell, updated);
								} else {
									var nativeOperation = _v2.a;
									var stamp = ($author$project$Provider$actionProtocol(slot.dB) === 2) ? $author$project$Shell$captureGeometry(shell) : $author$project$Shell$capture(shell);
									if (stamp.$ === 1) {
										return A3($author$project$MenuBridge$cancelPrepared, 'Fresh native context unavailable', shell, updated);
									} else {
										var current = stamp.a;
										var _v4 = A2(
											$author$project$Shell$update,
											A3(
												$author$project$Shell$Act,
												current,
												nativeOperation,
												$author$project$Provider$incarnation(fresh)),
											shell);
										var issued = _v4.a;
										var commands = _v4.b;
										if ((commands.b && (!commands.a.$)) && (!commands.b.b)) {
											var command = commands.a.a;
											var _v6 = A5($author$project$ReceiptRouter$registerPrepared, slot.cg, slot.X.bF, fresh, command, state.V);
											if (_v6.$ === 1) {
												var reason = _v6.a;
												return A3($author$project$MenuBridge$cancelPrepared, reason, shell, updated);
											} else {
												var router = _v6.a;
												return A4(
													$author$project$MenuBridge$answer,
													_Utils_update(
														state,
														{u: $elm$core$Maybe$Nothing, V: router}),
													_Utils_update(
														issued,
														{cH: false}),
													commands,
													$elm$core$Maybe$Nothing);
											}
										} else {
											return A3($author$project$MenuBridge$cancelPrepared, 'Native operation unavailable', shell, updated);
										}
									}
								}
							}
						}
					}
				}
			}
		}
	});
var $author$project$Menu$markDisconnected = function (_v0) {
	var state = _v0;
	return _Utils_update(
		state,
		{
			aq: A2(
				$elm$core$Maybe$map,
				function (menu) {
					var _v1 = menu.cx;
					if (_v1.$ === 1) {
						var intent = _v1.a;
						return _Utils_update(
							menu,
							{
								cx: $author$project$Menu$Unknown(intent)
							});
					} else {
						return menu;
					}
				},
				state.aq),
			d3: A2(
				$elm$core$List$map,
				function (entry) {
					return _Utils_update(
						entry,
						{aQ: true});
				},
				state.d3)
		});
};
var $author$project$MenuBridge$connectionLost = function (_v0) {
	var state = _v0;
	var canceled = function () {
		var _v2 = state.u;
		if (_v2.$ === 1) {
			return state.aq;
		} else {
			var slot = _v2.a;
			return A2(
				$author$project$Menu$update,
				A3(
					$author$project$Menu$ReceiveFor,
					slot.by,
					slot.a8,
					$author$project$Menu$Refusal('Connection lost before dispatch')),
				state.aq).a;
		}
	}();
	var uncertain = $author$project$Menu$markDisconnected(canceled);
	var closed = function () {
		var _v1 = $author$project$Menu$snapshot(uncertain).aq;
		if (_v1.$ === 1) {
			return uncertain;
		} else {
			var view = _v1.a;
			return A2(
				$author$project$Menu$update,
				$author$project$Menu$Dismiss(view.bu),
				uncertain).a;
		}
	}();
	return _Utils_update(
		state,
		{aq: closed, u: $elm$core$Maybe$Nothing});
};
var $author$project$MenuBridge$preparedSnapshot = function (_v0) {
	var state = _v0;
	return A2(
		$elm$core$Maybe$map,
		function (slot) {
			return {aV: slot.aV, aF: slot.aF, aX: slot.aX, aJ: slot.aJ, bh: slot.bh};
		},
		state.u);
};
var $author$project$MenuBridge$guardedAct = F5(
	function (stamp, action, incarnation, shell, model) {
		var blocked = A3($author$project$MenuBridge$blockedFor, incarnation, shell, model);
		if (blocked || (!_Utils_eq(
			$author$project$MenuBridge$preparedSnapshot(model),
			$elm$core$Maybe$Nothing))) {
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
var $author$project$UnsentOperation$encodeCommand = function (key) {
	return $elm$json$Json$Encode$object(
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
				$elm$json$Json$Encode$int(key.b_)),
				_Utils_Tuple2(
				'binding',
				$author$project$Binding$encode(key.d)),
				_Utils_Tuple2(
				'intent',
				$author$project$Effects$encodeIntent(key.K))
			]));
};
var $author$project$ReceiptRouter$locallyRefuseUnsent = F2(
	function (proved, model) {
		var entries = model;
		var _v0 = A2(
			$elm$json$Json$Decode$decodeValue,
			$author$project$ReceiptRouter$command,
			$author$project$UnsentOperation$encodeCommand(proved));
		if (_v0.$ === 1) {
			return _Utils_Tuple2(model, $elm$core$Maybe$Nothing);
		} else {
			var _native = _v0.a;
			var _v1 = $elm$core$List$head(
				A2(
					$elm$core$List$filter,
					function (entry) {
						return _Utils_eq(entry.ap, _native);
					},
					entries));
			if (_v1.$ === 1) {
				return _Utils_Tuple2(model, $elm$core$Maybe$Nothing);
			} else {
				var entry = _v1.a;
				return _Utils_Tuple2(
					A2(
						$elm$core$List$filter,
						function (item) {
							return !_Utils_eq(item.ap, _native);
						},
						entries),
					$elm$core$Maybe$Just(
						A3(
							$author$project$Menu$ReceiveFor,
							entry.by,
							entry.d,
							$author$project$Menu$Refusal('The request was not sent. Choose again.'))));
			}
		}
	});
var $author$project$MenuBridge$locallyRefuseUnsent = F2(
	function (proved, model) {
		var state = model;
		var _v0 = A2($author$project$ReceiptRouter$locallyRefuseUnsent, proved, state.V);
		var router = _v0.a;
		var message = _v0.b;
		if (message.$ === 1) {
			return model;
		} else {
			var receipt = message.a;
			var _v2 = A2($author$project$Menu$update, receipt, state.aq);
			var menu = _v2.a;
			return _Utils_update(
				state,
				{aq: menu, V: router});
		}
	});
var $elm$json$Json$Decode$decodeString = _Json_runOnString;
var $author$project$Menu$Committed = {$: 0};
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
							return _Utils_eq(entry.ap, _native);
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
							return !_Utils_eq(item.by, entry.by);
						},
						entries);
					return _Utils_Tuple3(
						next,
						$elm$core$Maybe$Just(
							A3($author$project$Menu$ReceiveFor, entry.by, entry.d, outcome)),
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
					var _v1 = A2($author$project$ReceiptRouter$accept, raw, state.V);
					var router = _v1.a;
					var receipt = _v1.b;
					var error = _v1.c;
					if (receipt.$ === 1) {
						return _Utils_Tuple2(model, error);
					} else {
						var message = receipt.a;
						var _v3 = A2($author$project$Menu$update, message, state.aq);
						var menu = _v3.a;
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{aq: menu, V: router}),
							error);
					}
				default:
					return _Utils_Tuple2(model, $elm$core$Maybe$Nothing);
			}
		}
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
							$author$project$UInt64$string(context.m))),
						_Utils_Tuple2(
						'revision',
						$elm$json$Json$Encode$string(
							$author$project$UInt64$string(context.dj)))
					]))));
};
var $author$project$Menu$rebindReady = F5(
	function (id, previous, fresh, items, model) {
		var state = model;
		var _v0 = state.aq;
		if (!_v0.$) {
			var current = _v0.a;
			return (state.Z || ((!_Utils_eq(current.bu, id)) || ((!_Utils_eq(current.d, previous)) || ((!_Utils_eq(current.cx, $author$project$Menu$Ready)) || ((!_Utils_eq(current.dX, items)) || ((!$author$project$Menu$validItems(items)) || ((!A2($author$project$Menu$sameTarget, previous, fresh)) || ((!_Utils_eq(
				$author$project$Menu$outputTuple(previous),
				$author$project$Menu$outputTuple(fresh))) || (A2($elm$core$List$member, fresh, state.ao) || (A2(
				$elm$core$List$member,
				$author$project$Menu$outputTuple(fresh),
				state.at) || A2(
				$elm$core$List$any,
				function (entry) {
					return A2($author$project$Menu$sameTarget, entry.d, fresh);
				},
				state.d3))))))))))) ? model : _Utils_update(
				state,
				{
					aq: $elm$core$Maybe$Just(
						_Utils_update(
							current,
							{d: fresh}))
				});
		} else {
			return model;
		}
	});
var $author$project$MenuBridge$reconcileWithShell = F2(
	function (shell, model) {
		var state = model;
		if (!shell.G) {
			return $author$project$MenuBridge$connectionLost(model);
		} else {
			if (!_Utils_eq(state.u, $elm$core$Maybe$Nothing)) {
				return model;
			} else {
				var _v0 = state.a_;
				if (_v0.$ === 1) {
					return model;
				} else {
					var captured = _v0.a;
					var _v1 = shell.R.aa;
					if (_v1.$ === 1) {
						return model;
					} else {
						var observed = _v1.a;
						var retired = function () {
							var _v8 = A2(
								$author$project$Menu$update,
								$author$project$Menu$Invalidate(
									$author$project$Provider$getBinding(captured.bF)),
								state.aq);
							var menu = _v8.a;
							return _Utils_update(
								state,
								{aq: menu});
						}();
						var previous = $author$project$Provider$nativeContext(captured.bF);
						var sameAuthority = _Utils_eq(
							shell.d,
							$elm$core$Maybe$Just(
								$author$project$Provider$nativeBinding(captured.bF))) && (_Utils_eq(observed.A.dY, previous.dY) && (_Utils_eq(observed.A.dM, previous.dM) && _Utils_eq(observed.A.m, previous.m)));
						var liveRoot = _Utils_eq(
							A2(
								$author$project$ActionProjection$rootOf,
								$author$project$Provider$incarnation(captured.bF),
								observed.dk),
							$elm$core$Maybe$Just(
								$author$project$Provider$incarnation(captured.bF)));
						var changed = (!_Utils_eq(observed.A, previous)) || ((!sameAuthority) || ((!liveRoot) || (!_Utils_eq(
							A2(
								$elm$core$Maybe$map,
								function ($) {
									return $.A;
								},
								$author$project$Provider$geometryObservation(captured.bF)),
							_Utils_eq(
								$author$project$Provider$geometryObservation(captured.bF),
								$elm$core$Maybe$Nothing) ? $elm$core$Maybe$Nothing : A2(
								$elm$core$Maybe$map,
								function ($) {
									return $.A;
								},
								shell.ad)))));
						if (!changed) {
							return model;
						} else {
							var _v2 = $author$project$Menu$snapshot(state.aq).aq;
							if (!_v2.$) {
								var view = _v2.a;
								if ((!_Utils_eq(view.cx, $author$project$Menu$Ready)) || ((!sameAuthority) || (!liveRoot))) {
									return retired;
								} else {
									if ((!_Utils_eq(shell.n, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(shell.dQ, $elm$core$Maybe$Nothing)) || (!_Utils_eq(shell.cQ, $elm$core$Maybe$Nothing)))) {
										return model;
									} else {
										if (!$author$project$Shell$available(shell)) {
											return retired;
										} else {
											var scope = $author$project$Provider$presentationScope(captured.bF);
											var sameGeometry = function (fresh) {
												var _v5 = _Utils_Tuple2(
													$author$project$Provider$geometryObservation(captured.bF),
													$author$project$Provider$geometryObservation(fresh));
												_v5$2:
												while (true) {
													if (_v5.a.$ === 1) {
														if (_v5.b.$ === 1) {
															var _v6 = _v5.a;
															var _v7 = _v5.b;
															return true;
														} else {
															break _v5$2;
														}
													} else {
														if (!_v5.b.$) {
															var previousFacts = _v5.a.a;
															var currentFacts = _v5.b.a;
															return _Utils_eq(previousFacts.a, currentFacts.a) && (_Utils_eq(previousFacts.d, currentFacts.d) && (_Utils_eq(previousFacts.A.dY, currentFacts.A.dY) && (_Utils_eq(previousFacts.A.dM, currentFacts.A.dM) && _Utils_eq(previousFacts.A.m, currentFacts.A.m))));
														} else {
															break _v5$2;
														}
													}
												}
												return false;
											};
											var _v3 = A3(
												$author$project$NativeProvider$fromShell,
												{dG: observed.A.dj, cn: scope.cn, cr: scope.cr},
												$author$project$Provider$incarnation(captured.bF),
												shell);
											if (_v3.$ === 1) {
												return retired;
											} else {
												var fresh = _v3.a;
												if ((!_Utils_eq(
													$author$project$Provider$getItems(fresh),
													$author$project$Provider$getItems(captured.bF))) || ((!_Utils_eq(
													$author$project$Provider$title(fresh),
													$author$project$Provider$title(captured.bF))) || (!sameGeometry(fresh)))) {
													return retired;
												} else {
													var _v4 = $author$project$MenuBridge$providerStamp(fresh);
													if (_v4.$ === 1) {
														return retired;
													} else {
														var stamp = _v4.a;
														var refreshed = A5(
															$author$project$Menu$rebindReady,
															view.bu,
															view.d,
															$author$project$Provider$getBinding(fresh),
															$author$project$Provider$getItems(fresh),
															state.aq);
														return (!_Utils_eq(
															A2(
																$elm$core$Maybe$map,
																function ($) {
																	return $.d;
																},
																$author$project$Menu$snapshot(refreshed).aq),
															$elm$core$Maybe$Just(
																$author$project$Provider$getBinding(fresh)))) ? retired : _Utils_update(
															state,
															{
																aq: refreshed,
																a_: $elm$core$Maybe$Just(
																	{bF: fresh, b6: stamp})
															});
													}
												}
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
		}
	});
var $author$project$TaskbarShell$native = F2(
	function (message, model) {
		var menus = function () {
			switch (message.$) {
				case 3:
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
										model.k).a : model.k;
								case 'host-disconnected':
									return $author$project$MenuBridge$connectionLost(model.k);
								default:
									break _v4$2;
							}
						} else {
							break _v4$2;
						}
					}
					return model.k;
				case 13:
					var operations = message.a;
					return A3(
						$elm$core$List$foldl,
						F2(
							function (key, menusSoFar) {
								return A2(
									$author$project$Shell$canProveUnsent,
									_List_fromArray(
										[key]),
									model.b) ? A2($author$project$MenuBridge$locallyRefuseUnsent, key, menusSoFar) : menusSoFar;
							}),
						model.k,
						operations);
				case 12:
					var operations = message.a;
					return A2($author$project$Shell$canProveUnsent, operations, model.b) ? A3($elm$core$List$foldl, $author$project$MenuBridge$locallyRefuseUnsent, model.k, operations) : model.k;
				default:
					return model.k;
			}
		}();
		var _v0 = function () {
			switch (message.$) {
				case 9:
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
								d_: A2($elm$core$Maybe$withDefault, next.d_, error)
							}),
						emitted);
				case 3:
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
		var advanced = A4($author$project$MenuBridge$advancePrepared, message, model.b, shell, menus);
		var finalShell = advanced.b;
		var settledMenus = A2($author$project$MenuBridge$reconcileWithShell, advanced.b, advanced.cC);
		var picker = A2(
			$elm$core$Maybe$andThen,
			function (current) {
				return (_Utils_eq(
					$author$project$Shell$capture(shell),
					$elm$core$Maybe$Just(current.b3)) && $author$project$Shell$available(shell)) ? $elm$core$Maybe$Just(current) : $elm$core$Maybe$Nothing;
			},
			model.J);
		return _Utils_Tuple2(
			_Utils_update(
				model,
				{
					k: settledMenus,
					J: picker,
					b: _Utils_update(
						finalShell,
						{
							d_: A2($elm$core$Maybe$withDefault, finalShell.d_, advanced.cK)
						})
				}),
			_Utils_ap(effects, advanced.R));
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
					{J: $elm$core$Maybe$Nothing}));
		} else {
			return _Utils_Tuple2(model, _List_Nil);
		}
	});
var $author$project$MenuBridge$cancelSelection = F3(
	function (token, shell, model) {
		var state = model;
		var _v0 = state.u;
		if (!_v0.$) {
			var slot = _v0.a;
			return _Utils_eq(slot.bh, token) ? A3($author$project$MenuBridge$cancelPrepared, 'Selection canceled before dispatch', shell, model) : A4($author$project$MenuBridge$answer, model, shell, _List_Nil, $elm$core$Maybe$Nothing);
		} else {
			return A4($author$project$MenuBridge$answer, model, shell, _List_Nil, $elm$core$Maybe$Nothing);
		}
	});
var $author$project$Shell$ArmPrepared = function (a) {
	return {$: 2, a: a};
};
var $author$project$MenuBridge$providerMatches = F2(
	function (captured, shell) {
		return _Utils_eq(
			shell.d,
			$elm$core$Maybe$Just(
				$author$project$Provider$nativeBinding(captured.bF))) && (_Utils_eq(
			$author$project$Shell$capture(shell),
			$elm$core$Maybe$Just(captured.b6)) && (_Utils_eq(
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.A;
				},
				$author$project$Provider$geometryObservation(captured.bF)),
			_Utils_eq(
				$author$project$Provider$geometryObservation(captured.bF),
				$elm$core$Maybe$Nothing) ? $elm$core$Maybe$Nothing : A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.A;
				},
				shell.ad)) && (_Utils_eq(
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.A;
				},
				shell.R.aa),
			$elm$core$Maybe$Just(
				$author$project$Provider$nativeContext(captured.bF))) && _Utils_eq(
			A2(
				$elm$core$Maybe$andThen,
				function (observed) {
					return A2(
						$author$project$ActionProjection$rootOf,
						$author$project$Provider$incarnation(captured.bF),
						observed.dk);
				},
				shell.R.aa),
			$elm$core$Maybe$Just(
				$author$project$Provider$incarnation(captured.bF))))));
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
			case 5:
				var id = message.a;
				var _v1 = state.u;
				if (!_v1.$) {
					var slot = _v1.a;
					return _Utils_eq(slot.cj, id) ? A3($author$project$MenuBridge$cancelPrepared, 'Selection canceled before dispatch', shell, model) : A4($author$project$MenuBridge$answer, model, shell, _List_Nil, $elm$core$Maybe$Nothing);
				} else {
					return A4(
						$author$project$MenuBridge$answer,
						_Utils_update(
							state,
							{
								aq: A2($author$project$Menu$update, message, state.aq).a
							}),
						shell,
						_List_Nil,
						$elm$core$Maybe$Nothing);
				}
			case 6:
				var binding = message.a;
				var _v2 = state.u;
				if (!_v2.$) {
					var slot = _v2.a;
					return _Utils_eq(slot.a8, binding) ? A3($author$project$MenuBridge$cancelPrepared, 'Selection authority retired', shell, model) : A4(
						$author$project$MenuBridge$answer,
						_Utils_update(
							state,
							{
								aq: A2($author$project$Menu$update, message, state.aq).a
							}),
						shell,
						_List_Nil,
						$elm$core$Maybe$Nothing);
				} else {
					return A4(
						$author$project$MenuBridge$answer,
						_Utils_update(
							state,
							{
								aq: A2($author$project$Menu$update, message, state.aq).a
							}),
						shell,
						_List_Nil,
						$elm$core$Maybe$Nothing);
				}
			case 7:
				var output = message.a;
				var generation = message.b;
				var _v3 = state.u;
				if (!_v3.$) {
					var slot = _v3.a;
					return (_Utils_eq(
						$author$project$Menu$outputId(
							$author$project$UInt64$string(
								$author$project$Provider$presentationScope(slot.X.bF).cn)),
						output) && _Utils_eq(
						$author$project$UInt64$string(
							$author$project$Provider$nativeContext(slot.X.bF).m),
						generation)) ? A3($author$project$MenuBridge$cancelPrepared, 'Selection output retired', shell, model) : A4(
						$author$project$MenuBridge$answer,
						_Utils_update(
							state,
							{
								aq: A2($author$project$Menu$update, message, state.aq).a
							}),
						shell,
						_List_Nil,
						$elm$core$Maybe$Nothing);
				} else {
					return A4(
						$author$project$MenuBridge$answer,
						_Utils_update(
							state,
							{
								aq: A2($author$project$Menu$update, message, state.aq).a
							}),
						shell,
						_List_Nil,
						$elm$core$Maybe$Nothing);
				}
			default:
				var preblocked = function () {
					var _v12 = _Utils_Tuple2(message, state.a_);
					if ((_v12.a.$ === 3) && (!_v12.b.$)) {
						var _v13 = _v12.a;
						var captured = _v12.b.a;
						return A3(
							$author$project$MenuBridge$blockedFor,
							$author$project$Provider$incarnation(captured.bF),
							shell,
							model);
					} else {
						return false;
					}
				}();
				var _v4 = A2($author$project$Menu$update, message, state.aq);
				var menu = _v4.a;
				var effects = _v4.b;
				var updated = _Utils_update(
					state,
					{aq: menu});
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
							var _v6 = _Utils_Tuple2(
								state.a_,
								$author$project$MenuBridge$operation(action));
							if ((!_v6.a.$) && (!_v6.b.$)) {
								var captured = _v6.a.a;
								if ((!_Utils_eq(
									$author$project$Provider$getBinding(captured.bF),
									binding)) || ((!A2($author$project$MenuBridge$providerMatches, captured, shell)) || (($author$project$Provider$actionProtocol(action) === 2) && ((!_Utils_eq(shell.dQ, $elm$core$Maybe$Nothing)) || (!_Utils_eq(shell.cQ, $elm$core$Maybe$Nothing)))))) {
									return rejected('Native window information changed; choose again');
								} else {
									var _v7 = _Utils_Tuple3(
										state.u,
										$author$project$UInt64$next(state.cp),
										_Utils_Tuple2(
											$author$project$Menu$snapshot(state.aq).aq,
											shell.R.aa));
									if ((((_v7.a.$ === 1) && (!_v7.b.$)) && (!_v7.c.a.$)) && (!_v7.c.b.$)) {
										var _v8 = _v7.a;
										var token = _v7.b.a;
										var _v9 = _v7.c;
										var view = _v9.a.a;
										var observed = _v9.b.a;
										var needsGeometry = !_Utils_eq(
											$author$project$Provider$geometryObservation(captured.bF),
											$elm$core$Maybe$Nothing);
										var closed = A2(
											$author$project$Menu$update,
											$author$project$Menu$Dismiss(view.bu),
											menu).a;
										var _v10 = A2($author$project$Shell$update, $author$project$Shell$Refresh, shell);
										var refreshing = _v10.a;
										var requests = _v10.b;
										var _v11 = refreshing.n;
										if (_v11.$ === 1) {
											return rejected('Post-close window observation unavailable');
										} else {
											var legacyRequest = _v11.a;
											if ($elm$core$List$isEmpty(requests) || (needsGeometry && _Utils_eq(refreshing.dQ, $elm$core$Maybe$Nothing))) {
												return rejected('Post-close geometry observation unavailable');
											} else {
												var slot = {
													dB: action,
													X: captured,
													cg: dispatch,
													cR: shell.cR,
													aV: !needsGeometry,
													aF: refreshing.dQ,
													aX: false,
													aJ: legacyRequest,
													ci: $author$project$ActionProjection$windows(observed.dk),
													by: local,
													cj: view.bu,
													a8: binding,
													bh: token
												};
												return A4(
													$author$project$MenuBridge$answer,
													_Utils_update(
														state,
														{
															aq: closed,
															u: $elm$core$Maybe$Just(slot),
															cp: token
														}),
													_Utils_update(
														refreshing,
														{cH: true}),
													_Utils_ap(
														requests,
														_List_fromArray(
															[
																$author$project$Shell$ArmPrepared(token)
															])),
													$elm$core$Maybe$Nothing);
											}
										}
									} else {
										return rejected('A prepared selection is already pending or exhausted');
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
	var _v0 = $author$project$MenuBridge$menuSnapshot(model.k).aq;
	if (_v0.$ === 1) {
		return model;
	} else {
		var view = _v0.a;
		var result = A3(
			$author$project$MenuBridge$menuEvent,
			$author$project$Menu$Dismiss(view.bu),
			model.b,
			model.k);
		return _Utils_update(
			model,
			{k: result.cC});
	}
};
var $author$project$MenuBridge$expirePrepared = F3(
	function (token, shell, model) {
		var state = model;
		var _v0 = state.u;
		if (!_v0.$) {
			var slot = _v0.a;
			return _Utils_eq(slot.bh, token) ? A3($author$project$MenuBridge$cancelPrepared, 'Window information took too long. Choose again.', shell, model) : A4($author$project$MenuBridge$answer, model, shell, _List_Nil, $elm$core$Maybe$Nothing);
		} else {
			return A4($author$project$MenuBridge$answer, model, shell, _List_Nil, $elm$core$Maybe$Nothing);
		}
	});
var $author$project$Menu$Open = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$Provider$toOpen = function (_v0) {
	var value = _v0;
	return A2($author$project$Menu$Open, value.d, value.dX);
};
var $author$project$MenuBridge$open = F2(
	function (provider, model) {
		var state = model;
		if (!_Utils_eq(state.u, $elm$core$Maybe$Nothing)) {
			return model;
		} else {
			var _v0 = $author$project$MenuBridge$providerStamp(provider);
			if (_v0.$ === 1) {
				return model;
			} else {
				var stamp = _v0.a;
				var before = $author$project$Menu$snapshot(state.aq);
				var _v1 = A2(
					$author$project$Menu$update,
					$author$project$Provider$toOpen(provider),
					state.aq);
				var menu = _v1.a;
				return _Utils_eq(
					$author$project$Menu$snapshot(menu).aq,
					before.aq) ? model : _Utils_update(
					state,
					{
						aq: menu,
						a_: $elm$core$Maybe$Just(
							{bF: provider, b6: stamp})
					});
			}
		}
	});
var $author$project$Taskbar$selection = function (entry) {
	return (!entry.ca) ? $author$project$Taskbar$Unavailable : A2(
		$author$project$Taskbar$Apply,
		entry.a7 ? $author$project$Effects$Restore : $author$project$Effects$Activate,
		entry.v);
};
var $author$project$TaskbarShell$valid = F2(
	function (scope, model) {
		return _Utils_eq(
			$author$project$MenuBridge$preparedSnapshot(model.k),
			$elm$core$Maybe$Nothing) && (_Utils_eq(
			$author$project$Shell$capture(model.b),
			$elm$core$Maybe$Just(scope)) && $author$project$Shell$available(model.b));
	});
var $author$project$TaskbarShell$update = F2(
	function (message, model) {
		switch (message.$) {
			case 4:
				var provider = message.a;
				var menus = A2($author$project$MenuBridge$open, provider, model.k);
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							k: menus,
							J: _Utils_eq(menus, model.k) ? model.J : $elm$core$Maybe$Nothing
						}),
					_List_Nil);
			case 5:
				var event = message.a;
				var result = A3($author$project$MenuBridge$menuEvent, event, model.b, model.k);
				var shell = result.b;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							k: result.cC,
							J: $elm$core$List$isEmpty(result.R) ? model.J : $elm$core$Maybe$Nothing,
							b: _Utils_update(
								shell,
								{
									d_: A2($elm$core$Maybe$withDefault, shell.d_, result.cK)
								})
						}),
					result.R);
			case 7:
				var token = message.a;
				var result = A3($author$project$MenuBridge$cancelSelection, token, model.b, model.k);
				var shell = result.b;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							k: result.cC,
							b: _Utils_update(
								shell,
								{
									d_: A2($elm$core$Maybe$withDefault, shell.d_, result.cK)
								})
						}),
					result.R);
			case 6:
				var token = message.a;
				var result = A3($author$project$MenuBridge$expirePrepared, token, model.b, model.k);
				var shell = result.b;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							k: result.cC,
							b: _Utils_update(
								shell,
								{
									d_: A2($elm$core$Maybe$withDefault, shell.d_, result.cK)
								})
						}),
					result.R);
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
								return _Utils_eq(group.ap, key);
							},
							$author$project$TaskbarShell$groups(model)));
					if (_v1.$ === 1) {
						return _Utils_Tuple2(model, _List_Nil);
					} else {
						var group = _v1.a;
						var base = $author$project$TaskbarShell$dismissMenus(model);
						var _v2 = A2($author$project$Taskbar$primary, false, group.am);
						if (_v2.$ === 1) {
							var _v3 = $author$project$UInt64$next(model.dP);
							if (!_v3.$) {
								var generation = _v3.a;
								return _Utils_Tuple2(
									_Utils_update(
										base,
										{
											dP: generation,
											J: $elm$core$Maybe$Just(
												{dP: generation, ap: key, b3: scope})
										}),
									_List_Nil);
							} else {
								return _Utils_Tuple2(
									_Utils_update(
										base,
										{J: $elm$core$Maybe$Nothing}),
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
				var _v4 = model.J;
				if (!_v4.$) {
					var picker = _v4.a;
					return ((!A2($author$project$TaskbarShell$valid, scope, model)) || ((!_Utils_eq(picker.b3, scope)) || (!_Utils_eq(picker.dP, generation)))) ? _Utils_Tuple2(model, _List_Nil) : A2(
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
										return _Utils_eq(family.v, root);
									},
									A2(
										$elm$core$List$concatMap,
										function ($) {
											return $.am;
										},
										A2(
											$elm$core$List$filter,
											function (group) {
												return _Utils_eq(group.ap, picker.ap);
											},
											$author$project$TaskbarShell$groups(model)))))));
				} else {
					return _Utils_Tuple2(model, _List_Nil);
				}
			default:
				var scope = message.a;
				var generation = message.b;
				var _v5 = model.J;
				if (!_v5.$) {
					var picker = _v5.a;
					return (_Utils_eq(picker.b3, scope) && _Utils_eq(picker.dP, generation)) ? _Utils_Tuple2(
						_Utils_update(
							model,
							{J: $elm$core$Maybe$Nothing}),
						_List_Nil) : _Utils_Tuple2(model, _List_Nil);
				} else {
					return _Utils_Tuple2(model, _List_Nil);
				}
		}
	});
var $author$project$Snap$valid = F2(
	function (current, choice) {
		return _Utils_eq(current.d, choice.bF.d) && (_Utils_eq(current.A.dY, choice.bF.A.dY) && (_Utils_eq(current.A.dM, choice.bF.A.dM) && (_Utils_eq(current.A.m, choice.bF.A.m) && A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (window) {
					return (current.dE || window.dK) && ((!window.a7) && (window.bq && ((!window.bs) && ((!window.dO) && (_Utils_eq(window.co, $elm$core$Maybe$Nothing) && ((!window.c3) && ((!window.ce) && (_Utils_eq(
						A2(
							$elm$core$Maybe$map,
							function ($) {
								return $.b5;
							},
							A2($author$project$GeometryProjection$window, choice.ed, choice.bF)),
						$elm$core$Maybe$Just(window.b5)) && _Utils_eq(
						$author$project$Snap$proposal(
							_Utils_update(
								choice,
								{bF: current})),
						A2(
							$elm$core$Maybe$map,
							function (prior) {
								return _Utils_update(
									prior,
									{A: current.A});
							},
							$author$project$Snap$proposal(choice)))))))))));
				},
				A2($author$project$GeometryProjection$window, choice.ed, current))))));
	});
var $author$project$Desktop$windowBase = F2(
	function (message, model) {
		var _v0 = A2($author$project$TaskbarShell$update, message, model.a);
		var windows = _v0.a;
		var effects = _v0.b;
		var changed = !_Utils_eq(windows.b.d, model.a.b.d);
		var disconnected = !windows.b.G;
		var pins = (disconnected || changed) ? $author$project$Pins$initial : model.y;
		var launch = disconnected ? $author$project$Launch$disconnect(model.p) : (changed ? A2(
			$elm$core$Maybe$withDefault,
			$author$project$Launch$disconnect(model.p),
			A2(
				$elm$core$Maybe$map,
				function (binding) {
					return A2(
						$author$project$Launch$bind,
						$author$project$Desktop$host(binding),
						model.p);
				},
				windows.b.d)) : model.p);
		var read = (changed && (!disconnected)) ? A2(
			$elm$core$Maybe$andThen,
			function (binding) {
				return A2(
					$elm$core$Maybe$map,
					function (request) {
						return _Utils_Tuple2(binding, request);
					},
					$author$project$UInt64$next(model.o));
			},
			windows.b.d) : $elm$core$Maybe$Nothing;
		return _Utils_Tuple2(
			((disconnected || changed) ? $author$project$Desktop$advance : $elm$core$Basics$identity)(
				_Utils_update(
					model,
					{
						ak: (disconnected || changed) ? $elm$core$Maybe$Nothing : model.ak,
						aS: (disconnected || changed) ? $elm$core$Maybe$Nothing : model.aS,
						j: (disconnected || (changed || (windows.b.G === 3))) ? $elm$core$Maybe$Nothing : model.j,
						E: (disconnected || changed) ? '' : model.E,
						n: (disconnected || changed) ? A2($elm$core$Maybe$map, $elm$core$Tuple$second, read) : model.n,
						p: launch,
						F: (disconnected || (changed || _Utils_eq(
							$author$project$MenuBridge$menuSnapshot(windows.k).aq,
							$elm$core$Maybe$Nothing))) ? $elm$core$Maybe$Nothing : model.F,
						O: (disconnected || (changed || (windows.b.G === 3))) ? $elm$core$Maybe$Nothing : model.O,
						t: (disconnected || (changed || (windows.b.G === 3))) ? false : model.t,
						ag: (disconnected || changed) ? $elm$core$Maybe$Nothing : model.ag,
						y: pins,
						o: A2(
							$elm$core$Maybe$withDefault,
							model.o,
							A2($elm$core$Maybe$map, $elm$core$Tuple$second, read)),
						r: (disconnected || changed) ? $elm$core$Maybe$Nothing : model.r,
						w: (disconnected || (changed || (windows.b.G === 3))) ? $elm$core$Maybe$Nothing : A2(
							$elm$core$Maybe$andThen,
							function (choice) {
								var _v1 = windows.b.ad;
								if (_v1.$ === 1) {
									return $elm$core$Maybe$Just(choice);
								} else {
									var geometry = _v1.a;
									return A2($author$project$Snap$valid, geometry, choice) ? $elm$core$Maybe$Just(
										_Utils_update(
											choice,
											{bF: geometry})) : $elm$core$Maybe$Nothing;
								}
							},
							model.w),
						e: (disconnected || (changed || (windows.b.G === 3))) ? A2(
							$author$project$Switcher$cancel,
							$author$project$Switcher$generation(model.e),
							model.e) : model.e,
						ai: (disconnected || (changed || (windows.b.G === 3))) ? $elm$core$Maybe$Nothing : model.ai,
						aj: (disconnected || (changed || (windows.b.G === 3))) ? $elm$core$Maybe$Nothing : model.aj,
						a: windows
					})),
			_Utils_ap(
				A2(
					$elm$core$Maybe$withDefault,
					_List_Nil,
					A2(
						$elm$core$Maybe$map,
						function (_v2) {
							var binding = _v2.a;
							var request = _v2.b;
							return _List_fromArray(
								[
									A2($author$project$Desktop$catalogRequest, binding, request)
								]);
						},
						read)),
				_Utils_ap(
					A2($elm$core$List$map, $author$project$Desktop$WindowEffect, effects),
					function () {
						var _v3 = _Utils_Tuple3(model.a.J, windows.J, message);
						if (!_v3.b.$) {
							var prior = _v3.a;
							var picker = _v3.b.a;
							return _Utils_eq(
								A2(
									$elm$core$Maybe$map,
									function ($) {
										return $.dP;
									},
									prior),
								$elm$core$Maybe$Just(picker.dP)) ? _List_Nil : A2(
								$elm$core$Maybe$withDefault,
								_List_Nil,
								A2(
									$elm$core$Maybe$map,
									function (family) {
										return _List_fromArray(
											[
												$author$project$Desktop$Focus(
												'picker:' + ($author$project$Shell$stampKey(picker.b3) + (':' + ($author$project$UInt64$string(picker.dP) + (':' + $author$project$UInt64$string(family.v))))))
											]);
									},
									$elm$core$List$head(
										A2(
											$elm$core$List$filter,
											function ($) {
												return $.ca;
											},
											A2(
												$elm$core$List$concatMap,
												function ($) {
													return $.am;
												},
												A2(
													$elm$core$List$filter,
													function (group) {
														return _Utils_eq(group.ap, picker.ap);
													},
													$author$project$TaskbarShell$groups(windows)))))));
						} else {
							if ((!_v3.a.$) && (_v3.c.$ === 3)) {
								var picker = _v3.a.a;
								var _v4 = _v3.b;
								var _v5 = _v3.c;
								var scope = _v5.a;
								var generation = _v5.b;
								return (_Utils_eq(picker.b3, scope) && (_Utils_eq(picker.dP, generation) && _Utils_eq(
									$author$project$Shell$capture(windows.b),
									$elm$core$Maybe$Just(scope)))) ? _List_fromArray(
									[
										$author$project$Desktop$Focus(
										'group:' + ($author$project$Shell$stampKey(scope) + (':' + picker.ap)))
									]) : _List_Nil;
							} else {
								return _List_Nil;
							}
						}
					}())));
	});
var $author$project$Desktop$chooseFamily = F2(
	function (family, model) {
		var _v0 = _Utils_Tuple2(model.a.b.d, model.a.b.R.aa);
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var binding = _v0.a.a;
			var observed = _v0.b.a;
			if ((!_Utils_eq(model.j, $elm$core$Maybe$Nothing)) || A3($author$project$MenuBridge$blockedFor, family.v, model.a.b, model.a.k)) {
				return _Utils_Tuple2(
					$author$project$Desktop$retireSwitcher(model),
					_List_Nil);
			} else {
				var _v1 = A2(
					$author$project$Desktop$windowBase,
					$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
					$author$project$Desktop$retireSwitcher(
						_Utils_update(
							model,
							{E: '', t: false})));
				var next = _v1.a;
				var effects = _v1.b;
				var _v2 = next.a.b.n;
				if (!_v2.$) {
					var request = _v2.a;
					var token = A2($author$project$Desktop$ChoiceToken, binding, request);
					return _Utils_Tuple2(
						_Utils_update(
							next,
							{
								j: $elm$core$Maybe$Just(
									{
										b9: family.b9,
										d: binding,
										aC: A2(
											$elm$core$Maybe$map,
											function ($) {
												return $.dP;
											},
											model.O),
										m: observed.A.m,
										aZ: $elm$core$Maybe$Nothing,
										v: family.v,
										bh: token
									})
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
		} else {
			return _Utils_Tuple2(
				$author$project$Desktop$retireSwitcher(model),
				_List_Nil);
		}
	});
var $author$project$Switcher$fresh = function (token) {
	var _v0 = $author$project$Switcher$initial;
	var model = _v0;
	return _Utils_update(
		model,
		{dP: token, G: 1});
};
var $author$project$Switcher$prepare = F2(
	function (token, model) {
		var _v0 = A2($author$project$UInt64$compare, token, model.dP);
		switch (_v0) {
			case 2:
				return _Utils_eq(token, $author$project$UInt64$zero) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(
					$author$project$Switcher$fresh(token));
			case 1:
				return $author$project$Switcher$writable(model) ? $elm$core$Maybe$Just(model) : $elm$core$Maybe$Nothing;
			default:
				return $elm$core$Maybe$Nothing;
		}
	});
var $author$project$Switcher$Resolved = 3;
var $elm$core$Dict$member = F2(
	function (key, dict) {
		var _v0 = A2($elm$core$Dict$get, key, dict);
		if (!_v0.$) {
			return true;
		} else {
			return false;
		}
	});
var $author$project$Switcher$contiguous = F2(
	function (through, model) {
		return (through > 0) && A2(
			$elm$core$List$all,
			function (ordinal) {
				return A2($elm$core$Dict$member, ordinal, model.a1);
			},
			A2($elm$core$List$range, 1, through));
	});
var $author$project$Switcher$settle = function (model) {
	var complete = A2(
		$elm$core$Maybe$withDefault,
		A2(
			$author$project$Switcher$contiguous,
			$author$project$Switcher$lastOrdinal(model),
			model),
		A2(
			$elm$core$Maybe$map,
			function (ordinal) {
				return A2($author$project$Switcher$contiguous, ordinal, model);
			},
			model.b1));
	if ((!model.bc) || (!complete)) {
		return _Utils_Tuple2(
			_Utils_update(
				model,
				{G: 1}),
			$elm$core$Maybe$Nothing);
	} else {
		if ($elm$core$List$isEmpty(model.bp)) {
			return _Utils_Tuple2(
				_Utils_update(
					model,
					{G: 3}),
				$elm$core$Maybe$Nothing);
		} else {
			if (!_Utils_eq(model.b1, $elm$core$Maybe$Nothing)) {
				var current = _Utils_update(
					model,
					{G: 3});
				return _Utils_Tuple2(
					current,
					$author$project$Switcher$selected(current));
			} else {
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{G: 2}),
					$elm$core$Maybe$Nothing);
			}
		}
	}
};
var $author$project$Switcher$release = F3(
	function (token, ordinal, original) {
		var current = original;
		if ((ordinal < 1) || (ordinal > 4096)) {
			return _Utils_Tuple2(original, $elm$core$Maybe$Nothing);
		} else {
			var _v0 = A2($author$project$Switcher$prepare, token, current);
			if (_v0.$ === 1) {
				return _Utils_Tuple2(original, $elm$core$Maybe$Nothing);
			} else {
				var model = _v0.a;
				if (_Utils_cmp(
					ordinal,
					$author$project$Switcher$lastOrdinal(model)) < 0) {
					return _Utils_Tuple2(original, $elm$core$Maybe$Nothing);
				} else {
					var _v1 = model.b1;
					if (!_v1.$) {
						return _Utils_Tuple2(original, $elm$core$Maybe$Nothing);
					} else {
						return $author$project$Switcher$settle(
							_Utils_update(
								model,
								{
									b1: $elm$core$Maybe$Just(ordinal)
								}));
					}
				}
			}
		}
	});
var $author$project$Switcher$commit = F2(
	function (token, original) {
		var model = original;
		return ((!_Utils_eq(token, model.dP)) || (model.G !== 2)) ? _Utils_Tuple2(original, $elm$core$Maybe$Nothing) : A3(
			$author$project$Switcher$release,
			token,
			$author$project$Switcher$lastOrdinal(model),
			original);
	});
var $author$project$Pins$Snapshot = F2(
	function (revision, identities) {
		return {dU: identities, dj: revision};
	});
var $author$project$Pins$identityDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (s) {
		return ((!$elm$core$String$isEmpty(s)) && (($elm$core$String$length(s) <= 256) && (!A2(
			$elm$core$String$any,
			function (c) {
				return ($elm$core$Char$toCode(c) < 32) || ($elm$core$Char$toCode(c) === 127);
			},
			s)))) ? $elm$json$Json$Decode$succeed(s) : $elm$json$Json$Decode$fail('Pin identity');
	},
	$elm$json$Json$Decode$string);
var $author$project$Pins$strict = F2(
	function (fields, child) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? child : $elm$json$Json$Decode$fail('Pin fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$Pins$bytes = A2(
	$elm$core$String$foldl,
	F2(
		function (c, total) {
			return total + (($elm$core$Char$toCode(c) <= 127) ? 1 : (($elm$core$Char$toCode(c) <= 2047) ? 2 : (($elm$core$Char$toCode(c) <= 65535) ? 3 : 4)));
		}),
	0);
var $author$project$Pins$valid = function (values) {
	return ($elm$core$List$length(values) <= 32) && (_Utils_eq(
		$elm$core$List$length(values),
		$elm$core$List$length(
			A3(
				$elm$core$List$foldl,
				F2(
					function (s, seen) {
						return A2($elm$core$List$member, s, seen) ? seen : A2($elm$core$List$cons, s, seen);
					}),
				_List_Nil,
				values))) && ($author$project$Pins$bytes(
		A2(
			$elm$json$Json$Encode$encode,
			0,
			A2($elm$json$Json$Encode$list, $elm$json$Json$Encode$string, values))) <= 3000));
};
var $author$project$Pins$decoder = A2(
	$author$project$Pins$strict,
	_List_fromArray(
		['revision', 'identities']),
	A3(
		$elm$json$Json$Decode$map2,
		$author$project$Pins$Snapshot,
		A2(
			$elm$json$Json$Decode$field,
			'revision',
			A2(
				$elm$json$Json$Decode$andThen,
				function (n) {
					return (!_Utils_eq(n, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(n) : $elm$json$Json$Decode$fail('Pin revision');
				},
				$author$project$UInt64$decoder)),
		A2(
			$elm$json$Json$Decode$field,
			'identities',
			A2(
				$elm$json$Json$Decode$andThen,
				function (values) {
					return $author$project$Pins$valid(values) ? $elm$json$Json$Decode$succeed(values) : $elm$json$Json$Decode$fail('Pin bounds');
				},
				$elm$json$Json$Decode$list($author$project$Pins$identityDecoder)))));
var $author$project$Switcher$lastStep = function (_v0) {
	var model = _v0;
	return $author$project$Switcher$lastOrdinal(model);
};
var $author$project$Pins$move = F3(
	function (identity, direction, values) {
		var index = A2(
			$elm$core$Maybe$map,
			$elm$core$Tuple$first,
			$elm$core$List$head(
				A2(
					$elm$core$List$filter,
					function (_v2) {
						var s = _v2.b;
						return _Utils_eq(s, identity);
					},
					A2($elm$core$List$indexedMap, $elm$core$Tuple$pair, values))));
		var at = function (n) {
			return $elm$core$List$head(
				A2($elm$core$List$drop, n, values));
		};
		if (!index.$) {
			var n = index.a;
			var target = n + direction;
			if ((!A2(
				$elm$core$List$member,
				direction,
				_List_fromArray(
					[-1, 1]))) || ((target < 0) || (_Utils_cmp(
				target,
				$elm$core$List$length(values)) > -1))) {
				return values;
			} else {
				var _v1 = at(target);
				if (!_v1.$) {
					var other = _v1.a;
					return A2(
						$elm$core$List$indexedMap,
						F2(
							function (i, s) {
								return _Utils_eq(i, n) ? other : (_Utils_eq(i, target) ? identity : s);
							}),
						values);
				} else {
					return values;
				}
			}
		} else {
			return values;
		}
	});
var $author$project$Desktop$NativeChord = F8(
	function (generation, roots, history, origin, steps, released, cancelled, consumed) {
		return {bO: cancelled, bS: consumed, dP: generation, bt: history, bZ: origin, b1: released, ah: roots, a1: steps};
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
var $author$project$Desktop$nativeChordDecoder = function () {
	var positive = A2(
		$elm$json$Json$Decode$andThen,
		function (value) {
			return _Utils_eq(value, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero chord identity') : $elm$json$Json$Decode$succeed(value);
		},
		$author$project$UInt64$decoder);
	var identities = A2(
		$elm$json$Json$Decode$andThen,
		function (rows) {
			return (($elm$core$List$length(rows) <= 256) && _Utils_eq(
				$elm$core$List$length(
					A3(
						$elm$core$List$foldl,
						F2(
							function (root, unique) {
								return A2($elm$core$List$member, root, unique) ? unique : A2($elm$core$List$cons, root, unique);
							}),
						_List_Nil,
						rows)),
				$elm$core$List$length(rows))) ? $elm$json$Json$Decode$succeed(rows) : $elm$json$Json$Decode$fail('Chord membership');
		},
		$elm$json$Json$Decode$list(positive));
	var direction = A2(
		$elm$json$Json$Decode$andThen,
		function (value) {
			return (value === 1) ? $elm$json$Json$Decode$succeed(0) : (_Utils_eq(value, -1) ? $elm$json$Json$Decode$succeed(1) : $elm$json$Json$Decode$fail('Chord direction'));
		},
		$elm$json$Json$Decode$int);
	var steps = A2(
		$elm$json$Json$Decode$andThen,
		function (rows) {
			return ($elm$core$List$length(rows) <= 4096) ? $elm$json$Json$Decode$succeed(rows) : $elm$json$Json$Decode$fail('Chord ordinals');
		},
		$elm$json$Json$Decode$list(direction));
	return A2(
		$elm$json$Json$Decode$andThen,
		function (chord) {
			return (_Utils_eq(
				_Utils_eq(chord.dP, $author$project$UInt64$zero),
				$elm$core$List$isEmpty(chord.a1)) && A2(
				$elm$core$List$all,
				function (root) {
					return A2($elm$core$List$member, root, chord.ah);
				},
				chord.bt)) ? $elm$json$Json$Decode$succeed(chord) : $elm$json$Json$Decode$fail('Chord entry/history');
		},
		A2(
			$author$project$Desktop$strict,
			_List_fromArray(
				['generation', 'roots', 'history', 'origin', 'steps', 'released', 'cancelled', 'consumed']),
			A9(
				$elm$json$Json$Decode$map8,
				$author$project$Desktop$NativeChord,
				A2($elm$json$Json$Decode$field, 'generation', $author$project$UInt64$decoder),
				A2($elm$json$Json$Decode$field, 'roots', identities),
				A2($elm$json$Json$Decode$field, 'history', identities),
				A2(
					$elm$json$Json$Decode$field,
					'origin',
					$elm$json$Json$Decode$nullable(positive)),
				A2($elm$json$Json$Decode$field, 'steps', steps),
				A2($elm$json$Json$Decode$field, 'released', $elm$json$Json$Decode$bool),
				A2($elm$json$Json$Decode$field, 'cancelled', $elm$json$Json$Decode$bool),
				A2($elm$json$Json$Decode$field, 'consumed', $elm$json$Json$Decode$bool))));
}();
var $author$project$Switcher$delta = function (direction) {
	return (!direction) ? 1 : (-1);
};
var $elm$core$Basics$modBy = _Basics_modBy;
var $author$project$Switcher$navigate = F2(
	function (direction, original) {
		var model = original;
		if ((model.G !== 2) || ((!_Utils_eq(model.b1, $elm$core$Maybe$Nothing)) || $elm$core$List$isEmpty(model.bp))) {
			return original;
		} else {
			var position = A2(
				$elm$core$Basics$modBy,
				$elm$core$List$length(model.bp),
				model.eb + $author$project$Switcher$delta(direction));
			var root = A2(
				$elm$core$Maybe$withDefault,
				$author$project$UInt64$zero,
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.v;
					},
					$elm$core$List$head(
						A2($elm$core$List$drop, position, model.bp))));
			return _Utils_update(
				model,
				{
					aB: $elm$core$Maybe$Just(
						{
							v: root,
							b8: $author$project$Switcher$lastOrdinal(model)
						}),
					eb: position
				});
		}
	});
var $author$project$Pins$observe = F2(
	function (snapshot, model) {
		if (snapshot.$ === 1) {
			return _Utils_update(
				model,
				{d_: 'Pin storage unavailable. Refresh applications to try again.', d4: $elm$core$Maybe$Nothing, bF: $elm$core$Maybe$Nothing});
		} else {
			var value = snapshot.a;
			return A2(
				$elm$core$Maybe$withDefault,
				false,
				A2(
					$elm$core$Maybe$map,
					function (old) {
						return !A2($author$project$UInt64$compare, value.dj, old.dj);
					},
					model.bF)) ? model : _Utils_update(
				model,
				{
					d_: '',
					d4: $elm$core$Maybe$Nothing,
					bF: $elm$core$Maybe$Just(value)
				});
		}
	});
var $author$project$Desktop$historyRequest = F2(
	function (binding, request) {
		return $author$project$Desktop$Send(
			$elm$json$Json$Encode$object(
				_List_fromArray(
					[
						_Utils_Tuple2(
						'protocolVersion',
						$elm$json$Json$Encode$int(3)),
						_Utils_Tuple2(
						'kind',
						$elm$json$Json$Encode$string('activation-history-request')),
						_Utils_Tuple2(
						'binding',
						$author$project$Binding$encode(binding)),
						_Utils_Tuple2(
						'requestId',
						$elm$json$Json$Encode$string(
							$author$project$UInt64$string(request)))
					])));
	});
var $author$project$Desktop$readSwitcherHistory = function (model) {
	var _v0 = _Utils_Tuple2(
		model.a.b.d,
		$author$project$UInt64$next(model.o));
	if ((!_v0.a.$) && (!_v0.b.$)) {
		var binding = _v0.a.a;
		var request = _v0.b.a;
		return _Utils_Tuple2(
			_Utils_update(
				model,
				{
					o: request,
					ai: $elm$core$Maybe$Just(request),
					aj: $elm$core$Maybe$Nothing
				}),
			_List_fromArray(
				[
					A2($author$project$Desktop$historyRequest, binding, request)
				]));
	} else {
		return _Utils_Tuple2(
			$author$project$Desktop$retireSwitcher(model),
			_List_Nil);
	}
};
var $author$project$Launch$Refused = 1;
var $author$project$Launch$Submitted = 0;
var $author$project$Launch$Intent = F4(
	function (request, lifetime, generation, entry) {
		return {cJ: entry, dP: generation, dY: lifetime, o: request};
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
var $author$project$Launch$receiptDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (receipt) {
		return ((receipt.ds !== 1) || (receipt.cX !== 'launch-outcome')) ? $elm$json$Json$Decode$fail('Launch receipt version/kind') : (((receipt.b7 === 'Submitted') && (receipt.b0 === 'native-submission-accepted')) ? $elm$json$Json$Decode$succeed(
			_Utils_Tuple2(receipt.K, 0)) : (((receipt.b7 === 'Unknown') && (receipt.b0 === 'submission-not-confirmed')) ? $elm$json$Json$Decode$succeed(
			_Utils_Tuple2(receipt.K, 2)) : (((receipt.b7 === 'Refused') && A2(
			$elm$core$List$member,
			receipt.b0,
			_List_fromArray(
				['retired-authority', 'request-reuse', 'retired-request', 'catalog-unavailable', 'stale-catalog', 'removed-entry', 'native-entry-unavailable', 'desktop-entry-raced']))) ? $elm$json$Json$Decode$succeed(
			_Utils_Tuple2(receipt.K, 1)) : $elm$json$Json$Decode$fail('Launch receipt outcome'))));
	},
	A2(
		$author$project$Launch$strict,
		_List_fromArray(
			['catalogProtocol', 'kind', 'intent', 'status', 'reason']),
		A6(
			$elm$json$Json$Decode$map5,
			F5(
				function (version, kind, intent, state, reason) {
					return {K: intent, cX: kind, b0: reason, b7: state, ds: version};
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
			model.G,
			A2($elm$json$Json$Decode$decodeValue, $author$project$Launch$receiptDecoder, raw));
		if ((_v0.a.$ === 1) && (!_v0.b.$)) {
			var _v1 = _v0.a;
			var owner = _v1.a;
			var intent = _v1.b;
			var _v2 = _v0.b.a;
			var received = _v2.a;
			var result = _v2.b;
			return (_Utils_eq(host, owner) && (_Utils_eq(
				model.aG,
				$elm$core$Maybe$Just(owner)) && _Utils_eq(received, intent))) ? $author$project$Launch$advance(
				_Utils_update(
					model,
					{
						G: A2($author$project$Launch$Settled, intent, result)
					})) : current;
		} else {
			return current;
		}
	});
var $author$project$Pins$receive = F4(
	function (request, status, snapshot, model) {
		var _v0 = model.d4;
		if (!_v0.$) {
			var pending = _v0.a;
			return (!_Utils_eq(pending.o, request)) ? model : (((status === 'Saved') && A2(
				$elm$core$Maybe$withDefault,
				false,
				A2(
					$elm$core$Maybe$map,
					function (s) {
						return _Utils_eq(s.dU, pending.dU) && A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (old) {
									return A2($author$project$UInt64$compare, s.dj, old.dj) === 2;
								},
								model.bF));
					},
					snapshot))) ? _Utils_update(
				model,
				{d_: 'Pin order saved.', d4: $elm$core$Maybe$Nothing, bF: snapshot}) : ((status === 'Refused') ? _Utils_update(
				model,
				{d_: 'Pin change refused. Refresh applications and choose again.', d4: $elm$core$Maybe$Nothing}) : _Utils_update(
				model,
				{d_: 'Pin save not confirmed. Refresh applications to read the order; the change will not be repeated.'})));
		} else {
			return model;
		}
	});
var $author$project$Menu$abandonPrepared = F3(
	function (local, bound, _v0) {
		var state = _v0;
		return _Utils_update(
			state,
			{
				aq: $elm$core$Maybe$Nothing,
				d3: A2(
					$elm$core$List$filter,
					function (entry) {
						return !(_Utils_eq(entry.bu, local) && (_Utils_eq(entry.d, bound) && (!entry.aQ)));
					},
					state.d3)
			});
	});
var $author$project$MenuBridge$retireChoices = function (_v0) {
	var state = _v0;
	var menu = function () {
		var _v2 = state.u;
		if (!_v2.$) {
			var slot = _v2.a;
			return A3($author$project$Menu$abandonPrepared, slot.by, slot.a8, state.aq);
		} else {
			return state.aq;
		}
	}();
	var closed = function () {
		var _v1 = $author$project$Menu$snapshot(menu).aq;
		if (!_v1.$) {
			var view = _v1.a;
			return A2(
				$author$project$Menu$update,
				$author$project$Menu$Dismiss(view.bu),
				menu).a;
		} else {
			return menu;
		}
	}();
	return _Utils_update(
		state,
		{aq: closed, u: $elm$core$Maybe$Nothing});
};
var $elm$core$List$sum = function (numbers) {
	return A3($elm$core$List$foldl, $elm$core$Basics$add, 0, numbers);
};
var $elm$core$List$takeReverse = F3(
	function (n, list, kept) {
		takeReverse:
		while (true) {
			if (n <= 0) {
				return kept;
			} else {
				if (!list.b) {
					return kept;
				} else {
					var x = list.a;
					var xs = list.b;
					var $temp$n = n - 1,
						$temp$list = xs,
						$temp$kept = A2($elm$core$List$cons, x, kept);
					n = $temp$n;
					list = $temp$list;
					kept = $temp$kept;
					continue takeReverse;
				}
			}
		}
	});
var $elm$core$List$takeTailRec = F2(
	function (n, list) {
		return $elm$core$List$reverse(
			A3($elm$core$List$takeReverse, n, list, _List_Nil));
	});
var $elm$core$List$takeFast = F3(
	function (ctr, n, list) {
		if (n <= 0) {
			return _List_Nil;
		} else {
			var _v0 = _Utils_Tuple2(n, list);
			_v0$1:
			while (true) {
				_v0$5:
				while (true) {
					if (!_v0.b.b) {
						return list;
					} else {
						if (_v0.b.b.b) {
							switch (_v0.a) {
								case 1:
									break _v0$1;
								case 2:
									var _v2 = _v0.b;
									var x = _v2.a;
									var _v3 = _v2.b;
									var y = _v3.a;
									return _List_fromArray(
										[x, y]);
								case 3:
									if (_v0.b.b.b.b) {
										var _v4 = _v0.b;
										var x = _v4.a;
										var _v5 = _v4.b;
										var y = _v5.a;
										var _v6 = _v5.b;
										var z = _v6.a;
										return _List_fromArray(
											[x, y, z]);
									} else {
										break _v0$5;
									}
								default:
									if (_v0.b.b.b.b && _v0.b.b.b.b.b) {
										var _v7 = _v0.b;
										var x = _v7.a;
										var _v8 = _v7.b;
										var y = _v8.a;
										var _v9 = _v8.b;
										var z = _v9.a;
										var _v10 = _v9.b;
										var w = _v10.a;
										var tl = _v10.b;
										return (ctr > 1000) ? A2(
											$elm$core$List$cons,
											x,
											A2(
												$elm$core$List$cons,
												y,
												A2(
													$elm$core$List$cons,
													z,
													A2(
														$elm$core$List$cons,
														w,
														A2($elm$core$List$takeTailRec, n - 4, tl))))) : A2(
											$elm$core$List$cons,
											x,
											A2(
												$elm$core$List$cons,
												y,
												A2(
													$elm$core$List$cons,
													z,
													A2(
														$elm$core$List$cons,
														w,
														A3($elm$core$List$takeFast, ctr + 1, n - 4, tl)))));
									} else {
										break _v0$5;
									}
							}
						} else {
							if (_v0.a === 1) {
								break _v0$1;
							} else {
								break _v0$5;
							}
						}
					}
				}
				return list;
			}
			var _v1 = _v0.b;
			var x = _v1.a;
			return _List_fromArray(
				[x]);
		}
	});
var $elm$core$List$take = F2(
	function (n, list) {
		return A3($elm$core$List$takeFast, 0, n, list);
	});
var $author$project$Switcher$advanceSelection = function (model) {
	var through = A2(
		$elm$core$Maybe$withDefault,
		0,
		A2(
			$elm$core$Maybe$map,
			function ($) {
				return $.b8;
			},
			model.aB));
	var total = $elm$core$List$sum(
		A2(
			$elm$core$List$map,
			A2($elm$core$Basics$composeR, $elm$core$Tuple$second, $author$project$Switcher$delta),
			A2(
				$elm$core$List$filter,
				function (_v1) {
					var number = _v1.a;
					return _Utils_cmp(number, through) > 0;
				},
				$elm$core$Dict$toList(model.a1))));
	var ring = _Utils_eq(model.aB, $elm$core$Maybe$Nothing) ? model.ct : A2(
		$elm$core$List$map,
		function ($) {
			return $.v;
		},
		model.bp);
	var size = $elm$core$List$length(ring);
	var anchor = A2(
		$elm$core$Maybe$withDefault,
		_Utils_eq(
			A2($elm$core$Dict$get, 1, model.a1),
			$elm$core$Maybe$Just(0)) ? (-1) : 0,
		function (root) {
			return A2(
				$elm$core$Maybe$map,
				$elm$core$Tuple$first,
				$elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (_v0) {
							var identity = _v0.b;
							return _Utils_eq(identity, root);
						},
						A2($elm$core$List$indexedMap, $elm$core$Tuple$pair, ring))));
		}(
			A2(
				$elm$core$Maybe$withDefault,
				A2($elm$core$Maybe$withDefault, $author$project$UInt64$zero, model.bZ),
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.v;
					},
					model.aB))));
	var position = (!size) ? 0 : A2($elm$core$Basics$modBy, size, anchor + total);
	var survivor = $elm$core$List$head(
		A2(
			$elm$core$List$filter,
			function (identity) {
				return A2(
					$elm$core$List$any,
					function (row) {
						return _Utils_eq(row.v, identity);
					},
					model.bp);
			},
			_Utils_ap(
				A2($elm$core$List$drop, position, ring),
				A2($elm$core$List$take, position, ring))));
	return _Utils_update(
		model,
		{
			eb: A2(
				$elm$core$Maybe$withDefault,
				0,
				A2(
					$elm$core$Maybe$andThen,
					function (identity) {
						return A2($author$project$Switcher$index, identity, model.bp);
					},
					survivor))
		});
};
var $author$project$Switcher$step = F4(
	function (token, ordinal, direction, original) {
		var current = original;
		if ((ordinal < 1) || (ordinal > 4096)) {
			return _Utils_Tuple2(original, $elm$core$Maybe$Nothing);
		} else {
			var _v0 = A2($author$project$Switcher$prepare, token, current);
			if (_v0.$ === 1) {
				return _Utils_Tuple2(original, $elm$core$Maybe$Nothing);
			} else {
				var model = _v0.a;
				if (A2(
					$elm$core$Maybe$withDefault,
					false,
					A2(
						$elm$core$Maybe$map,
						function (_final) {
							return _Utils_cmp(ordinal, _final) > 0;
						},
						model.b1))) {
					return _Utils_Tuple2(original, $elm$core$Maybe$Nothing);
				} else {
					var _v1 = A2($elm$core$Dict$get, ordinal, model.a1);
					if (!_v1.$) {
						var previous = _v1.a;
						return _Utils_eq(previous, direction) ? _Utils_Tuple2(original, $elm$core$Maybe$Nothing) : _Utils_Tuple2(
							_Utils_update(
								model,
								{bp: _List_Nil, G: 4}),
							$elm$core$Maybe$Nothing);
					} else {
						var next = _Utils_update(
							model,
							{
								a1: A3($elm$core$Dict$insert, ordinal, direction, model.a1)
							});
						return $author$project$Switcher$settle(
							next.bc ? $author$project$Switcher$advanceSelection(next) : next);
					}
				}
			}
		}
	});
var $author$project$Switcher$readyWith = F6(
	function (frozenRoots, token, history, candidates, origin, original) {
		var model = original;
		if ((!_Utils_eq(token, model.dP)) || ((!$author$project$Switcher$writable(model)) || model.bc)) {
			return _Utils_Tuple2(original, $elm$core$Maybe$Nothing);
		} else {
			var unique = function (rows) {
				return A3(
					$elm$core$List$foldl,
					F2(
						function (row, accumulated) {
							return A2(
								$elm$core$List$any,
								function (old) {
									return _Utils_eq(old.v, row.v);
								},
								accumulated) ? accumulated : _Utils_ap(
								accumulated,
								_List_fromArray(
									[row]));
						}),
					_List_Nil,
					rows);
			};
			var eligible = A2(
				$elm$core$List$filter,
				function (row) {
					return row.ca && A2(
						$elm$core$Maybe$withDefault,
						true,
						A2(
							$elm$core$Maybe$map,
							$elm$core$List$member(row.v),
							frozenRoots));
				},
				candidates);
			var known = unique(
				A2(
					$elm$core$List$filterMap,
					function (root) {
						return $elm$core$List$head(
							A2(
								$elm$core$List$filter,
								function (row) {
									return _Utils_eq(row.v, root);
								},
								eligible));
					},
					history));
			var unranked = A2(
				$elm$core$List$sortWith,
				F2(
					function (a, b) {
						return A2($author$project$UInt64$compare, a.v, b.v);
					}),
				unique(
					A2(
						$elm$core$List$filter,
						function (row) {
							return !A2(
								$elm$core$List$any,
								function (old) {
									return _Utils_eq(old.v, row.v);
								},
								known);
						},
						eligible)));
			var frozen = _Utils_ap(known, unranked);
			var ring = A2(
				$elm$core$Maybe$withDefault,
				A2(
					$elm$core$List$map,
					function ($) {
						return $.v;
					},
					frozen),
				A2(
					$elm$core$Maybe$map,
					function (roots) {
						return _Utils_ap(
							A2(
								$elm$core$List$filter,
								function (identity) {
									return A2($elm$core$List$member, identity, roots);
								},
								history),
							A2(
								$elm$core$List$sortWith,
								$author$project$UInt64$compare,
								A2(
									$elm$core$List$filter,
									function (identity) {
										return !A2($elm$core$List$member, identity, history);
									},
									roots)));
					},
					frozenRoots));
			return (($elm$core$List$length(candidates) > 256) || ($elm$core$List$length(ring) > 256)) ? _Utils_Tuple2(
				_Utils_update(
					model,
					{G: 4}),
				$elm$core$Maybe$Nothing) : $author$project$Switcher$settle(
				$author$project$Switcher$advanceSelection(
					_Utils_update(
						model,
						{bp: frozen, bZ: origin, bc: true, ct: ring})));
		}
	});
var $author$project$Switcher$readyFrozen = F2(
	function (token, roots) {
		return A2(
			$author$project$Switcher$readyWith,
			$elm$core$Maybe$Just(roots),
			token);
	});
var $author$project$Switcher$reconcile = F2(
	function (candidates, original) {
		var model = original;
		if ((!$author$project$Switcher$writable(model)) || (!model.bc)) {
			return original;
		} else {
			var prior = A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.v;
				},
				$author$project$Switcher$selected(original));
			var current = function (old) {
				return $elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (row) {
							return row.ca && (_Utils_eq(row.v, old.v) && _Utils_eq(row.b9, old.b9));
						},
						candidates));
			};
			var surviving = A2($elm$core$List$filterMap, current, model.bp);
			var after = _Utils_ap(
				A2($elm$core$List$drop, model.eb, model.bp),
				A2($elm$core$List$take, model.eb, model.bp));
			var fallback = $elm$core$List$head(
				A2(
					$elm$core$List$filterMap,
					function (old) {
						return A2(
							$elm$core$Maybe$map,
							function ($) {
								return $.v;
							},
							current(old));
					},
					after));
			var root = A2(
				$elm$core$Maybe$withDefault,
				A2($elm$core$Maybe$withDefault, $author$project$UInt64$zero, fallback),
				A2(
					$elm$core$Maybe$andThen,
					function (identity) {
						return A2(
							$elm$core$List$any,
							function (row) {
								return _Utils_eq(row.v, identity);
							},
							surviving) ? $elm$core$Maybe$Just(identity) : $elm$core$Maybe$Nothing;
					},
					prior));
			var baseline = (model.G === 2) ? $elm$core$Maybe$Just(
				{
					v: root,
					b8: $author$project$Switcher$lastOrdinal(model)
				}) : model.aB;
			var position = A2(
				$elm$core$Maybe$withDefault,
				0,
				A2($author$project$Switcher$index, root, surviving));
			return _Utils_update(
				model,
				{
					aB: baseline,
					bp: surviving,
					G: $elm$core$List$isEmpty(surviving) ? 4 : model.G,
					eb: position
				});
		}
	});
var $author$project$Desktop$switcherFocus = function (model) {
	return A2(
		$elm$core$Maybe$withDefault,
		_List_Nil,
		A2(
			$elm$core$Maybe$map,
			function (family) {
				return _List_fromArray(
					[
						$author$project$Desktop$Focus(
						A2(
							$author$project$Desktop$key,
							model,
							'switcher:family:' + $author$project$UInt64$string(family.v)))
					]);
			},
			$author$project$Switcher$selected(model.e)));
};
var $author$project$Switcher$ready = $author$project$Switcher$readyWith($elm$core$Maybe$Nothing);
var $author$project$Desktop$syncLocalSwitcher = function (model) {
	var _v0 = _Utils_Tuple3(
		model.aj,
		model.a.b.R.aa,
		$author$project$TaskView$groups(model.a.b));
	if (((!_v0.a.$) && (!_v0.b.$)) && (!_v0.c.$)) {
		var history = _v0.a.a;
		var observed = _v0.b.a;
		var groups = _v0.c.a;
		if ($author$project$Switcher$phase(model.e) === 2) {
			return _Utils_Tuple2(
				_Utils_update(
					model,
					{
						e: A2(
							$author$project$Switcher$reconcile,
							A2(
								$elm$core$List$concatMap,
								function ($) {
									return $.a;
								},
								groups),
							model.e)
					}),
				_List_Nil);
		} else {
			if (!_Utils_eq(history.A, observed.A)) {
				return _Utils_eq(model.ai, $elm$core$Maybe$Nothing) ? $author$project$Desktop$readSwitcherHistory(model) : _Utils_Tuple2(model, _List_Nil);
			} else {
				var _v1 = A5(
					$author$project$Switcher$ready,
					$author$project$Switcher$generation(model.e),
					history.ah,
					A2(
						$elm$core$List$concatMap,
						function ($) {
							return $.a;
						},
						groups),
					model.bG,
					model.e);
				var switcher = _v1.a;
				var selected = _v1.b;
				var next = $author$project$Desktop$advance(
					_Utils_update(
						model,
						{e: switcher}));
				if (!selected.$) {
					var family = selected.a;
					return A2($author$project$Desktop$chooseFamily, family, next);
				} else {
					return _Utils_Tuple2(
						next,
						$author$project$Desktop$switcherFocus(next));
				}
			}
		}
	} else {
		return _Utils_Tuple2(model, _List_Nil);
	}
};
var $author$project$Desktop$syncSwitcher = function (model) {
	if (!$author$project$Desktop$switcherOpen(model)) {
		return _Utils_Tuple2(model, _List_Nil);
	} else {
		var _v0 = model.O;
		if (!_v0.$) {
			var chord = _v0.a;
			var _v1 = $author$project$TaskView$groups(model.a.b);
			if (!_v1.$) {
				var groups = _v1.a;
				var candidates = A2(
					$elm$core$List$filter,
					function (row) {
						return A2($elm$core$List$member, row.v, chord.ah);
					},
					A2(
						$elm$core$List$concatMap,
						function ($) {
							return $.a;
						},
						groups));
				var _v2 = ($author$project$Switcher$phase(model.e) === 2) ? _Utils_Tuple2(
					A2($author$project$Switcher$reconcile, candidates, model.e),
					$elm$core$Maybe$Nothing) : A6(
					$author$project$Switcher$readyFrozen,
					$author$project$Switcher$generation(model.e),
					chord.ah,
					chord.bt,
					candidates,
					chord.bZ,
					model.e);
				var switcher = _v2.a;
				var selected = _v2.b;
				var next = $author$project$Desktop$advance(
					_Utils_update(
						model,
						{e: switcher}));
				if (!selected.$) {
					var family = selected.a;
					return A2($author$project$Desktop$chooseFamily, family, next);
				} else {
					return _Utils_Tuple2(
						next,
						$author$project$Desktop$switcherFocus(next));
				}
			} else {
				return _Utils_Tuple2(model, _List_Nil);
			}
		} else {
			return $author$project$Desktop$syncLocalSwitcher(model);
		}
	}
};
var $author$project$Desktop$receiveChord = F2(
	function (chord, model) {
		var old = model.O;
		var order = A2(
			$elm$core$Maybe$withDefault,
			2,
			A2(
				$elm$core$Maybe$map,
				function (previous) {
					return A2($author$project$UInt64$compare, chord.dP, previous.dP);
				},
				old));
		var inconsistent = A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (previous) {
					return (order === 1) && ((!_Utils_eq(previous.ah, chord.ah)) || ((!_Utils_eq(previous.bt, chord.bt)) || ((!_Utils_eq(previous.bZ, chord.bZ)) || ((!_Utils_eq(
						A2(
							$elm$core$List$take,
							$elm$core$List$length(previous.a1),
							chord.a1),
						previous.a1)) || ((previous.b1 && (!chord.b1)) || ((previous.bO && (!chord.bO)) || (previous.bS && (!chord.bS))))))));
				},
				old));
		var closed = function () {
			var retired = $author$project$Desktop$advance(
				$author$project$Desktop$retireSwitcher(
					_Utils_update(
						model,
						{
							O: $elm$core$Maybe$Just(chord)
						})));
			var choice = A2(
				$elm$core$Maybe$andThen,
				function (pending) {
					return _Utils_eq(
						pending.aC,
						$elm$core$Maybe$Just(chord.dP)) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(pending);
				},
				retired.j);
			return _Utils_Tuple2(
				_Utils_update(
					retired,
					{j: choice}),
				_List_Nil);
		}();
		if (_Utils_eq(chord.dP, $author$project$UInt64$zero) || (!order)) {
			return _Utils_Tuple2(model, _List_Nil);
		} else {
			if (inconsistent || (chord.bO || chord.bS)) {
				return closed;
			} else {
				var localGeneration = (order === 2) ? $author$project$UInt64$next(
					$author$project$Switcher$generation(model.e)) : $elm$core$Maybe$Just(
					$author$project$Switcher$generation(model.e));
				if (localGeneration.$ === 1) {
					return _Utils_Tuple2(
						$author$project$Desktop$retireSwitcher(model),
						_List_Nil);
				} else {
					var generation = localGeneration.a;
					var windows = model.a;
					var base = (order === 2) ? _Utils_update(
						model,
						{
							j: $elm$core$Maybe$Nothing,
							E: '',
							n: $elm$core$Maybe$Nothing,
							F: $elm$core$Maybe$Nothing,
							O: $elm$core$Maybe$Just(chord),
							q: false,
							t: false,
							r: $elm$core$Maybe$Nothing,
							ai: $elm$core$Maybe$Nothing,
							aj: $elm$core$Maybe$Nothing,
							a: _Utils_update(
								windows,
								{
									k: $author$project$MenuBridge$retireChoices(windows.k),
									J: $elm$core$Maybe$Nothing
								})
						}) : _Utils_update(
						model,
						{
							O: $elm$core$Maybe$Just(chord)
						});
					var _v1 = A3(
						$elm$core$List$foldl,
						F2(
							function (_v2, _v3) {
								var ordinal = _v2.a;
								var direction = _v2.b;
								var state = _v3.a;
								return A4($author$project$Switcher$step, generation, ordinal + 1, direction, state);
							}),
						_Utils_Tuple2(base.e, $elm$core$Maybe$Nothing),
						A2($elm$core$List$indexedMap, $elm$core$Tuple$pair, chord.a1));
					var stepped = _v1.a;
					var _v4 = chord.b1 ? A3(
						$author$project$Switcher$release,
						generation,
						$elm$core$List$length(chord.a1),
						stepped) : _Utils_Tuple2(stepped, $elm$core$Maybe$Nothing);
					var released = _v4.a;
					var selected = _v4.b;
					var next = $author$project$Desktop$advance(
						_Utils_update(
							base,
							{e: released}));
					if (!selected.$) {
						var family = selected.a;
						return A2($author$project$Desktop$chooseFamily, family, next);
					} else {
						var _v6 = $author$project$Desktop$syncSwitcher(next);
						var synced = _v6.a;
						var effects = _v6.b;
						if ((order === 2) && (!$author$project$Shell$available(next.a.b))) {
							var _v7 = A2(
								$author$project$Desktop$windowBase,
								$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
								synced);
							var refreshing = _v7.a;
							var reads = _v7.b;
							return _Utils_Tuple2(
								refreshing,
								_Utils_ap(effects, reads));
						} else {
							return _Utils_Tuple2(synced, effects);
						}
					}
				}
			}
		}
	});
var $author$project$Pins$encode = function (snapshot) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'revision',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(snapshot.dj))),
				_Utils_Tuple2(
				'identities',
				A2($elm$json$Json$Encode$list, $elm$json$Json$Encode$string, snapshot.dU))
			]));
};
var $author$project$Pins$propose = F3(
	function (request, values, model) {
		var _v0 = model.bF;
		if (!_v0.$) {
			var snapshot = _v0.a;
			return ((!$author$project$Pins$writable(model)) || ((!$author$project$Pins$valid(values)) || _Utils_eq(values, snapshot.dU))) ? _Utils_Tuple2(model, $elm$core$Maybe$Nothing) : _Utils_Tuple2(
				_Utils_update(
					model,
					{
						d_: 'Saving pin order…',
						d4: $elm$core$Maybe$Just(
							{dU: values, o: request})
					}),
				$elm$core$Maybe$Just(
					$author$project$Pins$encode(
						_Utils_update(
							snapshot,
							{dU: values}))));
		} else {
			return _Utils_Tuple2(model, $elm$core$Maybe$Nothing);
		}
	});
var $author$project$Desktop$savePins = F2(
	function (values, model) {
		var _v0 = _Utils_Tuple2(
			model.a.b.d,
			$author$project$UInt64$next(model.o));
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var binding = _v0.a.a;
			var request = _v0.b.a;
			var wire = function (p) {
				return $elm$json$Json$Encode$object(
					_List_fromArray(
						[
							_Utils_Tuple2(
							'protocolVersion',
							$elm$json$Json$Encode$int(3)),
							_Utils_Tuple2(
							'kind',
							$elm$json$Json$Encode$string('taskbar-pins-write')),
							_Utils_Tuple2(
							'binding',
							$author$project$Binding$encode(binding)),
							_Utils_Tuple2(
							'requestId',
							$elm$json$Json$Encode$string(
								$author$project$UInt64$string(request))),
							_Utils_Tuple2('proposal', p)
						]));
			};
			var _v1 = A3($author$project$Pins$propose, request, values, model.y);
			var pins = _v1.a;
			var proposal = _v1.b;
			if (!proposal.$) {
				var p = proposal.a;
				return ($author$project$Pins$bytes(
					A2(
						$elm$json$Json$Encode$encode,
						0,
						wire(p))) > 4095) ? _Utils_Tuple2(
					_Utils_update(
						model,
						{
							y: _Utils_update(
								pins,
								{d_: 'Pin order is too large to save.', d4: $elm$core$Maybe$Nothing})
						}),
					_List_Nil) : _Utils_Tuple2(
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{y: pins, o: request})),
					_List_fromArray(
						[
							$author$project$Desktop$Send(
							wire(p))
						]));
			} else {
				return _Utils_Tuple2(model, _List_Nil);
			}
		} else {
			return _Utils_Tuple2(model, _List_Nil);
		}
	});
var $author$project$Snap$select = F3(
	function (current, region, choice) {
		return A2($author$project$Snap$valid, current, choice) ? $elm$core$Maybe$Just(
			_Utils_update(
				choice,
				{eb: region})) : $elm$core$Maybe$Nothing;
	});
var $author$project$Launch$Pending = F2(
	function (a, b) {
		return {$: 1, a: a, b: b};
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
			var _v3 = model.G;
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
			model.bF,
			$author$project$UInt64$next(model.o));
		if ((!_v1.a.$) && (!_v1.b.$)) {
			var snapshot = _v1.a.a;
			var request = _v1.b.a;
			var scope = $author$project$Catalog$scope(snapshot);
			if (ready && (_Utils_eq(
				model.aG,
				$elm$core$Maybe$Just(host)) && (_Utils_eq(model.dj, revision) && (_Utils_eq(lifetime, scope.dY) && _Utils_eq(generation, scope.dP))))) {
				var _v2 = A3($author$project$Catalog$intent, request, entry, snapshot);
				if (!_v2.$) {
					var wire = _v2.a;
					return _Utils_Tuple2(
						$author$project$Launch$advance(
							_Utils_update(
								model,
								{
									G: A2(
										$author$project$Launch$Pending,
										host,
										{
											cJ: $author$project$Catalog$id(entry),
											dP: generation,
											dY: lifetime,
											o: request
										}),
									o: request
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
var $author$project$Pins$toggle = F2(
	function (identity, values) {
		return A2($elm$core$List$member, identity, values) ? A2(
			$elm$core$List$filter,
			$elm$core$Basics$neq(identity),
			values) : _Utils_ap(
			values,
			_List_fromArray(
				[identity]));
	});
var $author$project$Desktop$version = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (value === 3) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Desktop version');
	},
	A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int));
var $author$project$Desktop$fenceSwitcherSelection = F3(
	function (chord, binding, effects) {
		return A2(
			$elm$core$List$concatMap,
			function (effect) {
				var _v0 = _Utils_Tuple2(chord, effect);
				if (((!_v0.a.$) && (!_v0.b.$)) && (!_v0.b.a.$)) {
					var generation = _v0.a.a;
					var raw = _v0.b.a.a;
					var _v1 = A2(
						$elm$json$Json$Decode$decodeValue,
						A4(
							$elm$json$Json$Decode$map3,
							F3(
								function (kind, request, root) {
									return _Utils_Tuple3(kind, request, root);
								}),
							A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
							A2(
								$elm$json$Json$Decode$at,
								_List_fromArray(
									['intent', 'request']),
								$author$project$UInt64$decoder),
							A2(
								$elm$json$Json$Decode$at,
								_List_fromArray(
									['intent', 'incarnation']),
								$author$project$UInt64$decoder)),
						raw);
					if ((!_v1.$) && (_v1.a.a === 'window-effect')) {
						var _v2 = _v1.a;
						var request = _v2.b;
						var root = _v2.c;
						return _List_fromArray(
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
											$elm$json$Json$Encode$string('switcher-selection-request')),
											_Utils_Tuple2(
											'binding',
											$author$project$Binding$encode(binding)),
											_Utils_Tuple2(
											'requestId',
											$elm$json$Json$Encode$string(
												$author$project$UInt64$string(request))),
											_Utils_Tuple2(
											'chord',
											$elm$json$Json$Encode$string(
												$author$project$UInt64$string(generation))),
											_Utils_Tuple2(
											'root',
											$elm$json$Json$Encode$string(
												$author$project$UInt64$string(root)))
										]))),
								effect
							]);
					} else {
						return _List_fromArray(
							[effect]);
					}
				} else {
					return _List_fromArray(
						[effect]);
				}
			},
			effects);
	});
var $author$project$Desktop$window = F2(
	function (message, model) {
		_v0$4:
		while (true) {
			switch (message.$) {
				case 5:
					switch (message.a.$) {
						case 3:
							var _v1 = message.a;
							var menuId = _v1.a;
							var binding = _v1.b;
							var index = _v1.c;
							var inactiveMinimize = function () {
								var _v3 = _Utils_Tuple2(
									$author$project$MenuBridge$menuSnapshot(model.a.k).aq,
									$author$project$MenuBridge$currentProvider(model.a.k));
								if ((!_v3.a.$) && (!_v3.b.$)) {
									var menu = _v3.a.a;
									var provider = _v3.b.a;
									return _Utils_eq(menu.bu, menuId) && (_Utils_eq(menu.d, binding) && (_Utils_eq(
										A2(
											$elm$core$Maybe$map,
											function ($) {
												return $.dB;
											},
											$elm$core$List$head(
												A2($elm$core$List$drop, index, menu.dX))),
										$elm$core$Maybe$Just($author$project$Menu$Minimize)) && A2(
										$elm$core$List$any,
										function (family) {
											return _Utils_eq(
												family.v,
												$author$project$Provider$incarnation(provider)) && (!family.dC);
										},
										A2(
											$elm$core$List$concatMap,
											function ($) {
												return $.am;
											},
											$author$project$TaskbarShell$groups(model.a)))));
								} else {
									return false;
								}
							}();
							var _v2 = A2(
								$author$project$Desktop$windowBase,
								message,
								_Utils_update(
									model,
									{r: $elm$core$Maybe$Nothing}));
							var next = _v2.a;
							var effects = _v2.b;
							var admitted = _Utils_eq(
								$author$project$MenuBridge$preparedSnapshot(model.a.k),
								$elm$core$Maybe$Nothing) && (!_Utils_eq(
								$author$project$MenuBridge$preparedSnapshot(next.a.k),
								$elm$core$Maybe$Nothing));
							return (inactiveMinimize && admitted) ? _Utils_Tuple2(
								_Utils_update(
									next,
									{r: model.F}),
								effects) : _Utils_Tuple2(next, effects);
						case 5:
							var menuId = message.a.a;
							var _v4 = _Utils_Tuple2(
								$author$project$MenuBridge$menuSnapshot(model.a.k).aq,
								model.F);
							if ((!_v4.a.$) && (!_v4.b.$)) {
								var menu = _v4.a.a;
								var origin = _v4.b.a;
								if (!_Utils_eq(menu.bu, menuId)) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var _v5 = A2($author$project$Desktop$windowBase, message, model);
									var closed = _v5.a;
									var effects = _v5.b;
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
												F: $elm$core$Maybe$Nothing,
												r: $elm$core$Maybe$Just(origin)
											}),
										_Utils_ap(effects, commands));
								}
							} else {
								return A2($author$project$Desktop$windowBase, message, model);
							}
						default:
							break _v0$4;
					}
				case 3:
					var scope = message.a;
					var generation = message.b;
					var _v7 = _Utils_Tuple2(model.a.J, model.a.b.d);
					if ((!_v7.a.$) && (!_v7.b.$)) {
						var picker = _v7.a.a;
						var binding = _v7.b.a;
						var _v8 = A2($author$project$Desktop$windowBase, message, model);
						var closed = _v8.a;
						var effects = _v8.b;
						if ((!_Utils_eq(closed.a.J, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(picker.b3, scope)) || (!_Utils_eq(picker.dP, generation)))) {
							return _Utils_Tuple2(closed, effects);
						} else {
							var _v9 = A2(
								$author$project$Desktop$windowBase,
								$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
								closed);
							var refreshing = _v9.a;
							var commands = _v9.b;
							return _Utils_Tuple2(
								_Utils_update(
									refreshing,
									{
										r: $elm$core$Maybe$Just(
											{
												d: binding,
												aT: $author$project$Desktop$TaskbarGroup(picker.ap),
												m: A2(
													$elm$core$Maybe$map,
													A2(
														$elm$core$Basics$composeR,
														function ($) {
															return $.A;
														},
														function ($) {
															return $.m;
														}),
													model.a.b.R.aa)
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
					var _v11 = _Utils_Tuple3(model.a.J, model.a.b.d, model.a.b.R.aa);
					if (((!_v11.a.$) && (!_v11.b.$)) && (!_v11.c.$)) {
						var picker = _v11.a.a;
						var binding = _v11.b.a;
						var observed = _v11.c.a;
						if ((!_Utils_eq(model.j, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(picker.b3, scope)) || ((!_Utils_eq(picker.dP, generation)) || ((!_Utils_eq(
							$author$project$Shell$capture(model.a.b),
							$elm$core$Maybe$Just(scope))) || (!$author$project$Shell$available(model.a.b)))))) {
							return _Utils_Tuple2(model, _List_Nil);
						} else {
							var _v12 = $elm$core$List$head(
								A2(
									$elm$core$List$filter,
									function (family) {
										return _Utils_eq(family.v, root) && family.ca;
									},
									A2(
										$elm$core$List$concatMap,
										function ($) {
											return $.am;
										},
										A2(
											$elm$core$List$filter,
											function (group) {
												return _Utils_eq(group.ap, picker.ap);
											},
											$author$project$TaskbarShell$groups(model.a)))));
							if (_v12.$ === 1) {
								return _Utils_Tuple2(model, _List_Nil);
							} else {
								var family = _v12.a;
								var windows = model.a;
								var _v13 = A2(
									$author$project$Desktop$windowBase,
									$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
									_Utils_update(
										model,
										{
											E: '',
											a: _Utils_update(
												windows,
												{J: $elm$core$Maybe$Nothing})
										}));
								var next = _v13.a;
								var effects = _v13.b;
								var _v14 = next.a.b.n;
								if (!_v14.$) {
									var request = _v14.a;
									var token = A2($author$project$Desktop$ChoiceToken, binding, request);
									return _Utils_Tuple2(
										_Utils_update(
											next,
											{
												j: $elm$core$Maybe$Just(
													{b9: family.b9, d: binding, aC: $elm$core$Maybe$Nothing, m: observed.A.m, aZ: $elm$core$Maybe$Nothing, v: root, bh: token})
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
					break _v0$4;
			}
		}
		var matchingProjection = function () {
			if ((!message.$) && (message.a.$ === 3)) {
				var raw = message.a.a;
				return A2(
					$elm$core$Result$withDefault,
					false,
					A2(
						$elm$core$Result$map,
						function (_v32) {
							var kind = _v32.a;
							var request = _v32.b;
							return (kind === 'action-projection') && _Utils_eq(
								model.a.b.n,
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
			if ((!message.$) && (message.a.$ === 3)) {
				return model;
			} else {
				return _Utils_update(
					model,
					{r: $elm$core$Maybe$Nothing});
			}
		}();
		var _v15 = A2($author$project$Desktop$windowBase, message, base);
		var updated = _v15.a;
		var ordinaryEffects = _v15.b;
		var geometryOutput = A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.R;
				},
				updated.a.b.cR)) ? A2(
			$elm$core$Maybe$map,
			A2(
				$elm$core$Basics$composeR,
				function ($) {
					return $.A;
				},
				function ($) {
					return $.m;
				}),
			updated.a.b.ad) : A2(
			$elm$core$Maybe$map,
			A2(
				$elm$core$Basics$composeR,
				function ($) {
					return $.A;
				},
				function ($) {
					return $.m;
				}),
			updated.a.b.R.aa);
		var matchingGeometry = function () {
			if ((!message.$) && (message.a.$ === 3)) {
				var raw = message.a.a;
				return A2(
					$elm$core$Result$withDefault,
					false,
					A2(
						$elm$core$Result$map,
						function (_v29) {
							var kind = _v29.a;
							var request = _v29.b;
							return (kind === 'geometry-facts') && (_Utils_eq(
								model.a.b.dQ,
								$elm$core$Maybe$Just(request)) && (_Utils_eq(
								A2(
									$elm$core$Maybe$map,
									function ($) {
										return $.o;
									},
									updated.a.b.ad),
								$elm$core$Maybe$Just(request)) && (!_Utils_eq(updated.a.b.ad, model.a.b.ad))));
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
		var matchingObservation = matchingProjection || matchingGeometry;
		var _v16 = function () {
			var _v17 = updated.r;
			if (!_v17.$) {
				var target = _v17.a;
				var blocked = function () {
					var _v20 = target.aT;
					if (!_v20.$) {
						var groupKey = _v20.a;
						return A2(
							$elm$core$List$any,
							function (family) {
								return A3($author$project$MenuBridge$blockedFor, family.v, updated.a.b, updated.a.k);
							},
							A2(
								$elm$core$List$concatMap,
								function ($) {
									return $.am;
								},
								A2(
									$elm$core$List$filter,
									function (group) {
										return _Utils_eq(group.ap, groupKey);
									},
									$author$project$TaskbarShell$groups(updated.a))));
					} else {
						return false;
					}
				}();
				if ((!matchingObservation) || ((!$author$project$Shell$available(updated.a.b)) || blocked)) {
					return _Utils_Tuple2(updated, ordinaryEffects);
				} else {
					var retired = _Utils_update(
						updated,
						{r: $elm$core$Maybe$Nothing});
					var focus = function () {
						var _v19 = target.aT;
						if (!_v19.$) {
							var groupKey = _v19.a;
							return A2(
								$elm$core$Maybe$map,
								function (scope) {
									return 'group:' + ($author$project$Shell$stampKey(scope) + (':' + groupKey));
								},
								$author$project$Shell$capture(retired.a.b));
						} else {
							return $elm$core$Maybe$Just(
								A2($author$project$Desktop$key, retired, 'control:overview-opener'));
						}
					}();
					var exists = function () {
						var _v18 = target.aT;
						if (!_v18.$) {
							var groupKey = _v18.a;
							return A2(
								$elm$core$List$any,
								function (group) {
									return _Utils_eq(group.ap, groupKey) && A2(
										$elm$core$List$any,
										function ($) {
											return $.ca;
										},
										group.am);
								},
								$author$project$TaskbarShell$groups(retired.a));
						} else {
							return _Utils_eq(retired.j, $elm$core$Maybe$Nothing);
						}
					}();
					return (retired.q || (retired.t || ((!_Utils_eq(retired.a.J, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(
						$author$project$MenuBridge$menuSnapshot(retired.a.k).aq,
						$elm$core$Maybe$Nothing)) || ((!_Utils_eq(
						retired.a.b.d,
						$elm$core$Maybe$Just(target.d))) || (_Utils_eq(target.m, $elm$core$Maybe$Nothing) || ((!_Utils_eq(
						A2(
							$elm$core$Maybe$map,
							A2(
								$elm$core$Basics$composeR,
								function ($) {
									return $.A;
								},
								function ($) {
									return $.m;
								}),
							retired.a.b.R.aa),
						target.m)) || ((!_Utils_eq(geometryOutput, target.m)) || (!exists))))))))) ? _Utils_Tuple2(retired, ordinaryEffects) : _Utils_Tuple2(
						retired,
						_Utils_ap(
							ordinaryEffects,
							A2(
								$elm$core$Maybe$withDefault,
								_List_Nil,
								A2(
									$elm$core$Maybe$map,
									A2($elm$core$Basics$composeR, $author$project$Desktop$Focus, $elm$core$List$singleton),
									focus))));
				}
			} else {
				return _Utils_Tuple2(updated, ordinaryEffects);
			}
		}();
		var next = _v16.a;
		var effects = _v16.b;
		var _v21 = next.j;
		if (!_v21.$) {
			var pending = _v21.a;
			if ((!matchingObservation) || ((!$author$project$Shell$available(next.a.b)) || ((!_Utils_eq(pending.aZ, $elm$core$Maybe$Nothing)) && A2(
				$elm$core$Maybe$withDefault,
				true,
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.dE;
					},
					next.a.b.ad))))) {
				return _Utils_Tuple2(next, effects);
			} else {
				var retired = _Utils_update(
					next,
					{j: $elm$core$Maybe$Nothing, E: 'The window changed. Choose again.'});
				var output = A2(
					$elm$core$Maybe$map,
					A2(
						$elm$core$Basics$composeR,
						function ($) {
							return $.A;
						},
						function ($) {
							return $.m;
						}),
					next.a.b.R.aa);
				var family = $elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (item) {
							return _Utils_eq(item.v, pending.v) && (_Utils_eq(item.b9, pending.b9) && item.ca);
						},
						A2(
							$elm$core$List$concatMap,
							function ($) {
								return $.am;
							},
							$author$project$TaskbarShell$groups(next.a))));
				if ((!_Utils_eq(
					next.a.b.d,
					$elm$core$Maybe$Just(pending.d))) || ((!_Utils_eq(
					output,
					$elm$core$Maybe$Just(pending.m))) || (!_Utils_eq(
					geometryOutput,
					$elm$core$Maybe$Just(pending.m))))) {
					return _Utils_Tuple2(retired, effects);
				} else {
					var _v22 = _Utils_Tuple2(
						$author$project$Shell$capture(next.a.b),
						family);
					if ((!_v22.a.$) && (!_v22.b.$)) {
						var scope = _v22.a.a;
						var selected = _v22.b.a;
						var _v23 = pending.aZ;
						if (!_v23.$) {
							var proposed = _v23.a;
							var _v24 = _Utils_Tuple2(
								next.a.b.ad,
								$author$project$Shell$captureGeometry(next.a.b));
							if ((!_v24.a.$) && (!_v24.b.$)) {
								var geometry = _v24.a.a;
								var stamp = _v24.b.a;
								var current = _Utils_update(
									proposed,
									{A: geometry.A});
								if (!A3($author$project$Snap$matches, geometry, pending.v, current)) {
									return _Utils_Tuple2(
										_Utils_update(
											retired,
											{E: 'Output or window changed. Open snapping again.'}),
										effects);
								} else {
									var _v25 = A2(
										$author$project$Desktop$windowBase,
										$author$project$TaskbarShell$Native(
											A3(
												$author$project$Shell$Act,
												stamp,
												$author$project$Effects$SnapPlacement(current),
												pending.v)),
										_Utils_update(
											retired,
											{E: ''}));
									var applied = _v25.a;
									var commands = _v25.b;
									return _Utils_Tuple2(
										applied,
										_Utils_ap(effects, commands));
								}
							} else {
								return _Utils_Tuple2(retired, effects);
							}
						} else {
							var _v26 = $author$project$Taskbar$selection(selected);
							if (_v26.$ === 2) {
								var operation = _v26.a;
								var root = _v26.b;
								var _v27 = A2(
									$author$project$Desktop$windowBase,
									$author$project$TaskbarShell$Native(
										A3($author$project$Shell$Act, scope, operation, root)),
									_Utils_update(
										retired,
										{E: ''}));
								var applied = _v27.a;
								var commands = _v27.b;
								return _Utils_Tuple2(
									applied,
									_Utils_ap(
										effects,
										A3($author$project$Desktop$fenceSwitcherSelection, pending.aC, pending.d, commands)));
							} else {
								return _Utils_Tuple2(retired, effects);
							}
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
			case 2:
				var stamp = message.a;
				var root = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!$author$project$Shell$available(model.a.b)) || A3($author$project$MenuBridge$blockedFor, root, model.a.b, model.a.k))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v1 = A2(
						$elm$core$Maybe$andThen,
						function (geometry) {
							return A2($author$project$Snap$open, geometry, root);
						},
						model.a.b.ad);
					if (_v1.$ === 1) {
						return _Utils_Tuple2(model, _List_Nil);
					} else {
						var choice = _v1.a;
						var windows = model.a;
						return _Utils_Tuple2(
							$author$project$Desktop$advance(
								$author$project$Desktop$retireSwitcher(
									_Utils_update(
										model,
										{
											j: $elm$core$Maybe$Nothing,
											n: $elm$core$Maybe$Nothing,
											F: $elm$core$Maybe$Nothing,
											q: false,
											t: false,
											r: $elm$core$Maybe$Nothing,
											w: $elm$core$Maybe$Just(choice),
											a: _Utils_update(
												windows,
												{
													k: $author$project$MenuBridge$retireChoices(windows.k),
													J: $elm$core$Maybe$Nothing
												})
										}))),
							_List_Nil);
					}
				}
			case 3:
				var stamp = message.a;
				var region = message.b;
				if (!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v2 = _Utils_Tuple2(model.a.b.ad, model.w);
					if ((!_v2.a.$) && (!_v2.b.$)) {
						var geometry = _v2.a.a;
						var choice = _v2.b.a;
						return _Utils_Tuple2(
							_Utils_update(
								model,
								{
									w: A3($author$project$Snap$select, geometry, region, choice)
								}),
							_List_Nil);
					} else {
						return _Utils_Tuple2(model, _List_Nil);
					}
				}
			case 4:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!_Utils_eq(model.j, $elm$core$Maybe$Nothing)) || ((!$author$project$Shell$available(model.a.b)) || (!A2(
					$elm$core$Maybe$withDefault,
					false,
					A2(
						$elm$core$Maybe$map,
						function (caps) {
							return A2($elm$core$List$member, 'snap', caps.d1);
						},
						model.a.b.cR)))))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v3 = _Utils_Tuple2(model.w, model.a.b.ad);
					if ((!_v3.a.$) && (!_v3.b.$)) {
						var choice = _v3.a.a;
						var geometry = _v3.b.a;
						if (!A2($author$project$Snap$valid, geometry, choice)) {
							return _Utils_Tuple2(model, _List_Nil);
						} else {
							var _v4 = _Utils_Tuple2(
								$author$project$Snap$proposal(choice),
								$elm$core$List$head(
									A2(
										$elm$core$List$filter,
										function (family) {
											return _Utils_eq(family.v, choice.ed) && family.ca;
										},
										A2(
											$elm$core$List$concatMap,
											function ($) {
												return $.am;
											},
											$author$project$TaskbarShell$groups(model.a)))));
							if ((!_v4.a.$) && (!_v4.b.$)) {
								var proposed = _v4.a.a;
								var family = _v4.b.a;
								var _v5 = A2(
									$author$project$Desktop$chooseFamily,
									family,
									_Utils_update(
										model,
										{w: $elm$core$Maybe$Nothing}));
								var next = _v5.a;
								var effects = _v5.b;
								return _Utils_Tuple2(
									_Utils_update(
										next,
										{
											j: A2(
												$elm$core$Maybe$map,
												function (pending) {
													return _Utils_update(
														pending,
														{
															aZ: $elm$core$Maybe$Just(proposed)
														});
												},
												next.j)
										}),
									effects);
							} else {
								return _Utils_Tuple2(model, _List_Nil);
							}
						}
					} else {
						return _Utils_Tuple2(model, _List_Nil);
					}
				}
			case 5:
				var stamp = message.a;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || _Utils_eq(model.w, $elm$core$Maybe$Nothing)) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{w: $elm$core$Maybe$Nothing})),
					_List_Nil);
			case 6:
				return _Utils_eq(model.w, $elm$core$Maybe$Nothing) ? _Utils_Tuple2(model, _List_Nil) : A2(
					$author$project$Desktop$windowBase,
					$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{E: 'Output changed. Open snapping again.', w: $elm$core$Maybe$Nothing})));
			case 27:
				var token = message.a;
				return (!_Utils_eq(
					A2(
						$elm$core$Maybe$map,
						function ($) {
							return $.bh;
						},
						model.j),
					$elm$core$Maybe$Just(token))) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
					_Utils_update(
						model,
						{j: $elm$core$Maybe$Nothing, E: 'Window information took too long. Refresh windows, then choose again.'}),
					_List_Nil);
			case 28:
				return ((!_Utils_eq(model.j, $elm$core$Maybe$Nothing)) || $elm$core$String$isEmpty(model.E)) ? _Utils_Tuple2(model, _List_Nil) : A2(
					$author$project$Desktop$windowBase,
					$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
					_Utils_update(
						model,
						{E: ''}));
			case 8:
				var scope = message.a;
				if (_Utils_eq(scope, model.aM)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v6 = function () {
						var _v7 = $author$project$MenuBridge$currentProvider(model.a.k);
						if (_v7.$ === 1) {
							return _Utils_Tuple2(model, _List_Nil);
						} else {
							var provider = _v7.a;
							return A2(
								$author$project$Desktop$windowBase,
								$author$project$TaskbarShell$MenuEvent(
									$author$project$Menu$Invalidate(
										$author$project$Provider$getBinding(provider))),
								model);
						}
					}();
					var retired = _v6.a;
					var effects = _v6.b;
					return _Utils_Tuple2(
						$author$project$Desktop$retireSwitcher(
							_Utils_update(
								retired,
								{F: $elm$core$Maybe$Nothing, a9: false, aM: scope, r: $elm$core$Maybe$Nothing, w: $elm$core$Maybe$Nothing})),
						effects);
				}
			case 7:
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
									{cn: output, cr: provider});
							}),
						A2($elm$json$Json$Decode$field, 'surfaceProtocol', $elm$json$Json$Decode$int),
						A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
						A2($elm$json$Json$Decode$field, 'outputId', positive),
						A2($elm$json$Json$Decode$field, 'providerId', positive)));
				var _v8 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
				if (((!_v8.$) && (_v8.a.a === 2)) && (_v8.a.b === 'surface-owner')) {
					var _v9 = _v8.a;
					var owner = _v9.c;
					if (model.a9) {
						return _Utils_Tuple2(model, _List_Nil);
					} else {
						var _v10 = model.aM;
						if (_v10.$ === 1) {
							return _Utils_Tuple2(
								_Utils_update(
									model,
									{
										aM: $elm$core$Maybe$Just(owner)
									}),
								_List_Nil);
						} else {
							var previous = _v10.a;
							if (_Utils_eq(previous, owner)) {
								return _Utils_Tuple2(model, _List_Nil);
							} else {
								var retired = function () {
									var _v11 = $author$project$MenuBridge$currentProvider(model.a.k);
									if (_v11.$ === 1) {
										return model;
									} else {
										var provider = _v11.a;
										return A2(
											$author$project$Desktop$windowBase,
											$author$project$TaskbarShell$MenuEvent(
												$author$project$Menu$Invalidate(
													$author$project$Provider$getBinding(provider))),
											model).a;
									}
								}();
								return _Utils_Tuple2(
									$author$project$Desktop$retireSwitcher(
										_Utils_update(
											retired,
											{F: $elm$core$Maybe$Nothing, a9: true, aM: $elm$core$Maybe$Nothing, r: $elm$core$Maybe$Nothing, w: $elm$core$Maybe$Nothing})),
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
				if (model.a9 || ((!_Utils_eq(model.j, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(
					$author$project$MenuBridge$preparedSnapshot(model.a.k),
					$elm$core$Maybe$Nothing)) || ((!_Utils_eq(
					$author$project$Shell$capture(model.a.b),
					$elm$core$Maybe$Just(stamp))) || (!$author$project$Shell$available(model.a.b)))))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v12 = model.a.b.R.aa;
					if (_v12.$ === 1) {
						return _Utils_Tuple2(model, _List_Nil);
					} else {
						var observed = _v12.a;
						var _v13 = model.aM;
						if (_v13.$ === 1) {
							return _Utils_Tuple2(model, _List_Nil);
						} else {
							var owner = _v13.a;
							var _v14 = A3(
								$author$project$NativeProvider$fromShell,
								{dG: observed.A.dj, cn: owner.cn, cr: owner.cr},
								root,
								model.a.b);
							if (_v14.$ === 1) {
								return _Utils_Tuple2(model, _List_Nil);
							} else {
								var provider = _v14.a;
								var _v15 = A2(
									$author$project$Desktop$windowBase,
									$author$project$TaskbarShell$OpenMenu(provider),
									model);
								var next = _v15.a;
								var effects = _v15.b;
								return _Utils_eq(
									$author$project$MenuBridge$menuSnapshot(next.a.k).aq,
									$author$project$MenuBridge$menuSnapshot(model.a.k).aq) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
									$author$project$Desktop$retireSwitcher(
										_Utils_update(
											next,
											{
												n: $elm$core$Maybe$Nothing,
												F: A2(
													$elm$core$Maybe$andThen,
													function (binding) {
														return A2(
															$elm$core$Maybe$map,
															function (group) {
																return {
																	d: binding,
																	aT: $author$project$Desktop$TaskbarGroup(group.ap),
																	m: $elm$core$Maybe$Just(observed.A.m)
																};
															},
															$elm$core$List$head(
																A2(
																	$elm$core$List$filter,
																	function (group) {
																		return A2(
																			$elm$core$List$any,
																			function (family) {
																				return _Utils_eq(family.v, root);
																			},
																			group.am);
																	},
																	$author$project$TaskbarShell$groups(model.a))));
													},
													model.a.b.d),
												q: false,
												t: false,
												r: $elm$core$Maybe$Nothing,
												w: $elm$core$Maybe$Nothing
											})),
									effects);
							}
						}
					}
				}
			case 12:
				var stamp = message.a;
				var direction = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!_Utils_eq(model.j, $elm$core$Maybe$Nothing)) || ((!$author$project$Shell$available(model.a.b)) || (!_Utils_eq(
					$author$project$MenuBridge$preparedSnapshot(model.a.k),
					$elm$core$Maybe$Nothing))))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v16 = $author$project$UInt64$next(
						$author$project$Switcher$generation(model.e));
					if (_v16.$ === 1) {
						return _Utils_Tuple2(
							$author$project$Desktop$retireSwitcher(model),
							_List_Nil);
					} else {
						var generation = _v16.a;
						var base = A2(
							$elm$core$Maybe$withDefault,
							model,
							A2(
								$elm$core$Maybe$map,
								function (menu) {
									return A2(
										$author$project$Desktop$windowBase,
										$author$project$TaskbarShell$MenuEvent(
											$author$project$Menu$Dismiss(menu.bu)),
										model).a;
								},
								$author$project$MenuBridge$menuSnapshot(model.a.k).aq));
						var origin = A2(
							$elm$core$Maybe$andThen,
							function (observed) {
								return A2(
									$elm$core$Maybe$andThen,
									function (root) {
										return A2($author$project$ActionProjection$rootOf, root, observed.dk);
									},
									$author$project$ActionProjection$focused(observed.dk));
							},
							base.a.b.R.aa);
						var windows = base.a;
						var _v17 = A4($author$project$Switcher$step, generation, 1, direction, base.e);
						var switcher = _v17.a;
						var opened = $author$project$Desktop$advance(
							_Utils_update(
								base,
								{
									n: $elm$core$Maybe$Nothing,
									F: $elm$core$Maybe$Nothing,
									O: $elm$core$Maybe$Nothing,
									q: false,
									t: false,
									r: $elm$core$Maybe$Nothing,
									w: $elm$core$Maybe$Nothing,
									e: switcher,
									aj: $elm$core$Maybe$Nothing,
									bG: origin,
									a: _Utils_update(
										windows,
										{J: $elm$core$Maybe$Nothing})
								}));
						var _v18 = A2(
							$author$project$Desktop$windowBase,
							$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
							opened);
						var refreshing = _v18.a;
						var commands = _v18.b;
						var _v19 = $author$project$Desktop$readSwitcherHistory(refreshing);
						var next = _v19.a;
						var history = _v19.b;
						return _Utils_Tuple2(
							next,
							_Utils_ap(commands, history));
					}
				}
			case 13:
				var stamp = message.a;
				var direction = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!$author$project$Desktop$switcherOpen(model))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v20 = (!_Utils_eq(model.O, $elm$core$Maybe$Nothing)) ? _Utils_Tuple2(
						A2($author$project$Switcher$navigate, direction, model.e),
						$elm$core$Maybe$Nothing) : A4(
						$author$project$Switcher$step,
						$author$project$Switcher$generation(model.e),
						$author$project$Switcher$lastStep(model.e) + 1,
						direction,
						model.e);
					var switcher = _v20.a;
					var chosen = _v20.b;
					var next = $author$project$Desktop$advance(
						_Utils_update(
							model,
							{e: switcher}));
					if (!chosen.$) {
						var family = chosen.a;
						return A2($author$project$Desktop$chooseFamily, family, next);
					} else {
						return _Utils_Tuple2(
							next,
							$author$project$Desktop$switcherFocus(next));
					}
				}
			case 14:
				var stamp = message.a;
				var root = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!$author$project$Desktop$switcherOpen(model))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					if (!A2(
						$elm$core$List$any,
						function (family) {
							return _Utils_eq(family.v, root);
						},
						$author$project$Switcher$entries(model.e))) {
						return _Utils_Tuple2(model, _List_Nil);
					} else {
						var switcher = A3(
							$author$project$Switcher$choose,
							$author$project$Switcher$generation(model.e),
							root,
							model.e);
						var _v22 = A2(
							$author$project$Switcher$commit,
							$author$project$Switcher$generation(switcher),
							switcher);
						var resolved = _v22.a;
						var selected = _v22.b;
						if (!selected.$) {
							var family = selected.a;
							return A2(
								$author$project$Desktop$chooseFamily,
								family,
								$author$project$Desktop$advance(
									_Utils_update(
										model,
										{e: resolved})));
						} else {
							return _Utils_Tuple2(model, _List_Nil);
						}
					}
				}
			case 15:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!$author$project$Desktop$switcherOpen(model))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v24 = A2(
						$author$project$Switcher$commit,
						$author$project$Switcher$generation(model.e),
						model.e);
					var switcher = _v24.a;
					var selected = _v24.b;
					if (!selected.$) {
						var family = selected.a;
						return A2(
							$author$project$Desktop$chooseFamily,
							family,
							$author$project$Desktop$advance(
								_Utils_update(
									model,
									{e: switcher})));
					} else {
						return _Utils_Tuple2(model, _List_Nil);
					}
				}
			case 16:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!$author$project$Desktop$switcherOpen(model))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var closed = $author$project$Desktop$advance(
						$author$project$Desktop$retireSwitcher(model));
					var _v26 = _Utils_Tuple3(
						model.O,
						model.a.b.d,
						$author$project$UInt64$next(model.o));
					if (((!_v26.a.$) && (!_v26.b.$)) && (!_v26.c.$)) {
						var chord = _v26.a.a;
						var binding = _v26.b.a;
						var request = _v26.c.a;
						var _v27 = A2(
							$author$project$Desktop$windowBase,
							$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
							_Utils_update(
								closed,
								{o: request}));
						var next = _v27.a;
						var reads = _v27.b;
						return _Utils_Tuple2(
							next,
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
												$elm$json$Json$Encode$string('switcher-cancel-request')),
												_Utils_Tuple2(
												'binding',
												$author$project$Binding$encode(binding)),
												_Utils_Tuple2(
												'requestId',
												$elm$json$Json$Encode$string(
													$author$project$UInt64$string(request))),
												_Utils_Tuple2(
												'chord',
												$elm$json$Json$Encode$string(
													$author$project$UInt64$string(chord.dP)))
											]))),
								reads));
					} else {
						return A2(
							$author$project$Desktop$windowBase,
							$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
							closed);
					}
				}
			case 0:
				var value = message.a;
				var _v28 = A2($author$project$Desktop$window, value, model);
				var next = _v28.a;
				var effects = _v28.b;
				var _v29 = $author$project$Desktop$syncSwitcher(next);
				var synced = _v29.a;
				var commands = _v29.b;
				return ((!_Utils_eq(next.a.J, $elm$core$Maybe$Nothing)) && (!_Utils_eq(next.a.J, model.a.J))) ? _Utils_Tuple2(
					$author$project$Desktop$retireSwitcher(
						_Utils_update(
							next,
							{n: $elm$core$Maybe$Nothing, F: $elm$core$Maybe$Nothing, q: false, t: false, r: $elm$core$Maybe$Nothing, w: $elm$core$Maybe$Nothing})),
					effects) : _Utils_Tuple2(
					synced,
					_Utils_ap(effects, commands));
			case 9:
				var raw = message.a;
				var _v30 = A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
					raw);
				_v30$5:
				while (true) {
					if (!_v30.$) {
						switch (_v30.a) {
							case 'switcher-journal':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'chord']),
									A5(
										$elm$json$Json$Decode$map4,
										F4(
											function (_v32, binding, request, chord) {
												return {d: binding, aC: chord, o: request};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'chord', $author$project$Desktop$nativeChordDecoder)));
								var _v31 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v31.$) {
									var receipt = _v31.a;
									return ((!_Utils_eq(
										model.a.b.d,
										$elm$core$Maybe$Just(receipt.d))) || ((!model.a.b.G) || (model.a.b.G === 3))) ? _Utils_Tuple2(model, _List_Nil) : A2($author$project$Desktop$receiveChord, receipt.aC, model);
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'activation-history':
								var positive = A2(
									$elm$json$Json$Decode$andThen,
									function (value) {
										return _Utils_eq(value, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Zero history identity') : $elm$json$Json$Decode$succeed(value);
									},
									$author$project$UInt64$decoder);
								var roots = A2(
									$elm$json$Json$Decode$andThen,
									function (rows) {
										return (($elm$core$List$length(rows) <= 256) && _Utils_eq(
											$elm$core$List$length(
												A3(
													$elm$core$List$foldl,
													F2(
														function (root, unique) {
															return A2($elm$core$List$member, root, unique) ? unique : A2($elm$core$List$cons, root, unique);
														}),
													_List_Nil,
													rows)),
											$elm$core$List$length(rows))) ? $elm$json$Json$Decode$succeed(rows) : $elm$json$Json$Decode$fail('History bounds/duplicates');
									},
									$elm$json$Json$Decode$list(positive));
								var context = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['lifetime', 'epoch', 'output', 'revision']),
									A5(
										$elm$json$Json$Decode$map4,
										F4(
											function (lifetime, epoch, output, revision) {
												return {dM: epoch, dY: lifetime, m: output, dj: revision};
											}),
										A2($elm$json$Json$Decode$field, 'lifetime', positive),
										A2($elm$json$Json$Decode$field, 'epoch', positive),
										A2($elm$json$Json$Decode$field, 'output', positive),
										A2($elm$json$Json$Decode$field, 'revision', positive)));
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'context', 'roots']),
									A6(
										$elm$json$Json$Decode$map5,
										F5(
											function (_v34, binding, request, scope, rows) {
												return {d: binding, A: scope, o: request, ah: rows};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', positive),
										A2($elm$json$Json$Decode$field, 'context', context),
										A2($elm$json$Json$Decode$field, 'roots', roots)));
								var _v33 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v33.$) {
									var receipt = _v33.a;
									return ((!$author$project$Desktop$switcherOpen(model)) || ((!_Utils_eq(
										model.a.b.d,
										$elm$core$Maybe$Just(receipt.d))) || (!_Utils_eq(
										model.ai,
										$elm$core$Maybe$Just(receipt.o))))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Desktop$syncSwitcher(
										_Utils_update(
											model,
											{
												ai: $elm$core$Maybe$Nothing,
												aj: $elm$core$Maybe$Just(
													{A: receipt.A, ah: receipt.ah})
											}));
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'application-catalog':
								var decoder = A2(
									$elm$json$Json$Decode$andThen,
									function (pairs) {
										var fields = A2($elm$core$List$map, $elm$core$Tuple$first, pairs);
										var legacy = !A2($elm$core$List$member, 'preferences', fields);
										return A2(
											$author$project$Desktop$strict,
											_Utils_ap(
												_List_fromArray(
													['protocolVersion', 'kind', 'binding', 'requestId', 'snapshot']),
												legacy ? _List_Nil : _List_fromArray(
													['preferences'])),
											A6(
												$elm$json$Json$Decode$map5,
												F5(
													function (_v36, binding, request, snapshot, pins) {
														return {d: binding, y: pins, o: request, bF: snapshot};
													}),
												$author$project$Desktop$version,
												A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
												A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
												A2($elm$json$Json$Decode$field, 'snapshot', $elm$json$Json$Decode$value),
												legacy ? $elm$json$Json$Decode$succeed($elm$core$Maybe$Nothing) : A2(
													$elm$json$Json$Decode$field,
													'preferences',
													$elm$json$Json$Decode$nullable($author$project$Pins$decoder))));
									},
									$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
								var _v35 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v35.$) {
									var receipt = _v35.a;
									if ((!(!model.a.b.G)) && (_Utils_eq(
										model.a.b.d,
										$elm$core$Maybe$Just(receipt.d)) && _Utils_eq(
										model.n,
										$elm$core$Maybe$Just(receipt.o)))) {
										var target = 'launcher-search';
										var next = $author$project$Desktop$advance(
											_Utils_update(
												model,
												{
													ak: $elm$core$Result$toMaybe(
														$author$project$Catalog$decode(receipt.bF)),
													aS: $elm$core$Maybe$Nothing,
													n: $elm$core$Maybe$Nothing,
													p: A2($author$project$Launch$catalog, receipt.bF, model.p),
													y: A2($author$project$Pins$observe, receipt.y, model.y)
												}));
										return _Utils_Tuple2(
											next,
											next.q ? _List_fromArray(
												[
													$author$project$Desktop$Focus(target)
												]) : _List_Nil);
									} else {
										return _Utils_Tuple2(model, _List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'taskbar-pins-outcome':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'status', 'preferences']),
									A6(
										$elm$json$Json$Decode$map5,
										F5(
											function (_v38, binding, request, status, pins) {
												return {d: binding, y: pins, o: request, cx: status};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string),
										A2(
											$elm$json$Json$Decode$field,
											'preferences',
											$elm$json$Json$Decode$nullable($author$project$Pins$decoder))));
								var _v37 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v37.$) {
									var receipt = _v37.a;
									if ((!model.a.b.G) || ((!_Utils_eq(
										model.a.b.d,
										$elm$core$Maybe$Just(receipt.d))) || (!A2(
										$elm$core$List$member,
										receipt.cx,
										_List_fromArray(
											['Saved', 'Refused', 'Unknown']))))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var pins = A4($author$project$Pins$receive, receipt.o, receipt.cx, receipt.y, model.y);
										return _Utils_Tuple2(
											_Utils_update(
												model,
												{y: pins}),
											(model.q && (!_Utils_eq(pins, model.y))) ? _List_fromArray(
												[
													$author$project$Desktop$Focus('launcher-search')
												]) : _List_Nil);
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
											function (_v41, binding, outcome) {
												return _Utils_Tuple2(binding, outcome);
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'outcome', $elm$json$Json$Decode$value)));
								var _v39 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v39.$) {
									var _v40 = _v39.a;
									var binding = _v40.a;
									var outcome = _v40.b;
									if ((!(!model.a.b.G)) && _Utils_eq(
										model.a.b.d,
										$elm$core$Maybe$Just(binding))) {
										var launch = A3(
											$author$project$Launch$receive,
											$author$project$Desktop$host(binding),
											outcome,
											model.p);
										var refused = ($author$project$Launch$status(model.p) === 'Pending') && ($author$project$Launch$status(launch) === 'Refused');
										var next = _Utils_update(
											model,
											{
												p: launch,
												q: refused ? true : (model.q && ($author$project$Launch$status(launch) !== 'Submitted'))
											});
										return _Utils_Tuple2(
											next,
											refused ? _List_fromArray(
												[
													$author$project$Desktop$Focus('launcher-search')
												]) : _List_Nil);
									} else {
										return _Utils_Tuple2(model, _List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							default:
								break _v30$5;
						}
					} else {
						break _v30$5;
					}
				}
				var _v42 = A2(
					$author$project$Desktop$window,
					$author$project$TaskbarShell$Native(
						$author$project$Shell$Incoming(raw)),
					model);
				var next = _v42.a;
				var effects = _v42.b;
				var _v43 = $author$project$Desktop$syncSwitcher(next);
				var synced = _v43.a;
				var commands = _v43.b;
				return _Utils_Tuple2(
					synced,
					_Utils_ap(effects, commands));
			case 10:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!_Utils_eq(
					$author$project$MenuBridge$preparedSnapshot(model.a.k),
					$elm$core$Maybe$Nothing))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var base = function () {
						var _v45 = $author$project$MenuBridge$menuSnapshot(model.a.k).aq;
						if (_v45.$ === 1) {
							return model;
						} else {
							var menu = _v45.a;
							return A2(
								$author$project$Desktop$windowBase,
								$author$project$TaskbarShell$MenuEvent(
									$author$project$Menu$Dismiss(menu.bu)),
								model).a;
						}
					}();
					var windows = base.a;
					var retired = $author$project$Desktop$advance(
						$author$project$Desktop$retireSwitcher(
							_Utils_update(
								base,
								{
									ak: $elm$core$Maybe$Nothing,
									aS: $elm$core$Maybe$Nothing,
									n: $elm$core$Maybe$Nothing,
									p: A2($author$project$Launch$catalog, $elm$json$Json$Encode$null, model.p),
									F: $elm$core$Maybe$Nothing,
									q: true,
									t: false,
									r: $elm$core$Maybe$Nothing,
									w: $elm$core$Maybe$Nothing,
									a: _Utils_update(
										windows,
										{J: $elm$core$Maybe$Nothing})
								})));
					var _v44 = _Utils_Tuple2(
						model.a.b.d,
						$author$project$UInt64$next(model.o));
					if ((!_v44.a.$) && (!_v44.b.$)) {
						var binding = _v44.a.a;
						var request = _v44.b.a;
						return ((!model.a.b.G) || _Utils_eq(retired.aO, $elm$core$Maybe$Nothing)) ? _Utils_Tuple2(retired, _List_Nil) : _Utils_Tuple2(
							_Utils_update(
								retired,
								{
									n: $elm$core$Maybe$Just(request),
									o: request
								}),
							_List_fromArray(
								[
									A2($author$project$Desktop$catalogRequest, binding, request),
									$author$project$Desktop$Focus('launcher-search')
								]));
					} else {
						return _Utils_Tuple2(retired, _List_Nil);
					}
				}
			case 24:
				var binding = message.a;
				var request = message.b;
				return (!A3($author$project$Desktop$canProveCatalogUnsent, binding, request, model)) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
					_Utils_update(
						model,
						{
							aS: $elm$core$Maybe$Just(
								{d: binding, o: request}),
							n: $elm$core$Maybe$Nothing
						}),
					_List_Nil);
			case 20:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.q)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var next = $author$project$Desktop$advance(
						_Utils_update(
							model,
							{n: $elm$core$Maybe$Nothing, q: false}));
					return _Utils_Tuple2(
						next,
						_List_fromArray(
							[
								$author$project$Desktop$Focus(
								A2($author$project$Desktop$key, next, 'control:opener'))
							]));
				}
			case 11:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!_Utils_eq(model.j, $elm$core$Maybe$Nothing)) || ((!$author$project$Shell$available(model.a.b)) || (!_Utils_eq(
					$author$project$MenuBridge$preparedSnapshot(model.a.k),
					$elm$core$Maybe$Nothing))))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var base = A2(
						$elm$core$Maybe$withDefault,
						model,
						A2(
							$elm$core$Maybe$map,
							function (menu) {
								return A2(
									$author$project$Desktop$windowBase,
									$author$project$TaskbarShell$MenuEvent(
										$author$project$Menu$Dismiss(menu.bu)),
									model).a;
							},
							$author$project$MenuBridge$menuSnapshot(model.a.k).aq));
					var windows = base.a;
					var next = $author$project$Desktop$advance(
						$author$project$Desktop$retireSwitcher(
							_Utils_update(
								base,
								{
									n: $elm$core$Maybe$Nothing,
									F: $elm$core$Maybe$Nothing,
									q: false,
									t: true,
									ag: $elm$core$Maybe$Nothing,
									r: $elm$core$Maybe$Nothing,
									w: $elm$core$Maybe$Nothing,
									a: _Utils_update(
										windows,
										{J: $elm$core$Maybe$Nothing})
								})));
					var focus = A2(
						$elm$core$Maybe$withDefault,
						A2($author$project$Desktop$key, next, 'overview:all'),
						A2(
							$elm$core$Maybe$map,
							function (workspace) {
								return A2($author$project$Desktop$key, next, 'overview:workspace:' + workspace);
							},
							$author$project$TaskView$activeWorkspace(next.a.b)));
					return _Utils_Tuple2(
						next,
						_List_fromArray(
							[
								$author$project$Desktop$Focus(focus)
							]));
				}
			case 17:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.t)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var target = A2(
						$elm$core$Maybe$map,
						function (binding) {
							return {
								d: binding,
								aT: $author$project$Desktop$OverviewOpener,
								m: A2(
									$elm$core$Maybe$map,
									A2(
										$elm$core$Basics$composeR,
										function ($) {
											return $.A;
										},
										function ($) {
											return $.m;
										}),
									model.a.b.R.aa)
							};
						},
						model.a.b.d);
					var next = $author$project$Desktop$advance(
						_Utils_update(
							model,
							{t: false, ag: $elm$core$Maybe$Nothing}));
					var _v46 = A2(
						$author$project$Desktop$windowBase,
						$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
						next);
					var refreshing = _v46.a;
					var commands = _v46.b;
					return _Utils_Tuple2(
						_Utils_update(
							refreshing,
							{r: target}),
						commands);
				}
			case 18:
				var stamp = message.a;
				var selected = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.t) || _Utils_eq(selected, model.ag))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var next = $author$project$Desktop$advance(
						_Utils_update(
							model,
							{ag: selected}));
					var exists = A2(
						$elm$core$Maybe$withDefault,
						true,
						A2(
							$elm$core$Maybe$map,
							function (workspace) {
								return A2(
									$elm$core$Maybe$withDefault,
									false,
									A2(
										$elm$core$Maybe$map,
										$elm$core$List$any(
											function (g) {
												return _Utils_eq(g.bX, workspace);
											}),
										$author$project$TaskView$groups(model.a.b)));
							},
							selected));
					return (!exists) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
						next,
						_List_fromArray(
							[
								$author$project$Desktop$Focus(
								A2(
									$author$project$Desktop$key,
									next,
									A2(
										$elm$core$Maybe$withDefault,
										'overview:all',
										A2(
											$elm$core$Maybe$map,
											$elm$core$Basics$append('overview:workspace:'),
											selected))))
							]));
				}
			case 19:
				var stamp = message.a;
				var root = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.t) || ((!_Utils_eq(model.j, $elm$core$Maybe$Nothing)) || (!$author$project$Shell$available(model.a.b))))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var selected = $elm$core$List$head(
						A2(
							$elm$core$List$filter,
							function (family) {
								return _Utils_eq(family.v, root) && (family.ca && (!A3($author$project$MenuBridge$blockedFor, root, model.a.b, model.a.k)));
							},
							A2(
								$elm$core$List$concatMap,
								function ($) {
									return $.a;
								},
								A2(
									$elm$core$List$filter,
									function (g) {
										return _Utils_eq(model.ag, $elm$core$Maybe$Nothing) || _Utils_eq(
											model.ag,
											$elm$core$Maybe$Just(g.bX));
									},
									A2(
										$elm$core$Maybe$withDefault,
										_List_Nil,
										$author$project$TaskView$groups(model.a.b))))));
					var _v47 = _Utils_Tuple3(selected, model.a.b.d, model.a.b.R.aa);
					if (((!_v47.a.$) && (!_v47.b.$)) && (!_v47.c.$)) {
						var family = _v47.a.a;
						var binding = _v47.b.a;
						var observed = _v47.c.a;
						var _v48 = A2(
							$author$project$Desktop$windowBase,
							$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
							_Utils_update(
								model,
								{E: '', t: false}));
						var next = _v48.a;
						var effects = _v48.b;
						var _v49 = next.a.b.n;
						if (!_v49.$) {
							var request = _v49.a;
							var token = A2($author$project$Desktop$ChoiceToken, binding, request);
							return _Utils_Tuple2(
								_Utils_update(
									next,
									{
										j: $elm$core$Maybe$Just(
											{b9: family.b9, d: binding, aC: $elm$core$Maybe$Nothing, m: observed.A.m, aZ: $elm$core$Maybe$Nothing, v: root, bh: token})
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
					} else {
						return _Utils_Tuple2(model, _List_Nil);
					}
				}
			case 21:
				var stamp = message.a;
				var query = message.b;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.q) || (_Utils_eq(query, model.b$) || (($elm$core$String$length(query) > 256) || A2(
					$elm$core$String$any,
					function (c) {
						return ($elm$core$Char$toCode(c) < 32) || ($elm$core$Char$toCode(c) === 127);
					},
					query))))) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{b$: query})),
					_List_Nil);
			case 22:
				var stamp = message.a;
				var identity = message.b;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.q) || ((!$author$project$Pins$writable(model.y)) || ((!A2(
					$elm$core$List$member,
					identity,
					$author$project$Desktop$pinIdentities(model))) && _Utils_eq(
					A2(
						$elm$core$Maybe$andThen,
						$author$project$Catalog$lookup(identity),
						model.ak),
					$elm$core$Maybe$Nothing))))) ? _Utils_Tuple2(model, _List_Nil) : A2(
					$author$project$Desktop$savePins,
					A2(
						$author$project$Pins$toggle,
						identity,
						$author$project$Desktop$pinIdentities(model)),
					model);
			case 23:
				var stamp = message.a;
				var identity = message.b;
				var direction = message.c;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.q) || (!$author$project$Pins$writable(model.y)))) ? _Utils_Tuple2(model, _List_Nil) : A2(
					$author$project$Desktop$savePins,
					A3(
						$author$project$Pins$move,
						identity,
						direction,
						$author$project$Desktop$pinIdentities(model)),
					model);
			case 25:
				var selection = message.a;
				if (!_Utils_eq(
					$author$project$MenuBridge$preparedSnapshot(model.a.k),
					$elm$core$Maybe$Nothing)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v50 = A2($author$project$Launch$start, selection, model.p);
					var launch = _v50.a;
					var intent = _v50.b;
					var _v51 = _Utils_Tuple2(intent, model.a.b.d);
					if ((!_v51.a.$) && (!_v51.b.$)) {
						var wire = _v51.a.a;
						var binding = _v51.b.a;
						return _Utils_Tuple2(
							$author$project$Desktop$retireSwitcher(
								_Utils_update(
									model,
									{n: $elm$core$Maybe$Nothing, p: launch, q: false, t: false})),
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
								{p: launch}),
							_List_Nil);
					}
				}
			case 26:
				var token = message.a;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							p: A2($author$project$Launch$timeout, token, model.p)
						}),
					_List_Nil);
			default:
				var token = message.a;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							p: A2($author$project$Launch$acknowledgeUnknown, token, model.p)
						}),
					_List_Nil);
		}
	});
var $author$project$SurfaceController$applyOrdinary = F2(
	function (message, current) {
		var model = current;
		if (model.Z) {
			return _Utils_Tuple2(current, _List_Nil);
		} else {
			var oldMode = $author$project$Surface$mode(model.c);
			var _v0 = A2($author$project$Desktop$update, message, model.c);
			var next = _v0.a;
			var effects = _v0.b;
			var changed = !_Utils_eq(next, model.c);
			var nextMode = $author$project$Surface$mode(next);
			var newLease = (nextMode !== 'closed') && ((!_Utils_eq(nextMode, oldMode)) || ((!_Utils_eq(
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.bu;
					},
					$author$project$MenuBridge$menuSnapshot(model.c.a.k).aq),
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.bu;
					},
					$author$project$MenuBridge$menuSnapshot(next.a.k).aq))) || (((nextMode === 'picker') && (!_Utils_eq(
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.dP;
					},
					model.c.a.J),
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.dP;
					},
					next.a.J)))) || ((nextMode === 'switcher') && (!_Utils_eq(
				$author$project$Switcher$generation(model.c.e),
				$author$project$Switcher$generation(next.e)))))));
			var lease = newLease ? $author$project$UInt64$next(model.aI) : $elm$core$Maybe$Just(model.aI);
			if ((!changed) && $elm$core$List$isEmpty(effects)) {
				return _Utils_Tuple2(current, _List_Nil);
			} else {
				var stableSurface = (!_Utils_eq(model.bC, $author$project$UInt64$zero)) && ((!newLease) && ($elm$core$List$isEmpty(effects) && _Utils_eq(
					A2(
						$elm$json$Json$Encode$encode,
						0,
						A3($author$project$Surface$packet, model.bC, model.aI, next)),
					A2(
						$elm$json$Json$Encode$encode,
						0,
						$author$project$SurfaceController$frame(current)))));
				var stableApplications = function () {
					if (((!message.$) && (!message.a.$)) && (message.a.a.$ === 11)) {
						return (oldMode === 'applications') && ((nextMode === 'applications') && ((!newLease) && _Utils_eq(
							A2(
								$elm$json$Json$Encode$encode,
								0,
								A3($author$project$Surface$packet, model.bC, model.aI, next)),
							A2(
								$elm$json$Json$Encode$encode,
								0,
								$author$project$SurfaceController$frame(current)))));
					} else {
						return false;
					}
				}();
				if (stableSurface || stableApplications) {
					return _Utils_Tuple2(
						_Utils_update(
							model,
							{c: next}),
						A2($elm$core$List$map, $author$project$SurfaceController$DesktopEffect, effects));
				} else {
					var _v1 = _Utils_Tuple2(
						$author$project$UInt64$next(model.bC),
						lease);
					if ((!_v1.a.$) && (!_v1.b.$)) {
						var publication = _v1.a.a;
						var token = _v1.b.a;
						var result = _Utils_update(
							model,
							{c: next, aI: token, bC: publication});
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
								{Z: true}),
							_List_Nil);
					}
				}
			}
		}
	});
var $author$project$ReconciliationTracking$legacy = F3(
	function (raw, shell, model) {
		if ((!_Utils_eq(
			A2(
				$elm$json$Json$Decode$decodeValue,
				A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
				raw),
			$elm$core$Result$Ok('host-uncertain'))) || ((shell.G !== 1) || ((!_Utils_eq(
			$elm$core$Result$toMaybe(
				A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
					raw)),
			shell.d)) || (!_Utils_eq(
			A2(
				$elm$json$Json$Decode$decodeValue,
				A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int),
				raw),
			$elm$core$Result$Ok(3)))))) {
			return model;
		} else {
			var _v0 = A2(
				$elm$json$Json$Decode$decodeValue,
				A2($elm$json$Json$Decode$field, 'intent', $author$project$Effects$intentDecoder),
				raw);
			if (_v0.$ === 1) {
				return model;
			} else {
				var intent = _v0.a;
				var protocol = A2(
					$elm$core$Result$withDefault,
					1,
					A2(
						$elm$json$Json$Decode$decodeValue,
						A2($elm$json$Json$Decode$field, 'effectProtocol', $elm$json$Json$Decode$int),
						raw));
				var entry = {K: intent, b_: protocol};
				return (A2($elm$core$List$member, entry, model.aW) || (($elm$core$List$length(model.aW) >= 64) || (!A2(
					$elm$core$List$any,
					function (t) {
						return _Utils_eq(t.K, intent) && (_Utils_eq(t.Y, protocol) && (t.cx === 4));
					},
					shell.R.l)))) ? model : _Utils_update(
					model,
					{
						aW: A2($elm$core$List$cons, entry, model.aW)
					});
			}
		}
	});
var $author$project$ReceiptRouter$reservationKey = F3(
	function (bound, protocolId, original) {
		var operationValue = function () {
			var _v0 = original.aK;
			switch (_v0.$) {
				case 0:
					return $elm$core$Maybe$Just(0);
				case 1:
					return $elm$core$Maybe$Just(1);
				case 3:
					return $elm$core$Maybe$Just(2);
				case 4:
					return $elm$core$Maybe$Just(3);
				default:
					return $elm$core$Maybe$Nothing;
			}
		}();
		return A2(
			$elm$core$Maybe$map,
			function (op) {
				return {
					K: {A: original.A, dP: original.dP, U: original.U, aK: op, o: original.o},
					c2: bound,
					b_: protocolId
				};
			},
			operationValue);
	});
var $author$project$ReceiptRouter$findReservation = F4(
	function (bound, protocolId, original, _v0) {
		var entries = _v0;
		return A2(
			$elm$core$Maybe$andThen,
			function (_native) {
				return A2(
					$elm$core$Maybe$map,
					function (entry) {
						return _Utils_Tuple2(entry.by, entry.d);
					},
					$elm$core$List$head(
						A2(
							$elm$core$List$filter,
							function (entry) {
								return _Utils_eq(entry.ap, _native);
							},
							entries)));
			},
			A3($author$project$ReceiptRouter$reservationKey, bound, protocolId, original));
	});
var $author$project$Menu$observeUnknown = F3(
	function (local, bound, _v0) {
		var state = _v0;
		return _Utils_update(
			state,
			{
				aq: A2(
					$elm$core$Maybe$map,
					function (menu) {
						return (_Utils_eq(menu.d, bound) && _Utils_eq(
							menu.cx,
							$author$project$Menu$Pending(local))) ? _Utils_update(
							menu,
							{
								cx: $author$project$Menu$Unknown(local)
							}) : menu;
					},
					state.aq),
				d3: A2(
					$elm$core$List$map,
					function (entry) {
						return (_Utils_eq(entry.bu, local) && _Utils_eq(entry.d, bound)) ? _Utils_update(
							entry,
							{aQ: true}) : entry;
					},
					state.d3)
			});
	});
var $author$project$MenuBridge$observeReservationUnknown = F4(
	function (bound, protocolId, intent, model) {
		var state = model;
		return A2(
			$elm$core$Maybe$withDefault,
			model,
			A2(
				$elm$core$Maybe$map,
				function (_v0) {
					var local = _v0.a;
					var original = _v0.b;
					return _Utils_update(
						state,
						{
							aq: A3($author$project$Menu$observeUnknown, local, original, state.aq)
						});
				},
				A4($author$project$ReceiptRouter$findReservation, bound, protocolId, intent, state.V)));
	});
var $author$project$ReconciliationFrame$Context = F4(
	function (lifetime, epoch, output, revision) {
		return {dM: epoch, dY: lifetime, m: output, dj: revision};
	});
var $author$project$ReconciliationFrame$contextDecoder = A2(
	$author$project$ReconciliationFrame$strict,
	_List_fromArray(
		['lifetime', 'epoch', 'output', 'revision']),
	A5(
		$elm$json$Json$Decode$map4,
		$author$project$ReconciliationFrame$Context,
		A2($elm$json$Json$Decode$field, 'lifetime', $author$project$ReconciliationFrame$positive),
		A2($elm$json$Json$Decode$field, 'epoch', $author$project$ReconciliationFrame$positive),
		A2($elm$json$Json$Decode$field, 'output', $author$project$ReconciliationFrame$positive),
		A2($elm$json$Json$Decode$field, 'revision', $author$project$ReconciliationFrame$positive)));
var $author$project$ReconciliationTracking$observed = F4(
	function (raw, before, after, model) {
		var _v0 = A2(
			$elm$json$Json$Decode$decodeValue,
			A3(
				$elm$json$Json$Decode$map2,
				$elm$core$Tuple$pair,
				A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
				A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder)),
			raw);
		if (_v0.$ === 1) {
			return model;
		} else {
			var _v1 = _v0.a;
			var kind = _v1.a;
			var request = _v1.b;
			var geometryContext = A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.A;
				},
				after.ad);
			var geometryAccepted = (kind === 'geometry-facts') && (_Utils_eq(
				before.dQ,
				$elm$core$Maybe$Just(request)) && ((!_Utils_eq(
				after.dQ,
				$elm$core$Maybe$Just(request))) && _Utils_eq(
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.o;
					},
					after.ad),
				$elm$core$Maybe$Just(request))));
			var actionContext = $elm$core$Result$toMaybe(
				A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'context', $author$project$ReconciliationFrame$contextDecoder),
					raw));
			var actionAccepted = (kind === 'action-projection') && (_Utils_eq(
				before.n,
				$elm$core$Maybe$Just(request)) && ((!_Utils_eq(
				after.n,
				$elm$core$Maybe$Just(request))) && ((!_Utils_eq(actionContext, $elm$core$Maybe$Nothing)) && _Utils_eq(
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.A;
					},
					after.R.aa),
				actionContext))));
			return _Utils_update(
				model,
				{
					s: A2(
						$elm$core$List$map,
						function (slot) {
							return _Utils_eq(slot.dc, $elm$core$Maybe$Nothing) ? slot : ((actionAccepted && _Utils_eq(
								slot.a3,
								$elm$core$Maybe$Just(request))) ? _Utils_update(
								slot,
								{
									dB: A2(
										$elm$core$Maybe$map,
										function (context) {
											return {A: context, o: request};
										},
										actionContext)
								}) : ((geometryAccepted && _Utils_eq(
								slot.aF,
								$elm$core$Maybe$Just(request))) ? _Utils_update(
								slot,
								{
									ad: A2(
										$elm$core$Maybe$map,
										function (context) {
											return {A: context, o: request};
										},
										geometryContext)
								}) : slot));
						},
						model.s)
				});
		}
	});
var $author$project$ReconciliationFrame$ReservationReleased = F3(
	function (a, b, c) {
		return {$: 1, a: a, b: b, c: c};
	});
var $author$project$ReconciliationFrame$contextMatches = F2(
	function (binding, context) {
		return A3($author$project$Binding$matchesContext, context.dY, context.dM, binding);
	});
var $author$project$ReconciliationFrame$Record = F5(
	function (schema, effectProtocol, binding, intent, status) {
		return {d: binding, Y: effectProtocol, K: intent, ea: schema, cx: status};
	});
var $author$project$ReconciliationFrame$protocolDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (v) {
		return ((v === 1) || (v === 2)) ? $elm$json$Json$Decode$succeed(v) : $elm$json$Json$Decode$fail('Unsupported effect protocol');
	},
	$elm$json$Json$Decode$int);
var $author$project$ReconciliationFrame$recordDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (record) {
		var operationMatches = (record.Y === 1) ? A2(
			$elm$core$List$member,
			record.K.aK,
			_List_fromArray(
				[$author$project$Effects$Minimize, $author$project$Effects$Restore, $author$project$Effects$Activate])) : A2(
			$elm$core$List$member,
			record.K.aK,
			_List_fromArray(
				[$author$project$Effects$Maximize, $author$project$Effects$RestoreGeometry]));
		return (A3($author$project$Binding$matchesContext, record.K.A.dY, record.K.A.dM, record.d) && operationMatches) ? $elm$json$Json$Decode$succeed(record) : $elm$json$Json$Decode$fail('Record authority or operation/protocol mismatch');
	},
	A2(
		$author$project$ReconciliationFrame$strict,
		_List_fromArray(
			['schema', 'effectProtocol', 'binding', 'intent', 'status']),
		A6(
			$elm$json$Json$Decode$map5,
			$author$project$ReconciliationFrame$Record,
			A2(
				$elm$json$Json$Decode$field,
				'schema',
				$author$project$ReconciliationFrame$exactInt(2)),
			A2($elm$json$Json$Decode$field, 'effectProtocol', $author$project$ReconciliationFrame$protocolDecoder),
			A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
			A2($elm$json$Json$Decode$field, 'intent', $author$project$Effects$intentDecoder),
			A2(
				$elm$json$Json$Decode$field,
				'status',
				A2(
					$elm$json$Json$Decode$map,
					function (_v0) {
						return 4;
					},
					$author$project$ReconciliationFrame$exactString('Unknown'))))));
var $author$project$ReconciliationFrame$Release = F3(
	function (id, proof, observation) {
		return {bu: id, c4: observation, dc: proof};
	});
var $author$project$ReconciliationFrame$Observation = F4(
	function (actionRequestId, geometryRequestId, actionContext, geometryContext) {
		return {az: actionContext, bN: actionRequestId, aE: geometryContext, bV: geometryRequestId};
	});
var $author$project$ReconciliationFrame$observationDecoder = A2(
	$author$project$ReconciliationFrame$strict,
	_List_fromArray(
		['actionRequestId', 'geometryRequestId', 'actionContext', 'geometryContext']),
	A5(
		$elm$json$Json$Decode$map4,
		$author$project$ReconciliationFrame$Observation,
		A2($elm$json$Json$Decode$field, 'actionRequestId', $author$project$ReconciliationFrame$positive),
		A2($elm$json$Json$Decode$field, 'geometryRequestId', $author$project$ReconciliationFrame$positive),
		A2($elm$json$Json$Decode$field, 'actionContext', $author$project$ReconciliationFrame$contextDecoder),
		A2($elm$json$Json$Decode$field, 'geometryContext', $author$project$ReconciliationFrame$contextDecoder)));
var $author$project$ReconciliationFrame$releaseIdDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (($elm$core$String$length(value) === 64) && A2(
			$elm$core$List$all,
			function (c) {
				return ((c >= '0') && (c <= '9')) || ((c >= 'a') && (c <= 'f'));
			},
			$elm$core$String$toList(value))) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Release ID must be64lowerhex');
	},
	$elm$json$Json$Decode$string);
var $author$project$ReconciliationFrame$releaseDecoder = A2(
	$author$project$ReconciliationFrame$strict,
	_List_fromArray(
		['id', 'proof', 'observation']),
	A4(
		$elm$json$Json$Decode$map3,
		$author$project$ReconciliationFrame$Release,
		A2($elm$json$Json$Decode$field, 'id', $author$project$ReconciliationFrame$releaseIdDecoder),
		A2($elm$json$Json$Decode$field, 'proof', $author$project$ReconciliationFrame$proofDecoder),
		A2($elm$json$Json$Decode$field, 'observation', $author$project$ReconciliationFrame$observationDecoder)));
var $author$project$ReconciliationFrame$decodeReleased = F2(
	function (expected, raw) {
		var decoder = A2(
			$author$project$ReconciliationFrame$strict,
			_List_fromArray(
				['protocolVersion', 'kind', 'binding', 'record', 'release']),
			A6(
				$elm$json$Json$Decode$map5,
				F5(
					function (_v1, _v2, binding, record, release) {
						return _Utils_Tuple3(binding, record, release);
					}),
				A2(
					$elm$json$Json$Decode$field,
					'protocolVersion',
					$author$project$ReconciliationFrame$exactInt(3)),
				A2(
					$elm$json$Json$Decode$field,
					'kind',
					$author$project$ReconciliationFrame$exactString('host-reservation-released')),
				A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
				A2($elm$json$Json$Decode$field, 'record', $author$project$ReconciliationFrame$recordDecoder),
				A2($elm$json$Json$Decode$field, 'release', $author$project$ReconciliationFrame$releaseDecoder)));
		return A2(
			$elm$core$Result$andThen,
			function (_v0) {
				var binding = _v0.a;
				var record = _v0.b;
				var release = _v0.c;
				var proof = release.dc;
				var observation = release.c4;
				var expectedValid = A2($author$project$ReconciliationFrame$contextMatches, expected.bU, expected.az) && (A2($author$project$ReconciliationFrame$contextMatches, expected.bU, expected.aE) && _Utils_eq(expected.az.m, expected.aE.m));
				var correlated = _Utils_eq(binding, expected.bU) && (_Utils_eq(record, expected.df) && (_Utils_eq(proof.d, binding) && (_Utils_eq(proof.de, record.d) && (_Utils_eq(proof.dh, expected.dd) && ((!_Utils_eq(record.d, binding)) && (A2($author$project$Binding$sameLifetime, record.K.A.dY, binding) && (_Utils_eq(observation.bN, expected.bN) && (_Utils_eq(observation.bV, expected.bV) && (_Utils_eq(observation.az, expected.az) && (_Utils_eq(observation.aE, expected.aE) && (A2($author$project$ReconciliationFrame$contextMatches, binding, observation.az) && (A2($author$project$ReconciliationFrame$contextMatches, binding, observation.aE) && _Utils_eq(observation.az.m, observation.aE.m)))))))))))));
				return (expectedValid && correlated) ? $elm$core$Result$Ok(
					A3($author$project$ReconciliationFrame$ReservationReleased, binding, record, release)) : $elm$core$Result$Err('Uncorrelated retirement or current observation');
			},
			A2(
				$elm$core$Result$mapError,
				$elm$json$Json$Decode$errorToString,
				A2($elm$json$Json$Decode$decodeValue, decoder, raw)));
	});
var $author$project$ReconciliationTracking$same = F2(
	function (a, b) {
		return _Utils_eq(a.d, b.d) && (_Utils_eq(a.K, b.K) && _Utils_eq(a.Y, b.Y));
	});
var $author$project$ReconciliationTracking$release = F3(
	function (current, raw, model) {
		return A2(
			$elm$core$Result$andThen,
			function (record) {
				if (A2(
					$elm$core$List$any,
					function (entry) {
						return _Utils_eq(entry.K, record.K) && _Utils_eq(entry.b_, record.Y);
					},
					model.aW)) {
					return $elm$core$Result$Err('Legacy origin remains unsupported');
				} else {
					var _v0 = $elm$core$List$head(
						A2(
							$elm$core$List$filter,
							function (slot) {
								return A2($author$project$ReconciliationTracking$same, slot.df, record);
							},
							model.s));
					if (_v0.$ === 1) {
						return $elm$core$Result$Err('No stored Unknown reservation');
					} else {
						var slot = _v0.a;
						var _v1 = _Utils_Tuple3(slot.dc, slot.dB, slot.ad);
						if (((!_v1.a.$) && (!_v1.b.$)) && (!_v1.c.$)) {
							var proof = _v1.a.a;
							var action = _v1.b.a;
							var geometry = _v1.c.a;
							return A2(
								$elm$core$Result$andThen,
								function (frame) {
									if (frame.$ === 1) {
										var accepted = frame.c;
										return (!_Utils_eq(accepted.dc, proof)) ? $elm$core$Result$Err('Announced proof changed') : $elm$core$Result$Ok(
											_Utils_Tuple2(
												_Utils_update(
													model,
													{
														aH: _Utils_eq(
															model.aH,
															$elm$core$Maybe$Just(proof)) ? $elm$core$Maybe$Nothing : model.aH,
														s: A2(
															$elm$core$List$map,
															function (entry) {
																return A2($author$project$ReconciliationTracking$same, entry.df, record) ? _Utils_update(
																	entry,
																	{b1: true}) : entry;
															},
															model.s)
													}),
												record));
									} else {
										return $elm$core$Result$Err('Expected released frame');
									}
								},
								A2(
									$author$project$ReconciliationFrame$decodeReleased,
									{az: action.A, bN: action.o, bU: current, aE: geometry.A, bV: geometry.o, dd: proof.dh, df: slot.df},
									raw));
						} else {
							return $elm$core$Result$Err('Proof and both accepted observations required');
						}
					}
				}
			},
			A2(
				$elm$core$Result$mapError,
				$elm$json$Json$Decode$errorToString,
				A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'record', $author$project$ReconciliationFrame$recordDecoder),
					raw)));
	});
var $author$project$ReceiptRouter$forgetReservation = F2(
	function (local, _v0) {
		var entries = _v0;
		return A2(
			$elm$core$List$filter,
			function (entry) {
				return !_Utils_eq(entry.by, local);
			},
			entries);
	});
var $author$project$Menu$releaseUnknown = F3(
	function (local, bound, model) {
		var state = model;
		var _v0 = $elm$core$List$head(
			A2(
				$elm$core$List$filter,
				function (entry) {
					return _Utils_eq(entry.bu, local) && (_Utils_eq(entry.d, bound) && entry.aQ);
				},
				state.d3));
		if (_v0.$ === 1) {
			return _Utils_Tuple2(model, false);
		} else {
			var entry = _v0.a;
			return (_Utils_cmp(
				$elm$core$List$length(state.a0),
				$author$project$Menu$maxOutstanding) > -1) ? _Utils_Tuple2(model, false) : _Utils_Tuple2(
				_Utils_update(
					state,
					{
						d3: A2(
							$elm$core$List$filter,
							function (current) {
								return !_Utils_eq(current.bu, local);
							},
							state.d3),
						a0: A2($elm$core$List$cons, entry, state.a0)
					}),
				true);
		}
	});
var $author$project$MenuBridge$releaseReservationUnknown = F4(
	function (bound, protocolId, intent, model) {
		var state = model;
		var _v0 = A4($author$project$ReceiptRouter$findReservation, bound, protocolId, intent, state.V);
		if (_v0.$ === 1) {
			return model;
		} else {
			var _v1 = _v0.a;
			var local = _v1.a;
			var original = _v1.b;
			var _v2 = A3($author$project$Menu$releaseUnknown, local, original, state.aq);
			var menu = _v2.a;
			var accepted = _v2.b;
			return accepted ? _Utils_update(
				state,
				{
					aq: menu,
					V: A2($author$project$ReceiptRouter$forgetReservation, local, state.V)
				}) : model;
		}
	});
var $author$project$ReconciliationTracking$requested = F3(
	function (kind, request, model) {
		return _Utils_update(
			model,
			{
				s: A2(
					$elm$core$List$map,
					function (slot) {
						return _Utils_eq(slot.dc, $elm$core$Maybe$Nothing) ? slot : ((kind === 'projection-request') ? _Utils_update(
							slot,
							{
								a3: $elm$core$Maybe$Just(request)
							}) : ((kind === 'geometry-facts-request') ? _Utils_update(
							slot,
							{
								aF: $elm$core$Maybe$Just(request)
							}) : slot));
					},
					model.s)
			});
	});
var $author$project$ReconciliationTracking$reset = function (model) {
	return _Utils_update(
		model,
		{
			aH: $elm$core$Maybe$Nothing,
			s: A2(
				$elm$core$List$map,
				function (slot) {
					return _Utils_update(
						slot,
						{dB: $elm$core$Maybe$Nothing, a3: $elm$core$Maybe$Nothing, ad: $elm$core$Maybe$Nothing, aF: $elm$core$Maybe$Nothing, dc: $elm$core$Maybe$Nothing});
				},
				model.s)
		});
};
var $author$project$ReconciliationFrame$ReservationUnknown = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$ReconciliationFrame$decodeUnknown = F2(
	function (current, raw) {
		var decoder = A2(
			$author$project$ReconciliationFrame$strict,
			_List_fromArray(
				['protocolVersion', 'kind', 'binding', 'record']),
			A5(
				$elm$json$Json$Decode$map4,
				F4(
					function (_v1, _v2, binding, record) {
						return _Utils_Tuple2(binding, record);
					}),
				A2(
					$elm$json$Json$Decode$field,
					'protocolVersion',
					$author$project$ReconciliationFrame$exactInt(3)),
				A2(
					$elm$json$Json$Decode$field,
					'kind',
					$author$project$ReconciliationFrame$exactString('host-reservation-unknown')),
				A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
				A2($elm$json$Json$Decode$field, 'record', $author$project$ReconciliationFrame$recordDecoder)));
		return A2(
			$elm$core$Result$andThen,
			function (_v0) {
				var binding = _v0.a;
				var record = _v0.b;
				return _Utils_eq(binding, current) ? $elm$core$Result$Ok(
					A2($author$project$ReconciliationFrame$ReservationUnknown, binding, record)) : $elm$core$Result$Err('Foreign current binding');
			},
			A2(
				$elm$core$Result$mapError,
				$elm$json$Json$Decode$errorToString,
				A2($elm$json$Json$Decode$decodeValue, decoder, raw)));
	});
var $author$project$ReconciliationTracking$unknown = F3(
	function (current, raw, model) {
		return A2(
			$elm$core$Result$andThen,
			function (frame) {
				if (!frame.$) {
					var record = frame.b;
					var _v1 = $elm$core$List$head(
						A2(
							$elm$core$List$filter,
							function (slot) {
								return A2($author$project$ReconciliationTracking$same, slot.df, record);
							},
							model.s));
					if (!_v1.$) {
						var slot = _v1.a;
						return slot.b1 ? $elm$core$Result$Err('Historical reservation already released') : $elm$core$Result$Ok(
							_Utils_Tuple2(model, record));
					} else {
						return ($elm$core$List$length(model.s) >= 64) ? $elm$core$Result$Err('Historical reservation capacity') : $elm$core$Result$Ok(
							_Utils_Tuple2(
								_Utils_update(
									model,
									{
										s: A2(
											$elm$core$List$cons,
											{dB: $elm$core$Maybe$Nothing, a3: $elm$core$Maybe$Nothing, ad: $elm$core$Maybe$Nothing, aF: $elm$core$Maybe$Nothing, dc: $elm$core$Maybe$Nothing, df: record, b1: false},
											model.s)
									}),
								record));
					}
				} else {
					return $elm$core$Result$Err('Expected Unknown');
				}
			},
			A2($author$project$ReconciliationFrame$decodeUnknown, current, raw));
	});
var $author$project$SurfaceController$apply = F2(
	function (message, current) {
		var model = current;
		var register = F2(
			function (effects, recovery) {
				return A3(
					$elm$core$List$foldl,
					F2(
						function (effect, state) {
							if (((!effect.$) && (!effect.a.$)) && (!effect.a.a.$)) {
								var wire = effect.a.a.a;
								var _v21 = A2(
									$elm$json$Json$Decode$decodeValue,
									A3(
										$elm$json$Json$Decode$map2,
										$elm$core$Tuple$pair,
										A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder)),
									wire);
								if (!_v21.$) {
									var _v22 = _v21.a;
									var kind = _v22.a;
									var request = _v22.b;
									return A3($author$project$ReconciliationTracking$requested, kind, request, state);
								} else {
									return state;
								}
							} else {
								return state;
							}
						}),
					recovery,
					effects);
			});
		var publishDesktop = F2(
			function (recovery, next) {
				if (_Utils_eq(next, model.c)) {
					return _Utils_Tuple2(
						_Utils_update(
							model,
							{P: recovery}),
						_List_Nil);
				} else {
					var _v19 = $author$project$UInt64$next(model.bC);
					if (_v19.$ === 1) {
						return _Utils_Tuple2(
							_Utils_update(
								model,
								{Z: true}),
							_List_Nil);
					} else {
						var publication = _v19.a;
						var updated = _Utils_update(
							model,
							{c: next, bC: publication, P: recovery});
						return _Utils_Tuple2(
							updated,
							_List_fromArray(
								[
									$author$project$SurfaceController$Publish(
									$author$project$SurfaceController$frame(updated))
								]));
					}
				}
			});
		var incoming = function () {
			_v18$2:
			while (true) {
				switch (message.$) {
					case 9:
						var raw = message.a;
						return $elm$core$Maybe$Just(raw);
					case 0:
						if ((!message.a.$) && (message.a.a.$ === 3)) {
							var raw = message.a.a.a;
							return $elm$core$Maybe$Just(raw);
						} else {
							break _v18$2;
						}
					default:
						break _v18$2;
				}
			}
			return $elm$core$Maybe$Nothing;
		}();
		var ordinary = F2(
			function (prepared, action) {
				var _v12 = A2($author$project$SurfaceController$applyOrdinary, action, prepared);
				var next = _v12.a;
				var effects = _v12.b;
				var hasReads = A2(
					$elm$core$List$any,
					function (effect) {
						if (((!effect.$) && (!effect.a.$)) && (!effect.a.a.$)) {
							var wire = effect.a.a.a;
							return A2(
								$elm$core$Result$withDefault,
								false,
								A2(
									$elm$core$Result$map,
									function (kind) {
										return A2(
											$elm$core$List$member,
											kind,
											_List_fromArray(
												['projection-request', 'geometry-facts-request']));
									},
									A2(
										$elm$json$Json$Decode$decodeValue,
										A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
										wire)));
						} else {
							return false;
						}
					},
					effects);
				var _v13 = next;
				var result = _v13;
				var recovery = function () {
					if (!incoming.$) {
						var raw = incoming.a;
						return A3(
							$author$project$ReconciliationTracking$legacy,
							raw,
							result.c.a.b,
							A4($author$project$ReconciliationTracking$observed, raw, model.c.a.b, result.c.a.b, result.P));
					} else {
						return result.P;
					}
				}();
				var reset = ((!_Utils_eq(model.c.a.b.d, result.c.a.b.d)) || (!result.c.a.b.G)) ? $author$project$ReconciliationTracking$reset(recovery) : recovery;
				var proofs = A3(
					$elm$core$List$foldl,
					F2(
						function (proof, values) {
							return A2($elm$core$List$member, proof, values) ? values : A2($elm$core$List$cons, proof, values);
						}),
					_List_Nil,
					_Utils_ap(
						A2(
							$elm$core$List$filterMap,
							function ($) {
								return $.dc;
							},
							A2(
								$elm$core$List$filter,
								function (slot) {
									return !slot.b1;
								},
								reset.s)),
						A2(
							$elm$core$Maybe$withDefault,
							_List_Nil,
							A2($elm$core$Maybe$map, $elm$core$List$singleton, reset.aH))));
				var readyEffects = hasReads ? A2(
					$elm$core$List$map,
					function (proof) {
						return $author$project$SurfaceController$DesktopEffect(
							$author$project$Desktop$Send(
								$elm$json$Json$Encode$object(
									_List_fromArray(
										[
											_Utils_Tuple2(
											'protocolVersion',
											$elm$json$Json$Encode$int(3)),
											_Utils_Tuple2(
											'kind',
											$elm$json$Json$Encode$string('reconciliation-ready')),
											_Utils_Tuple2(
											'binding',
											$author$project$Binding$encode(proof.d)),
											_Utils_Tuple2(
											'proofRequestId',
											$elm$json$Json$Encode$string(
												$author$project$UInt64$string(proof.dh))),
											_Utils_Tuple2(
											'queriedBinding',
											$author$project$Binding$encode(proof.de))
										]))));
					},
					proofs) : _List_Nil;
				var emitted = _Utils_ap(readyEffects, effects);
				if ((!_Utils_eq(result.c, model.c)) && (!A2(
					$elm$core$List$any,
					function (effect) {
						if (effect.$ === 1) {
							return true;
						} else {
							return false;
						}
					},
					effects))) {
					var _v15 = $author$project$UInt64$next(result.bC);
					if (!_v15.$) {
						var publication = _v15.a;
						var updated = _Utils_update(
							result,
							{
								bC: publication,
								P: A2(register, emitted, reset)
							});
						return _Utils_Tuple2(
							updated,
							A2(
								$elm$core$List$cons,
								$author$project$SurfaceController$Publish(
									$author$project$SurfaceController$frame(updated)),
								emitted));
					} else {
						return _Utils_Tuple2(
							_Utils_update(
								result,
								{Z: true}),
							_List_Nil);
					}
				} else {
					return _Utils_Tuple2(
						_Utils_update(
							result,
							{
								P: A2(register, emitted, reset)
							}),
						emitted);
				}
			});
		var clearChoices = function (application) {
			var windows = application.a;
			var shell = windows.b;
			return _Utils_update(
				application,
				{
					j: $elm$core$Maybe$Nothing,
					F: $elm$core$Maybe$Nothing,
					t: false,
					ag: $elm$core$Maybe$Nothing,
					r: $elm$core$Maybe$Nothing,
					e: A2(
						$author$project$Switcher$cancel,
						$author$project$Switcher$generation(application.e),
						application.e),
					ai: $elm$core$Maybe$Nothing,
					aj: $elm$core$Maybe$Nothing,
					a: _Utils_update(
						windows,
						{
							k: $author$project$MenuBridge$retireChoices(windows.k),
							J: $elm$core$Maybe$Nothing,
							b: _Utils_update(
								shell,
								{cH: false})
						})
				});
		};
		if (incoming.$ === 1) {
			return A2(ordinary, current, message);
		} else {
			var raw = incoming.a;
			var _v1 = _Utils_Tuple2(
				A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
					raw),
				model.c.a.b.d);
			_v1$3:
			while (true) {
				if ((!_v1.a.$) && (!_v1.b.$)) {
					switch (_v1.a.a) {
						case 'host-reservation-unknown':
							var currentBinding = _v1.b.a;
							if ((!model.c.a.b.G) || (model.c.a.b.G === 3)) {
								return _Utils_Tuple2(current, _List_Nil);
							} else {
								var _v2 = A3($author$project$ReconciliationTracking$unknown, currentBinding, raw, model.P);
								if (_v2.$ === 1) {
									if (_v2.a === 'Historical reservation capacity') {
										return A2(
											ordinary,
											current,
											$author$project$Desktop$Window(
												$author$project$TaskbarShell$Native($author$project$Shell$ReconciliationFull)));
									} else {
										return _Utils_Tuple2(current, _List_Nil);
									}
								} else {
									var _v3 = _v2.a;
									var recovery = _v3.a;
									var record = _v3.b;
									var _v4 = A2(
										$author$project$Desktop$update,
										$author$project$Desktop$Window(
											$author$project$TaskbarShell$Native(
												A2($author$project$Shell$RecoveredUnknown, record.Y, record.K))),
										model.c);
									var admitted = _v4.a;
									var windows = admitted.a;
									var menus = A4($author$project$MenuBridge$observeReservationUnknown, record.d, record.Y, record.K, windows.k);
									var tracked = A2(
										$elm$core$List$any,
										function (entry) {
											return _Utils_eq(entry.K, record.K) && (_Utils_eq(entry.Y, record.Y) && (entry.cx === 4));
										},
										windows.b.R.l);
									return (!tracked) ? _Utils_Tuple2(current, _List_Nil) : A2(
										publishDesktop,
										recovery,
										_Utils_update(
											admitted,
											{
												a: _Utils_update(
													windows,
													{k: menus})
											}));
								}
							}
						case 'binding-retirement':
							var currentBinding = _v1.b.a;
							if ((!model.c.a.b.G) || (model.c.a.b.G === 3)) {
								return _Utils_Tuple2(current, _List_Nil);
							} else {
								var _v5 = A3($author$project$ReconciliationTracking$announce, currentBinding, raw, model.P);
								if (_v5.$ === 1) {
									return _Utils_Tuple2(current, _List_Nil);
								} else {
									var recovery = _v5.a;
									var _v6 = A2($elm$json$Json$Decode$decodeValue, $author$project$ReconciliationFrame$proofDecoder, raw);
									if (_v6.$ === 1) {
										return _Utils_Tuple2(current, _List_Nil);
									} else {
										var proof = _v6.a;
										var ready = $elm$json$Json$Encode$object(
											_List_fromArray(
												[
													_Utils_Tuple2(
													'protocolVersion',
													$elm$json$Json$Encode$int(3)),
													_Utils_Tuple2(
													'kind',
													$elm$json$Json$Encode$string('reconciliation-ready')),
													_Utils_Tuple2(
													'binding',
													$author$project$Binding$encode(currentBinding)),
													_Utils_Tuple2(
													'proofRequestId',
													$elm$json$Json$Encode$string(
														$author$project$UInt64$string(proof.dh))),
													_Utils_Tuple2(
													'queriedBinding',
													$author$project$Binding$encode(proof.de))
												]));
										var _v7 = A2(
											ordinary,
											_Utils_update(
												model,
												{
													c: clearChoices(model.c),
													P: recovery
												}),
											$author$project$Desktop$Window(
												$author$project$TaskbarShell$Native($author$project$Shell$Refresh)));
										var next = _v7.a;
										var effects = _v7.b;
										return A2(
											$elm$core$List$any,
											function (effect) {
												if ((!effect.$) && (effect.a.$ === 1)) {
													var wire = effect.a.a;
													return _Utils_eq(
														A2(
															$elm$json$Json$Decode$decodeValue,
															A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
															wire),
														$elm$core$Result$Ok('reconciliation-ready'));
												} else {
													return false;
												}
											},
											effects) ? _Utils_Tuple2(next, effects) : _Utils_Tuple2(
											next,
											A2(
												$elm$core$List$cons,
												$author$project$SurfaceController$DesktopEffect(
													$author$project$Desktop$Send(ready)),
												effects));
									}
								}
							}
						case 'host-reservation-released':
							var currentBinding = _v1.b.a;
							if ((!model.c.a.b.G) || (model.c.a.b.G === 3)) {
								return _Utils_Tuple2(current, _List_Nil);
							} else {
								var _v9 = A3($author$project$ReconciliationTracking$release, currentBinding, raw, model.P);
								if (_v9.$ === 1) {
									return _Utils_Tuple2(current, _List_Nil);
								} else {
									var _v10 = _v9.a;
									var recovery = _v10.a;
									var record = _v10.b;
									if (!A2(
										$elm$core$List$any,
										function (entry) {
											return (entry.cx === 4) && (_Utils_eq(entry.Y, record.Y) && _Utils_eq(entry.K, record.K));
										},
										model.c.a.b.R.l)) {
										return _Utils_Tuple2(
											_Utils_update(
												model,
												{P: recovery}),
											_List_Nil);
									} else {
										var preserveShared = A2(
											$elm$core$List$any,
											function (slot) {
												return (!slot.b1) && (_Utils_eq(slot.df.K, record.K) && _Utils_eq(slot.df.Y, record.Y));
											},
											recovery.s);
										var cleared = clearChoices(model.c);
										var windows = cleared.a;
										var menus = A4($author$project$MenuBridge$releaseReservationUnknown, record.d, record.Y, record.K, windows.k);
										var _v11 = A2(
											$author$project$Desktop$update,
											$author$project$Desktop$Window(
												$author$project$TaskbarShell$Native(
													A4($author$project$Shell$ReservationReleased, preserveShared, record.d, record.Y, record.K))),
											_Utils_update(
												cleared,
												{
													a: _Utils_update(
														windows,
														{k: menus})
												}));
										var released = _v11.a;
										return A2(publishDesktop, recovery, released);
									}
								}
							}
						default:
							break _v1$3;
					}
				} else {
					break _v1$3;
				}
			}
			return A2(ordinary, current, message);
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
						return {bX: identity, cX: kind, cu: role, dl: scoped, dn: shown, ds: version};
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
			return ((event.ds !== 2) || ((event.cX !== 'surface-action') || ((!_Utils_eq(event.dn, publication)) || (!_Utils_eq(event.dl, lease))))) ? $elm$core$Maybe$Nothing : A2(
				$elm$core$Maybe$andThen,
				function ($) {
					return $.g;
				},
				$elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (control) {
							return _Utils_eq(control.bu, event.bX) && control.dL;
						},
						(event.cu === 'bar') ? $author$project$Surface$barControls(model) : ((event.cu === 'popup') ? $author$project$Surface$controls(model) : _List_Nil))));
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
				function (_v5) {
					var valid = _v5.a;
					var role = _v5.b;
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
		var query = A2(
			strict,
			_List_fromArray(
				['surfaceProtocol', 'kind', 'surface', 'publication', 'lease', 'id', 'query']),
			scopes(
				function (role) {
					return ((role === 'popup') && model.q) ? A3(
						$elm$json$Json$Decode$map2,
						$elm$core$Tuple$pair,
						A2($elm$json$Json$Decode$field, 'id', $elm$json$Json$Decode$string),
						A2($elm$json$Json$Decode$field, 'query', $elm$json$Json$Decode$string)) : $elm$json$Json$Decode$fail('No applications');
				}));
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
								$author$project$Menu$Dismiss(menu.bu));
						case 'Close':
							return send(
								$author$project$Menu$Dismiss(menu.bu));
						case 'ArrowUp':
							return send(
								A2($author$project$Menu$Navigate, menu.bu, 0));
						case 'ArrowDown':
							return send(
								A2($author$project$Menu$Navigate, menu.bu, 1));
						case 'Home':
							return send(
								A2($author$project$Menu$Navigate, menu.bu, 2));
						case 'End':
							return send(
								A2($author$project$Menu$Navigate, menu.bu, 3));
						case 'Enter':
							return ($author$project$Shell$available(model.a.b) && (_Utils_eq(menu.cx, $author$project$Menu$Ready) && (!$author$project$Surface$menuBlocked(model)))) ? A2(
								$elm$core$Maybe$map,
								function (index) {
									return $author$project$Desktop$Window(
										$author$project$TaskbarShell$MenuEvent(
											A3($author$project$Menu$Activate, menu.bu, menu.d, index)));
								},
								menu.eb) : $elm$core$Maybe$Nothing;
						default:
							return $elm$core$Maybe$Nothing;
					}
				},
				$author$project$MenuBridge$menuSnapshot(model.a.k).aq);
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
		_v0$4:
		while (true) {
			if (!_v0.$) {
				switch (_v0.a) {
					case 'surface-action':
						return A4($author$project$Surface$resolveAction, publication, lease, raw, model);
					case 'surface-query':
						return A2(
							$elm$core$Maybe$andThen,
							function (_v1) {
								var identity = _v1.a;
								var value = _v1.b;
								return (identity !== 'control:search') ? $elm$core$Maybe$Nothing : A2(
									$elm$core$Maybe$map,
									function (stamp) {
										return A2($author$project$Desktop$SearchQuery, stamp, value);
									},
									$author$project$Desktop$capture(model));
							},
							$elm$core$Result$toMaybe(
								A2($elm$json$Json$Decode$decodeValue, query, raw)));
					case 'surface-menu-navigation':
						return A2(
							$elm$core$Maybe$andThen,
							menuMessage,
							$elm$core$Result$toMaybe(
								A2($elm$json$Json$Decode$decodeValue, navigation, raw)));
					case 'surface-context':
						return A2(
							$elm$core$Maybe$andThen,
							function (_v2) {
								var role = _v2.a;
								var identity = _v2.b;
								var trigger = _v2.c;
								return ((!A2(
									$elm$core$List$member,
									trigger,
									_List_fromArray(
										['pointer', 'keyboard']))) || (!_Utils_eq(model.j, $elm$core$Maybe$Nothing))) ? $elm$core$Maybe$Nothing : A2(
									$elm$core$Maybe$andThen,
									function (stamp) {
										if (role === 'bar') {
											var group = function () {
												if (A2($elm$core$String$startsWith, 'bar:pin:', identity)) {
													var pin = A2($elm$core$String$dropLeft, 8, identity);
													return A2(
														$elm$core$List$member,
														pin,
														$author$project$Desktop$pinIdentities(model)) ? A2($author$project$Desktop$pinnedGroup, pin, model) : $elm$core$Maybe$Nothing;
												} else {
													return $elm$core$List$head(
														A2(
															$elm$core$List$filter,
															function (candidate) {
																return _Utils_eq('bar:group:' + candidate.ap, identity);
															},
															$author$project$TaskbarShell$groups(model.a)));
												}
											}();
											var enabled = A2(
												$elm$core$List$any,
												function (control) {
													return _Utils_eq(control.bu, identity) && control.dL;
												},
												$author$project$Surface$barControls(model));
											return A2(
												$elm$core$Maybe$andThen,
												function (current) {
													var _v3 = current.am;
													if (_v3.b && (!_v3.b.b)) {
														var family = _v3.a;
														return family.ca ? $elm$core$Maybe$Just(
															A2($author$project$Desktop$OpenWindowMenu, stamp, family.v)) : $elm$core$Maybe$Nothing;
													} else {
														return _Utils_eq(
															A2($author$project$Taskbar$primary, false, current.am),
															$author$project$Taskbar$Picker) ? $elm$core$Maybe$Just(
															$author$project$Desktop$Window(
																A2($author$project$TaskbarShell$Primary, stamp, current.ap))) : $elm$core$Maybe$Nothing;
													}
												},
												enabled ? group : $elm$core$Maybe$Nothing);
										} else {
											if ((role === 'popup') && ($author$project$Surface$mode(model) === 'picker')) {
												return A2(
													$elm$core$Maybe$andThen,
													function (picker) {
														return (!_Utils_eq(picker.b3, stamp)) ? $elm$core$Maybe$Nothing : A2(
															$elm$core$Maybe$map,
															function (family) {
																return A2($author$project$Desktop$OpenWindowMenu, stamp, family.v);
															},
															$elm$core$List$head(
																A2(
																	$elm$core$List$filter,
																	function (family) {
																		return _Utils_eq(
																			'family:' + $author$project$UInt64$string(family.v),
																			identity) && family.ca;
																	},
																	A2(
																		$elm$core$List$concatMap,
																		function ($) {
																			return $.am;
																		},
																		A2(
																			$elm$core$List$filter,
																			function (group) {
																				return _Utils_eq(group.ap, picker.ap);
																			},
																			$author$project$TaskbarShell$groups(model.a))))));
													},
													model.a.J);
											} else {
												return $elm$core$Maybe$Nothing;
											}
										}
									},
									$author$project$Shell$capture(model.a.b));
							},
							$elm$core$Result$toMaybe(
								A2($elm$json$Json$Decode$decodeValue, context, raw)));
					default:
						break _v0$4;
				}
			} else {
				break _v0$4;
			}
		}
		return $elm$core$Maybe$Nothing;
	});
var $author$project$SurfaceController$update = F2(
	function (event, current) {
		var model = current;
		if (model.Z) {
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
							A4($author$project$Surface$resolve, model.bC, model.aI, raw, model.c)));
				case 4:
					if ($author$project$Surface$mode(model.c) === 'closed') {
						return _Utils_Tuple2(current, _List_Nil);
					} else {
						var _v1 = _Utils_Tuple2(
							$author$project$UInt64$next(model.aI),
							$author$project$UInt64$next(model.bC));
						if ((!_v1.a.$) && (!_v1.b.$)) {
							var token = _v1.a.a;
							var shown = _v1.b.a;
							var result = _Utils_update(
								model,
								{aI: token, bC: shown});
							return _Utils_Tuple2(
								result,
								_List_fromArray(
									[
										$author$project$SurfaceController$Publish(
										$author$project$SurfaceController$frame(result))
									]));
						} else {
							return _Utils_Tuple2(
								_Utils_update(
									model,
									{Z: true}),
								_List_Nil);
						}
					}
				case 3:
					var lease = event.a;
					if ((!_Utils_eq(lease, model.aI)) || ($author$project$Surface$mode(model.c) === 'closed')) {
						return _Utils_Tuple2(current, _List_Nil);
					} else {
						if (!_Utils_eq(model.c.w, $elm$core$Maybe$Nothing)) {
							return A2($author$project$SurfaceController$apply, $author$project$Desktop$InvalidateSnap, current);
						} else {
							var _v2 = _Utils_Tuple2(
								$author$project$UInt64$next(model.aI),
								$author$project$UInt64$next(model.bC));
							if ((!_v2.a.$) && (!_v2.b.$)) {
								var token = _v2.a.a;
								var shown = _v2.b.a;
								var result = _Utils_update(
									model,
									{aI: token, bC: shown});
								return _Utils_Tuple2(
									result,
									_List_fromArray(
										[
											$author$project$SurfaceController$Publish(
											$author$project$SurfaceController$frame(result))
										]));
							} else {
								return _Utils_Tuple2(
									_Utils_update(
										model,
										{Z: true}),
									_List_Nil);
							}
						}
					}
				default:
					var lease = event.a;
					return ((!_Utils_eq(lease, model.aI)) || ($author$project$Surface$mode(model.c) === 'closed')) ? _Utils_Tuple2(current, _List_Nil) : ((!_Utils_eq(model.c.w, $elm$core$Maybe$Nothing)) ? A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (stamp) {
								return A2(
									$author$project$SurfaceController$apply,
									$author$project$Desktop$CloseSnap(stamp),
									current);
							},
							$author$project$Desktop$capture(model.c))) : (($author$project$Surface$mode(model.c) === 'menu') ? A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (menu) {
								return A2(
									$author$project$SurfaceController$apply,
									$author$project$Desktop$Window(
										$author$project$TaskbarShell$MenuEvent(
											$author$project$Menu$Dismiss(menu.bu))),
									current);
							},
							$author$project$MenuBridge$menuSnapshot(model.c.a.k).aq)) : ($author$project$Desktop$switcherOpen(model.c) ? A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (stamp) {
								return A2(
									$author$project$SurfaceController$apply,
									$author$project$Desktop$CloseSwitcher(stamp),
									current);
							},
							$author$project$Desktop$capture(model.c))) : (model.c.t ? A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (stamp) {
								return A2(
									$author$project$SurfaceController$apply,
									$author$project$Desktop$CloseOverview(stamp),
									current);
							},
							$author$project$Desktop$capture(model.c))) : (model.c.q ? A2(
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
							$author$project$Desktop$capture(model.c))) : A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (picker) {
								return A2(
									$author$project$SurfaceController$apply,
									$author$project$Desktop$Window(
										A2($author$project$TaskbarShell$Close, picker.b3, picker.dP)),
									current);
							},
							model.c.a.J)))))));
			}
		}
	});
var $author$project$OutputController$apply = F2(
	function (event, _v0) {
		var model = _v0;
		var _v1 = A2($author$project$SurfaceController$update, event, model.bT);
		var next = _v1.a;
		var effects = _v1.b;
		var changed = !_Utils_eq(
			$author$project$SurfaceController$desktop(next).a.b.d,
			$author$project$SurfaceController$desktop(model.bT).a.b.d);
		return _Utils_Tuple2(
			_Utils_update(
				model,
				{
					ab: changed ? false : model.ab,
					W: changed ? _List_Nil : model.W,
					ac: changed ? false : model.ac,
					bT: next
				}),
			effects);
	});
var $author$project$OutputController$strict = F2(
	function (fields, decoder) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? decoder : $elm$json$Json$Decode$fail('Output view fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$OutputController$catalogRequest = function (raw) {
	var decoder = A2(
		$author$project$OutputController$strict,
		_List_fromArray(
			['protocolVersion', 'kind', 'binding', 'requestId']),
		A5(
			$elm$json$Json$Decode$map4,
			F4(
				function (version, kind, binding, request) {
					return _Utils_Tuple3(
						version,
						kind,
						{d: binding, o: request});
				}),
			A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int),
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
			A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder)));
	var _v0 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
	if (((!_v0.$) && (_v0.a.a === 3)) && (_v0.a.b === 'catalog-request')) {
		var _v1 = _v0.a;
		var request = _v1.c;
		return _Utils_eq(request.o, $author$project$UInt64$zero) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(request);
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$UnsentOperation$commandDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (fields) {
		return (!_Utils_eq(
			$elm$core$List$sort(
				A2($elm$core$List$map, $elm$core$Tuple$first, fields)),
			_List_fromArray(
				['binding', 'effectProtocol', 'intent', 'kind', 'protocolVersion']))) ? $elm$json$Json$Decode$fail('Operation command fields') : A2(
			$elm$json$Json$Decode$andThen,
			function (_v0) {
				var version = _v0.a;
				var kind = _v0.b;
				var key = _v0.c;
				return ((version !== 3) || ((kind !== 'window-effect') || ((!_Utils_eq(
					key.b_,
					$author$project$Effects$protocol(key.K.aK))) || (!A3($author$project$Binding$matchesContext, key.K.A.dY, key.K.A.dM, key.d))))) ? $elm$json$Json$Decode$fail('Operation command authority/protocol') : $elm$json$Json$Decode$succeed(key);
			},
			A6(
				$elm$json$Json$Decode$map5,
				F5(
					function (version, kind, binding, protocol, intent) {
						return _Utils_Tuple3(
							version,
							kind,
							{d: binding, K: intent, b_: protocol});
					}),
				A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int),
				A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
				A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
				A2($elm$json$Json$Decode$field, 'effectProtocol', $elm$json$Json$Decode$int),
				A2($elm$json$Json$Decode$field, 'intent', $author$project$Effects$intentDecoder)));
	},
	$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
var $author$project$SurfaceRenderer$Snapshot = $elm$core$Basics$identity;
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
		return {h: ariaLabel, f: detail, i: domId, dL: enabled, bX: identity, cZ: label};
	});
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
var $author$project$SurfaceRenderer$decode = function (raw) {
	var decoder = A2(
		$author$project$SurfaceRenderer$strict,
		_List_fromArray(
			['surfaceProtocol', 'publication', 'lease', 'mode', 'status', 'bar', 'popup']),
		A8(
			$elm$json$Json$Decode$map7,
			F7(
				function (version, shown, scoped, current, notice, bar, popup) {
					return {al: bar, bn: current, d_: notice, M: popup, dl: scoped, dn: shown, ds: version};
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
				$author$project$SurfaceRenderer$controls(292)),
			A2(
				$elm$json$Json$Decode$field,
				'popup',
				$author$project$SurfaceRenderer$controls(2150))));
	return A2(
		$elm$core$Result$andThen,
		function (record) {
			var unique = function (names) {
				return _Utils_eq(
					$elm$core$List$length(names),
					$elm$core$Set$size(
						$elm$core$Set$fromList(names)));
			};
			var all = _Utils_ap(record.al, record.M);
			var identities = A2(
				$elm$core$List$map,
				function ($) {
					return $.bX;
				},
				all);
			return ((record.ds !== 2) || (_Utils_eq(record.dn, $author$project$UInt64$zero) || ((!A2(
				$elm$core$List$member,
				record.bn,
				_List_fromArray(
					['closed', 'picker', 'applications', 'menu', 'overview', 'switcher', 'snap']))) || (((record.bn !== 'closed') && _Utils_eq(record.dl, $author$project$UInt64$zero)) || (((record.bn === 'closed') && (!$elm$core$List$isEmpty(record.M))) || ((!unique(identities)) || ((!unique(
				A2(
					$elm$core$List$map,
					function ($) {
						return $.i;
					},
					all))) || A2(
				$elm$core$List$any,
				function (control) {
					return $elm$core$String$isEmpty(control.bX) || $elm$core$String$isEmpty(control.i);
				},
				all)))))))) ? $elm$core$Result$Err('Invalid presentation scope/identities') : $elm$core$Result$Ok(
				{al: record.al, aI: record.dl, L: record.bn, M: record.M, bC: record.dn, cx: record.d_});
		},
		A2(
			$elm$core$Result$mapError,
			$elm$json$Json$Decode$errorToString,
			A2($elm$json$Json$Decode$decodeValue, decoder, raw)));
};
var $author$project$OutputController$encodeScope = function (_v0) {
	var viewId = _v0.a;
	var viewGeneration = _v0.b;
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'id',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(viewId))),
				_Utils_Tuple2(
				'generation',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(viewGeneration)))
			]));
};
var $author$project$OutputController$owner = function (_v0) {
	var model = _v0;
	return ($author$project$Surface$mode(
		$author$project$SurfaceController$desktop(model.bT)) === 'closed') ? $elm$core$Maybe$Nothing : model.eb;
};
var $author$project$OutputController$frame = function (current) {
	var model = current;
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'viewProtocol',
				$elm$json$Json$Encode$int(1)),
				_Utils_Tuple2(
				'kind',
				$elm$json$Json$Encode$string('view-frame')),
				_Utils_Tuple2(
				'revision',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(model.dj))),
				_Utils_Tuple2(
				'views',
				A2($elm$json$Json$Encode$list, $author$project$OutputController$encodeScope, model.av)),
				_Utils_Tuple2(
				'focusOwner',
				A2(
					$elm$core$Maybe$withDefault,
					$elm$json$Json$Encode$null,
					A2($elm$core$Maybe$map, $author$project$OutputController$encodeScope, model.eb))),
				_Utils_Tuple2(
				'popupOwner',
				A2(
					$elm$core$Maybe$withDefault,
					$elm$json$Json$Encode$null,
					A2(
						$elm$core$Maybe$map,
						$author$project$OutputController$encodeScope,
						$author$project$OutputController$owner(current)))),
				_Utils_Tuple2(
				'frame',
				$author$project$SurfaceController$frame(model.bT))
			]));
};
var $author$project$SurfaceRenderer$lease = function (_v0) {
	var snapshot = _v0;
	return snapshot.aI;
};
var $author$project$OutputController$lease = function (model) {
	return A2(
		$elm$core$Maybe$map,
		$author$project$SurfaceRenderer$lease,
		$elm$core$Result$toMaybe(
			$author$project$SurfaceRenderer$decode(
				$author$project$SurfaceController$frame(model))));
};
var $author$project$OutputController$observation = function (raw) {
	var _v0 = A2(
		$elm$json$Json$Decode$decodeValue,
		A3(
			$elm$json$Json$Decode$map2,
			$elm$core$Tuple$pair,
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder)),
		raw);
	if (!_v0.$) {
		var value = _v0.a;
		var kind = value.a;
		return A2(
			$elm$core$List$member,
			kind,
			_List_fromArray(
				['projection-request', 'geometry-attach', 'geometry-facts-request'])) ? $elm$core$Maybe$Just(value) : $elm$core$Maybe$Nothing;
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$SurfaceRenderer$publication = function (_v0) {
	var snapshot = _v0;
	return snapshot.bC;
};
var $author$project$Desktop$CatalogUnsent = F2(
	function (a, b) {
		return {$: 24, a: a, b: b};
	});
var $author$project$SurfaceController$NativeDismiss = function (a) {
	return {$: 2, a: a};
};
var $author$project$OutputController$refuseCatalogs = F3(
	function (capturedLease, requests, current) {
		var step = F2(
			function (request, _v4) {
				var state = _v4.a;
				var commands = _v4.b;
				var _v3 = A2(
					$author$project$OutputController$apply,
					$author$project$SurfaceController$Interaction(
						A2($author$project$Desktop$CatalogUnsent, request.d, request.o)),
					state);
				var next = _v3.a;
				var emitted = _v3.b;
				return _Utils_Tuple2(
					next,
					_Utils_ap(commands, emitted));
			});
		var desktop = $author$project$SurfaceController$desktop(
			$author$project$OutputController$controller(current));
		var matching = A2(
			$elm$core$List$filter,
			function (request) {
				return A3($author$project$Desktop$canProveCatalogUnsent, request.d, request.o, desktop);
			},
			requests);
		var _v0 = A3(
			$elm$core$List$foldl,
			step,
			_Utils_Tuple2(current, _List_Nil),
			matching);
		var cleared = _v0.a;
		var effects = _v0.b;
		if ($elm$core$List$isEmpty(matching) || (($author$project$Surface$mode(desktop) !== 'applications') || (!_Utils_eq(
			capturedLease,
			$author$project$OutputController$lease(
				$author$project$OutputController$controller(current)))))) {
			return _Utils_Tuple2(cleared, effects);
		} else {
			if (!capturedLease.$) {
				var token = capturedLease.a;
				var _v2 = A2(
					$author$project$OutputController$apply,
					$author$project$SurfaceController$NativeDismiss(token),
					cleared);
				var closed = _v2.a;
				var closeEffects = _v2.b;
				return _Utils_Tuple2(
					closed,
					_Utils_ap(effects, closeEffects));
			} else {
				return _Utils_Tuple2(cleared, effects);
			}
		}
	});
var $author$project$OutputController$utf8Length = function (text) {
	return A3(
		$elm$core$String$foldl,
		F2(
			function (_char, count) {
				var code = $elm$core$Char$toCode(_char);
				return count + ((code <= 127) ? 1 : ((code <= 2047) ? 2 : ((code <= 65535) ? 3 : 4)));
			}),
		0,
		text);
};
var $author$project$OutputController$register = F2(
	function (effects, current) {
		var model = current;
		var scoped = A2(
			$elm$core$Maybe$withDefault,
			A2(
				$elm$core$Maybe$withDefault,
				A2($author$project$OutputController$Scope, $author$project$UInt64$zero, $author$project$UInt64$zero),
				model.eb),
			$author$project$OutputController$owner(current));
		var requests = A2(
			$elm$core$List$filterMap,
			function (effect) {
				_v7$3:
				while (true) {
					if (!effect.$) {
						switch (effect.a.$) {
							case 1:
								var wire = effect.a.a;
								return $elm$core$Maybe$Just(wire);
							case 0:
								switch (effect.a.a.$) {
									case 0:
										var wire = effect.a.a.a;
										return $elm$core$Maybe$Just(wire);
									case 1:
										var _v8 = effect.a.a;
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
									default:
										break _v7$3;
								}
							default:
								break _v7$3;
						}
					} else {
						break _v7$3;
					}
				}
				return $elm$core$Maybe$Nothing;
			},
			effects);
		var operations = A2(
			$elm$core$List$filterMap,
			function (request) {
				return $elm$core$Result$toMaybe(
					A2($elm$json$Json$Decode$decodeValue, $author$project$UnsentOperation$commandDecoder, request));
			},
			requests);
		var observations = A2($elm$core$List$filterMap, $author$project$OutputController$observation, requests);
		var focus = A2(
			$elm$core$List$filterMap,
			function (effect) {
				if ((!effect.$) && (effect.a.$ === 4)) {
					var target = effect.a.a;
					return $elm$core$Maybe$Just(
						$elm$json$Json$Encode$string(target));
				} else {
					return $elm$core$Maybe$Nothing;
				}
			},
			effects);
		var packet = $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'viewProtocol',
					$elm$json$Json$Encode$int(1)),
					_Utils_Tuple2(
					'kind',
					$elm$json$Json$Encode$string('view-commit')),
					_Utils_Tuple2(
					'projection',
					$author$project$OutputController$frame(current)),
					_Utils_Tuple2(
					'requests',
					A2(
						$elm$json$Json$Encode$list,
						function (item) {
							return item;
						},
						requests)),
					_Utils_Tuple2(
					'focus',
					A2(
						$elm$json$Json$Encode$list,
						function (item) {
							return item;
						},
						focus))
				]));
		var text = A2($elm$json$Json$Encode$encode, 0, packet);
		var catalogs = A2($elm$core$List$filterMap, $author$project$OutputController$catalogRequest, requests);
		var binding = $author$project$SurfaceController$desktop(model.bT).a.b.d;
		var bound = A2(
			$elm$core$List$all,
			function (request) {
				return _Utils_eq(
					binding,
					$elm$core$Result$toMaybe(
						A2(
							$elm$json$Json$Decode$decodeValue,
							A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
							request)));
			},
			requests);
		if ($elm$core$List$isEmpty(effects)) {
			return _Utils_Tuple2(current, $elm$core$Maybe$Nothing);
		} else {
			if ($elm$core$List$isEmpty(requests) || ((!bound) || _Utils_eq(binding, $elm$core$Maybe$Nothing))) {
				return _Utils_Tuple2(
					current,
					$elm$core$Maybe$Just(packet));
			} else {
				if ((!A2($elm$core$List$member, scoped, model.av)) || (model.ab || (($elm$core$List$length(model.W) >= 16) || (($elm$core$List$length(requests) > 16) || (($elm$core$String$length(text) > 131072) || ($author$project$OutputController$utf8Length(text) > 131072)))))) {
					var capacity = ($elm$core$List$length(model.W) >= 16) && (A2($elm$core$List$member, scoped, model.av) && (($elm$core$List$length(requests) <= 16) && (($elm$core$String$length(text) <= 131072) && ($author$project$OutputController$utf8Length(text) <= 131072))));
					var belongs = function (slot) {
						return A2(
							$elm$core$List$member,
							_Utils_Tuple2('projection-request', slot.aJ),
							observations) || A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (id) {
									return A2(
										$elm$core$List$member,
										_Utils_Tuple2('geometry-facts-request', id),
										observations);
								},
								slot.aF));
					};
					var _v0 = A2(
						$author$project$OutputController$apply,
						$author$project$SurfaceController$Interaction(
							$author$project$Desktop$Window(
								$author$project$TaskbarShell$Native(
									A2($author$project$Shell$RegistrationRefused, operations, observations)))),
						_Utils_update(
							model,
							{
								ab: true,
								ac: model.ab ? model.ac : capacity
							}));
					var refused = _v0.a;
					var prepared = $author$project$MenuBridge$preparedSnapshot(
						$author$project$SurfaceController$desktop(
							$author$project$OutputController$controller(refused)).a.k);
					var _v1 = function () {
						if (!prepared.$) {
							var slot = prepared.a;
							return belongs(slot) ? A2(
								$author$project$OutputController$apply,
								$author$project$SurfaceController$Interaction(
									$author$project$Desktop$Window(
										$author$project$TaskbarShell$CancelPrepared(slot.bh))),
								refused) : _Utils_Tuple2(refused, _List_Nil);
						} else {
							return _Utils_Tuple2(refused, _List_Nil);
						}
					}();
					var settled = _v1.a;
					var _v3 = A3(
						$author$project$OutputController$refuseCatalogs,
						$author$project$OutputController$lease(model.bT),
						catalogs,
						settled);
					var catalogSettled = _v3.a;
					var catalogEffects = _v3.b;
					var catalogFocus = A2(
						$elm$core$List$filterMap,
						function (effect) {
							if ((!effect.$) && (effect.a.$ === 4)) {
								var target = effect.a.a;
								return $elm$core$Maybe$Just(
									$elm$json$Json$Encode$string(target));
							} else {
								return $elm$core$Maybe$Nothing;
							}
						},
						catalogEffects);
					var presentation = $elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'viewProtocol',
								$elm$json$Json$Encode$int(1)),
								_Utils_Tuple2(
								'kind',
								$elm$json$Json$Encode$string('view-commit')),
								_Utils_Tuple2(
								'projection',
								$author$project$OutputController$frame(catalogSettled)),
								_Utils_Tuple2(
								'requests',
								A2(
									$elm$json$Json$Encode$list,
									function (value) {
										return value;
									},
									_List_Nil)),
								_Utils_Tuple2(
								'focus',
								A2(
									$elm$json$Json$Encode$list,
									function (value) {
										return value;
									},
									catalogFocus))
							]));
					return _Utils_Tuple2(
						catalogSettled,
						$elm$core$Maybe$Just(presentation));
				} else {
					var _v5 = _Utils_Tuple2(
						binding,
						$author$project$SurfaceRenderer$decode(
							$author$project$SurfaceController$frame(model.bT)));
					if ((!_v5.a.$) && (!_v5.b.$)) {
						var authority = _v5.a.a;
						var snapshot = _v5.b.a;
						var batch = {
							d: authority,
							bQ: catalogs,
							aI: $author$project$SurfaceRenderer$lease(snapshot),
							bY: observations,
							d1: operations,
							bC: $author$project$SurfaceRenderer$publication(snapshot),
							dj: model.dj,
							b3: scoped,
							bL: text
						};
						return _Utils_Tuple2(
							_Utils_update(
								model,
								{
									W: A2($elm$core$List$cons, batch, model.W)
								}),
							$elm$core$Maybe$Just(packet));
					} else {
						return _Utils_Tuple2(current, $elm$core$Maybe$Nothing);
					}
				}
			}
		}
	});
var $author$project$SurfaceController$NativeReflow = function (a) {
	return {$: 3, a: a};
};
var $author$project$SurfaceController$NativeRelocate = {$: 4};
var $author$project$Shell$RegistrationAvailable = function (a) {
	return {$: 14, a: a};
};
var $author$project$Shell$SupersedeObservations = function (a) {
	return {$: 11, a: a};
};
var $author$project$Desktop$PresentationOwner = function (a) {
	return {$: 8, a: a};
};
var $author$project$OutputController$assignOwner = F2(
	function (scope, controllerModel) {
		var registered = A2(
			$elm$core$Maybe$map,
			function (_v0) {
				var outputId = _v0.a;
				var providerId = _v0.b;
				return {cn: outputId, cr: providerId};
			},
			scope);
		return A2(
			$author$project$SurfaceController$update,
			$author$project$SurfaceController$Interaction(
				$author$project$Desktop$PresentationOwner(registered)),
			controllerModel);
	});
var $author$project$OutputController$freshRelocationPossible = function (model) {
	var _v0 = $author$project$SurfaceRenderer$decode(
		$author$project$SurfaceController$frame(model));
	if (_v0.$ === 1) {
		return false;
	} else {
		var snapshot = _v0.a;
		return (!_Utils_eq(
			$author$project$UInt64$next(
				$author$project$SurfaceRenderer$lease(snapshot)),
			$elm$core$Maybe$Nothing)) && (!_Utils_eq(
			A2(
				$elm$core$Maybe$andThen,
				$author$project$UInt64$next,
				$author$project$UInt64$next(
					$author$project$SurfaceRenderer$publication(snapshot))),
			$elm$core$Maybe$Nothing));
	}
};
var $author$project$OutputController$generation = function (_v0) {
	var value = _v0.b;
	return value;
};
var $author$project$OutputController$identity = function (_v0) {
	var value = _v0.a;
	return value;
};
var $author$project$OutputController$scopeDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (scope) {
		var viewId = scope.a;
		var viewGeneration = scope.b;
		return (_Utils_eq(viewId, $author$project$UInt64$zero) || _Utils_eq(viewGeneration, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$fail('Zero view scope') : $elm$json$Json$Decode$succeed(scope);
	},
	A2(
		$author$project$OutputController$strict,
		_List_fromArray(
			['id', 'generation']),
		A3(
			$elm$json$Json$Decode$map2,
			$author$project$OutputController$Scope,
			A2($elm$json$Json$Decode$field, 'id', $author$project$UInt64$decoder),
			A2($elm$json$Json$Decode$field, 'generation', $author$project$UInt64$decoder))));
var $author$project$OutputController$nativePopup = F3(
	function (event, raw, current) {
		var model = current;
		var decoder = A2(
			$author$project$OutputController$strict,
			_List_fromArray(
				['scope', 'lease']),
			A3(
				$elm$json$Json$Decode$map2,
				$elm$core$Tuple$pair,
				A2($elm$json$Json$Decode$field, 'scope', $author$project$OutputController$scopeDecoder),
				A2($elm$json$Json$Decode$field, 'lease', $author$project$UInt64$decoder)));
		var _v0 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
		if (!_v0.$) {
			var _v1 = _v0.a;
			var scope = _v1.a;
			var token = _v1.b;
			return (_Utils_eq(
				$author$project$OutputController$owner(current),
				$elm$core$Maybe$Just(scope)) && A2($elm$core$List$member, scope, model.av)) ? A2(
				$author$project$OutputController$apply,
				event(token),
				current) : _Utils_Tuple2(current, _List_Nil);
		} else {
			return _Utils_Tuple2(current, _List_Nil);
		}
	});
var $author$project$OutputController$observationEffect = function (effect) {
	if (((!effect.$) && (!effect.a.$)) && (!effect.a.a.$)) {
		var wire = effect.a.a.a;
		return !_Utils_eq(
			$author$project$OutputController$observation(wire),
			$elm$core$Maybe$Nothing);
	} else {
		return false;
	}
};
var $author$project$Shell$UnsentObservations = function (a) {
	return {$: 10, a: a};
};
var $author$project$Shell$UnsentOperations = function (a) {
	return {$: 12, a: a};
};
var $author$project$OutputController$receiveDisposition = F2(
	function (raw, current) {
		var model = current;
		var decoder = A2(
			$author$project$OutputController$strict,
			_List_fromArray(
				['viewProtocol', 'kind', 'disposition', 'scope', 'revision', 'publication', 'lease', 'binding', 'batch']),
			A9(
				$elm$json$Json$Decode$map8,
				F8(
					function (scope, revision, publication, token, binding, batch, disposition, header) {
						return {d: binding, bo: disposition, cS: header, aI: token, bC: publication, dj: revision, b3: scope, bL: batch};
					}),
				A2($elm$json$Json$Decode$field, 'scope', $author$project$OutputController$scopeDecoder),
				A2($elm$json$Json$Decode$field, 'revision', $author$project$UInt64$decoder),
				A2($elm$json$Json$Decode$field, 'publication', $author$project$UInt64$decoder),
				A2($elm$json$Json$Decode$field, 'lease', $author$project$UInt64$decoder),
				A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
				A2(
					$elm$json$Json$Decode$field,
					'batch',
					A2(
						$elm$json$Json$Decode$andThen,
						function (text) {
							return (($elm$core$String$length(text) <= 131072) && ($author$project$OutputController$utf8Length(text) <= 131072)) ? $elm$json$Json$Decode$succeed(text) : $elm$json$Json$Decode$fail('Batch bound');
						},
						$elm$json$Json$Decode$string)),
				A2($elm$json$Json$Decode$field, 'disposition', $elm$json$Json$Decode$string),
				A3(
					$elm$json$Json$Decode$map2,
					$elm$core$Tuple$pair,
					A2($elm$json$Json$Decode$field, 'viewProtocol', $elm$json$Json$Decode$int),
					A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string))));
		var _v0 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
		if (!_v0.$) {
			var certificate = _v0.a;
			var matches = function (batch) {
				return _Utils_eq(batch.b3, certificate.b3) && (_Utils_eq(batch.dj, certificate.dj) && (_Utils_eq(batch.bC, certificate.bC) && (_Utils_eq(batch.aI, certificate.aI) && (_Utils_eq(batch.d, certificate.d) && _Utils_eq(batch.bL, certificate.bL)))));
			};
			if ((!_Utils_eq(
				certificate.cS,
				_Utils_Tuple2(1, 'batch-disposition'))) || (!A2(
				$elm$core$List$member,
				certificate.bo,
				_List_fromArray(
					['preflight-unsent', 'admitted', 'uncertain'])))) {
				return _Utils_Tuple2(current, _List_Nil);
			} else {
				var _v1 = $elm$core$List$head(
					A2($elm$core$List$filter, matches, model.W));
				if (_v1.$ === 1) {
					return _Utils_Tuple2(current, _List_Nil);
				} else {
					var batch = _v1.a;
					var remaining = A2(
						$elm$core$List$filter,
						A2($elm$core$Basics$composeR, matches, $elm$core$Basics$not),
						model.W);
					var currentShell = $author$project$SurfaceController$desktop(model.bT).a.b;
					var catalogMatched = A2(
						$elm$core$List$any,
						function (request) {
							return A3(
								$author$project$Desktop$canProveCatalogUnsent,
								request.d,
								request.o,
								$author$project$SurfaceController$desktop(model.bT));
						},
						batch.bQ);
					var canRecover = model.ac && ($elm$core$List$length(remaining) < 16);
					var consumed = _Utils_update(
						model,
						{
							ab: canRecover ? false : model.ab,
							W: remaining,
							ac: canRecover ? false : model.ac
						});
					var _v2 = ((certificate.bo === 'preflight-unsent') && _Utils_eq(
						currentShell.d,
						$elm$core$Maybe$Just(batch.d))) ? A2(
						$author$project$OutputController$apply,
						$author$project$SurfaceController$Interaction(
							$author$project$Desktop$Window(
								$author$project$TaskbarShell$Native(
									$author$project$Shell$UnsentOperations(batch.d1)))),
						consumed) : _Utils_Tuple2(consumed, _List_Nil);
					var settled = _v2.a;
					var operationEffects = _v2.b;
					var _v3 = ((certificate.bo === 'preflight-unsent') && _Utils_eq(
						currentShell.d,
						$elm$core$Maybe$Just(batch.d))) ? A3(
						$author$project$OutputController$refuseCatalogs,
						$elm$core$Maybe$Just(batch.aI),
						batch.bQ,
						settled) : _Utils_Tuple2(settled, _List_Nil);
					var catalogSettled = _v3.a;
					var catalogEffects = _v3.b;
					var _v4 = canRecover ? A2(
						$author$project$OutputController$apply,
						$author$project$SurfaceController$Interaction(
							$author$project$Desktop$Window(
								$author$project$TaskbarShell$Native(
									$author$project$Shell$RegistrationAvailable(true)))),
						catalogSettled) : _Utils_Tuple2(catalogSettled, _List_Nil);
					var recovered = _v4.a;
					var recoveryEffects = _v4.b;
					var allEffects = _Utils_ap(
						operationEffects,
						_Utils_ap(catalogEffects, recoveryEffects));
					if ((certificate.bo !== 'preflight-unsent') || (((!A2($author$project$Shell$matchesUnsent, batch.bY, currentShell)) && (!catalogMatched)) || ((!_Utils_eq(
						currentShell.d,
						$elm$core$Maybe$Just(batch.d))) || (!_Utils_eq(
						$author$project$OutputController$lease(model.bT),
						$elm$core$Maybe$Just(batch.aI)))))) {
						return _Utils_Tuple2(recovered, allEffects);
					} else {
						var _v5 = A2(
							$author$project$OutputController$apply,
							$author$project$SurfaceController$NativeDismiss(batch.aI),
							recovered);
						var closed = _v5.a;
						var closeEffects = _v5.b;
						var prepared = $author$project$MenuBridge$preparedSnapshot(
							$author$project$SurfaceController$desktop(
								$author$project$OutputController$controller(closed)).a.k);
						var _v6 = function () {
							if (!prepared.$) {
								var selection = prepared.a;
								return A2(
									$author$project$OutputController$apply,
									$author$project$SurfaceController$Interaction(
										$author$project$Desktop$Window(
											$author$project$TaskbarShell$CancelPrepared(selection.bh))),
									closed);
							} else {
								return _Utils_Tuple2(closed, _List_Nil);
							}
						}();
						var cancelled = _v6.a;
						var cancelEffects = _v6.b;
						var _v8 = A2(
							$author$project$OutputController$apply,
							$author$project$SurfaceController$Interaction(
								$author$project$Desktop$Window(
									$author$project$TaskbarShell$Native(
										$author$project$Shell$UnsentObservations(batch.bY)))),
							cancelled);
						var fresh = _v8.a;
						var effects = _v8.b;
						return _Utils_Tuple2(
							fresh,
							_Utils_ap(
								allEffects,
								_Utils_ap(
									closeEffects,
									_Utils_ap(cancelEffects, effects))));
					}
				}
			}
		} else {
			return _Utils_Tuple2(current, _List_Nil);
		}
	});
var $author$project$OutputController$update = F2(
	function (event, current) {
		var model = current;
		switch (event.$) {
			case 0:
				var raw = event.a;
				return A2($author$project$OutputController$receiveDisposition, raw, current);
			case 3:
				var message = event.a;
				return A2(
					$author$project$OutputController$apply,
					$author$project$SurfaceController$Interaction(message),
					current);
			case 1:
				var raw = event.a;
				var decoder = A2(
					$author$project$OutputController$strict,
					_List_fromArray(
						['viewProtocol', 'kind', 'revision', 'views']),
					A5(
						$elm$json$Json$Decode$map4,
						F4(
							function (version, kind, revision, scopes) {
								return {cX: kind, dj: revision, bf: scopes, ds: version};
							}),
						A2($elm$json$Json$Decode$field, 'viewProtocol', $elm$json$Json$Decode$int),
						A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
						A2($elm$json$Json$Decode$field, 'revision', $author$project$UInt64$decoder),
						A2(
							$elm$json$Json$Decode$field,
							'views',
							$elm$json$Json$Decode$list($author$project$OutputController$scopeDecoder))));
				var admitted = function (scopes) {
					return ($elm$core$List$length(scopes) <= 64) && (_Utils_eq(
						$elm$core$List$length(
							A2($elm$core$List$map, $author$project$OutputController$identity, scopes)),
						$elm$core$List$length(
							A3(
								$elm$core$List$foldl,
								F2(
									function (scope, ids) {
										return A2(
											$elm$core$List$member,
											$author$project$OutputController$identity(scope),
											ids) ? ids : A2(
											$elm$core$List$cons,
											$author$project$OutputController$identity(scope),
											ids);
									}),
								_List_Nil,
								scopes))) && A2(
						$elm$core$List$all,
						function (scope) {
							var _v8 = $elm$core$List$head(
								A2(
									$elm$core$List$filter,
									function (prior) {
										return _Utils_eq(
											$author$project$OutputController$identity(prior),
											$author$project$OutputController$identity(scope));
									},
									model.av));
							if (!_v8.$) {
								var prior = _v8.a;
								return !(!A2(
									$author$project$UInt64$compare,
									$author$project$OutputController$generation(scope),
									$author$project$OutputController$generation(prior)));
							} else {
								return A2(
									$author$project$UInt64$compare,
									$author$project$OutputController$identity(scope),
									model.bW) === 2;
							}
						},
						scopes));
				};
				var _v1 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
				if (!_v1.$) {
					var table = _v1.a;
					if ((table.ds !== 1) || ((table.cX !== 'view-topology') || ((A2($author$project$UInt64$compare, table.dj, model.dj) !== 2) || (!admitted(table.bf))))) {
						return _Utils_Tuple2(current, _List_Nil);
					} else {
						var survives = A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (priorSelected) {
									return A2($elm$core$List$member, priorSelected, table.bf);
								},
								model.eb));
						var selected = survives ? model.eb : $elm$core$List$head(table.bf);
						var retired = (!survives) && (!_Utils_eq(
							$author$project$OutputController$owner(current),
							$elm$core$Maybe$Nothing));
						var highest = A3(
							$elm$core$List$foldl,
							F2(
								function (scope, maximum) {
									return (A2(
										$author$project$UInt64$compare,
										$author$project$OutputController$identity(scope),
										maximum) === 2) ? $author$project$OutputController$identity(scope) : maximum;
								}),
							model.bW,
							table.bf);
						var _v2 = retired ? A2(
							$elm$core$Maybe$withDefault,
							_Utils_Tuple2(model.bT, _List_Nil),
							A2(
								$elm$core$Maybe$map,
								function (token) {
									return A2(
										$author$project$SurfaceController$update,
										$author$project$SurfaceController$NativeDismiss(token),
										model.bT);
								},
								$author$project$OutputController$lease(model.bT))) : _Utils_Tuple2(model.bT, _List_Nil);
						var next = _v2.a;
						var effects = _v2.b;
						var _v3 = A2($author$project$OutputController$assignOwner, selected, next);
						var assigned = _v3.a;
						var ownerEffects = _v3.b;
						var prepared = $author$project$MenuBridge$preparedSnapshot(
							$author$project$SurfaceController$desktop(assigned).a.k);
						var _v4 = function () {
							if (!prepared.$) {
								var slot = prepared.a;
								return A2(
									$author$project$SurfaceController$update,
									$author$project$SurfaceController$Interaction(
										$author$project$Desktop$Window(
											$author$project$TaskbarShell$CancelPrepared(slot.bh))),
									assigned);
							} else {
								return _Utils_Tuple2(assigned, _List_Nil);
							}
						}();
						var cancelled = _v4.a;
						var cancelEffects = _v4.b;
						var prior = A2(
							$elm$core$List$filter,
							A2($elm$core$Basics$composeL, $elm$core$Basics$not, $author$project$OutputController$observationEffect),
							_Utils_ap(
								effects,
								_Utils_ap(ownerEffects, cancelEffects)));
						var _v6 = model.ac ? _Utils_Tuple2(cancelled, _List_Nil) : A2(
							$author$project$SurfaceController$update,
							$author$project$SurfaceController$Interaction(
								$author$project$Desktop$Window(
									$author$project$TaskbarShell$Native(
										$author$project$Shell$RegistrationAvailable(false)))),
							cancelled);
						var unblocked = _v6.a;
						var _v7 = A2(
							$author$project$SurfaceController$update,
							$author$project$SurfaceController$Interaction(
								$author$project$Desktop$Window(
									$author$project$TaskbarShell$Native(
										$author$project$Shell$SupersedeObservations(
											!_Utils_eq(selected, $elm$core$Maybe$Nothing))))),
							unblocked);
						var refreshed = _v7.a;
						var readEffects = _v7.b;
						var result = _Utils_update(
							model,
							{
								ab: model.ac ? model.ab : false,
								bT: refreshed,
								bW: highest,
								dj: table.dj,
								eb: selected,
								av: table.bf
							});
						return _Utils_Tuple2(
							result,
							A2(
								$elm$core$List$cons,
								$author$project$SurfaceController$Publish(
									$author$project$SurfaceController$frame(refreshed)),
								_Utils_ap(prior, readEffects)));
					}
				} else {
					return _Utils_Tuple2(current, _List_Nil);
				}
			case 2:
				var raw = event.a;
				var decoder = A2(
					$author$project$OutputController$strict,
					_List_fromArray(
						['viewProtocol', 'kind', 'scope', 'action']),
					A5(
						$elm$json$Json$Decode$map4,
						F4(
							function (version, kind, scope, action) {
								return {dB: action, cX: kind, b3: scope, ds: version};
							}),
						A2($elm$json$Json$Decode$field, 'viewProtocol', $elm$json$Json$Decode$int),
						A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
						A2($elm$json$Json$Decode$field, 'scope', $author$project$OutputController$scopeDecoder),
						A2($elm$json$Json$Decode$field, 'action', $elm$json$Json$Decode$value)));
				var _v9 = _Utils_Tuple2(
					A2($elm$json$Json$Decode$decodeValue, decoder, raw),
					$author$project$SurfaceRenderer$decode(
						$author$project$SurfaceController$frame(model.bT)));
				if ((!_v9.a.$) && (!_v9.b.$)) {
					var callback = _v9.a.a;
					var snapshot = _v9.b.a;
					if ((callback.ds !== 1) || ((callback.cX !== 'view-action') || (!A2($elm$core$List$member, callback.b3, model.av)))) {
						return _Utils_Tuple2(current, _List_Nil);
					} else {
						var popup = _Utils_eq(
							A2(
								$elm$json$Json$Decode$decodeValue,
								A2($elm$json$Json$Decode$field, 'surface', $elm$json$Json$Decode$string),
								callback.dB),
							$elm$core$Result$Ok('popup'));
						var ownerChange = (!popup) && (!_Utils_eq(
							model.eb,
							$elm$core$Maybe$Just(callback.b3)));
						var canMove = (!ownerChange) || $author$project$OutputController$freshRelocationPossible(model.bT);
						if ((popup && (!_Utils_eq(
							$author$project$OutputController$owner(current),
							$elm$core$Maybe$Just(callback.b3)))) || (!canMove)) {
							return _Utils_Tuple2(current, _List_Nil);
						} else {
							var _v10 = A4(
								$author$project$Surface$resolve,
								$author$project$SurfaceRenderer$publication(snapshot),
								$author$project$SurfaceRenderer$lease(snapshot),
								callback.dB,
								$author$project$SurfaceController$desktop(model.bT));
							if (_v10.$ === 1) {
								return _Utils_Tuple2(current, _List_Nil);
							} else {
								var message = _v10.a;
								var _v11 = A2(
									$author$project$OutputController$assignOwner,
									$elm$core$Maybe$Just(callback.b3),
									model.bT);
								var assigned = _v11.a;
								var ownerEffects = _v11.b;
								var _v12 = A2(
									$author$project$SurfaceController$update,
									$author$project$SurfaceController$Interaction(message),
									assigned);
								var updated = _v12.a;
								var effects = _v12.b;
								var _v13 = ownerChange ? A2($author$project$SurfaceController$update, $author$project$SurfaceController$NativeRelocate, updated) : _Utils_Tuple2(updated, _List_Nil);
								var next = _v13.a;
								var relocation = _v13.b;
								return _Utils_Tuple2(
									_Utils_update(
										model,
										{
											bT: next,
											eb: $elm$core$Maybe$Just(callback.b3)
										}),
									_Utils_ap(
										ownerEffects,
										_Utils_ap(effects, relocation)));
							}
						}
					}
				} else {
					return _Utils_Tuple2(current, _List_Nil);
				}
			case 4:
				var raw = event.a;
				return A3($author$project$OutputController$nativePopup, $author$project$SurfaceController$NativeDismiss, raw, current);
			default:
				var raw = event.a;
				return A3($author$project$OutputController$nativePopup, $author$project$SurfaceController$NativeReflow, raw, current);
		}
	});
var $author$project$Main$update = F2(
	function (message, model) {
		var event = function () {
			switch (message.$) {
				case 0:
					var raw = message.a;
					return $elm$core$Maybe$Just(
						$author$project$OutputController$Disposition(raw));
				case 5:
					var raw = message.a;
					return $elm$core$Maybe$Just(
						$author$project$OutputController$Topology(raw));
				case 1:
					var raw = message.a;
					return $elm$core$Maybe$Just(
						$author$project$OutputController$Interaction(
							$author$project$Desktop$Incoming(raw)));
				case 2:
					var raw = message.a;
					return $elm$core$Maybe$Just(
						$author$project$OutputController$Renderer(raw));
				case 6:
					var value = message.a;
					return $elm$core$Maybe$Just(
						$author$project$OutputController$Interaction(value));
				case 4:
					var raw = message.a;
					return $elm$core$Maybe$Just(
						$author$project$OutputController$Reflow(raw));
				default:
					var raw = message.a;
					return $elm$core$Maybe$Just(
						$author$project$OutputController$Dismiss(raw));
			}
		}();
		if (event.$ === 1) {
			return _Utils_Tuple2(model, $elm$core$Platform$Cmd$none);
		} else {
			var value = event.a;
			var _v1 = A2($author$project$OutputController$update, value, model.bT);
			var updated = _v1.a;
			var effects = _v1.b;
			var _v2 = A2($author$project$OutputController$register, effects, updated);
			var next = _v2.a;
			var packet = _v2.b;
			return _Utils_Tuple2(
				_Utils_update(
					model,
					{bT: next}),
				$elm$core$Platform$Cmd$batch(
					_List_fromArray(
						[
							A2($author$project$Main$commit, packet, effects),
							model.cs ? $author$project$Main$inspections(
							$author$project$Inspection$packet(
								$author$project$OutputController$controller(next))) : $elm$core$Platform$Cmd$none
						])));
		}
	});
var $author$project$Main$main = $elm$browser$Browser$element(
	{
		dW: function (qa) {
			return _Utils_Tuple2(
				{bT: $author$project$OutputController$initial, cs: qa},
				$elm$core$Platform$Cmd$none);
		},
		ec: function (_v0) {
			return $elm$core$Platform$Sub$batch(
				_List_fromArray(
					[
						$author$project$Main$nativeBatchDispositions($author$project$Main$Disposition),
						$author$project$Main$nativeViews($author$project$Main$Topology),
						$author$project$Main$nativeEvents($author$project$Main$Native),
						$author$project$Main$rendererActions($author$project$Main$Action),
						$author$project$Main$nativeDismissals($author$project$Main$Dismiss),
						$author$project$Main$nativeReflows($author$project$Main$Reflow)
					]));
		},
		ee: $author$project$Main$update,
		ef: function (_v1) {
			return $elm$html$Html$text('');
		}
	});
_Platform_export({'Main':{'init':$author$project$Main$main($elm$json$Json$Decode$bool)(0)}});}(this));