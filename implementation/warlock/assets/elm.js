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
	if (region.dN.cp === region.d1.cp)
	{
		return 'on line ' + region.dN.cp;
	}
	return 'on lines ' + region.dN.cp + ' through ' + region.d1.cp;
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
		impl.fn,
		impl.fT,
		impl.fP,
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
		aJ: func(record.aJ),
		dO: record.dO,
		dH: record.dH
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
		var message = !tag ? value : tag < 3 ? value.a : value.aJ;
		var stopPropagation = tag == 1 ? value.b : tag == 3 && value.dO;
		var currentEventNode = (
			stopPropagation && event.stopPropagation(),
			(tag == 2 ? value.b : tag == 3 && value.dH) && event.preventDefault(),
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
		impl.fn,
		impl.fT,
		impl.fP,
		function(sendToApp, initialModel) {
			var view = impl.fU;
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
		impl.fn,
		impl.fT,
		impl.fP,
		function(sendToApp, initialModel) {
			var divertHrefToApp = impl.dM && impl.dM(sendToApp)
			var view = impl.fU;
			var title = _VirtualDom_doc.title;
			var bodyNode = _VirtualDom_doc.body;
			var currNode = _VirtualDom_virtualize(bodyNode);
			return _Browser_makeAnimator(initialModel, function(model)
			{
				_VirtualDom_divertHrefToApp = divertHrefToApp;
				var doc = view(model);
				var nextNode = _VirtualDom_node('body')(_List_Nil)(doc.dU);
				var patches = _VirtualDom_diff(currNode, nextNode);
				bodyNode = _VirtualDom_applyPatches(bodyNode, currNode, patches, sendToApp);
				currNode = nextNode;
				_VirtualDom_divertHrefToApp = 0;
				(title !== doc.cA) && (_VirtualDom_doc.title = title = doc.cA);
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
	var onUrlChange = impl.fu;
	var onUrlRequest = impl.fv;
	var key = function() { key.a(onUrlChange(_Browser_getUrl())); };

	return _Browser_document({
		dM: function(sendToApp)
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
							&& curr.eE === next.eE
							&& curr.be === next.be
							&& curr.ez.a === next.ez.a
						)
							? $elm$browser$Browser$Internal(next)
							: $elm$browser$Browser$External(href)
					));
				}
			});
		},
		fn: function(flags)
		{
			return A3(impl.fn, flags, _Browser_getUrl(), key);
		},
		fU: impl.fU,
		fT: impl.fT,
		fP: impl.fP
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
		? { fj: 'hidden', e8: 'visibilitychange' }
		:
	(typeof _VirtualDom_doc.mozHidden !== 'undefined')
		? { fj: 'mozHidden', e8: 'mozvisibilitychange' }
		:
	(typeof _VirtualDom_doc.msHidden !== 'undefined')
		? { fj: 'msHidden', e8: 'msvisibilitychange' }
		:
	(typeof _VirtualDom_doc.webkitHidden !== 'undefined')
		? { fj: 'webkitHidden', e8: 'webkitvisibilitychange' }
		: { fj: 'hidden', e8: 'visibilitychange' };
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
		eN: _Browser_getScene(),
		eV: {
			a6: _Browser_window.pageXOffset,
			a7: _Browser_window.pageYOffset,
			a5: _Browser_doc.documentElement.clientWidth,
			aX: _Browser_doc.documentElement.clientHeight
		}
	};
}

function _Browser_getScene()
{
	var body = _Browser_doc.body;
	var elem = _Browser_doc.documentElement;
	return {
		a5: Math.max(body.scrollWidth, body.offsetWidth, elem.scrollWidth, elem.offsetWidth, elem.clientWidth),
		aX: Math.max(body.scrollHeight, body.offsetHeight, elem.scrollHeight, elem.offsetHeight, elem.clientHeight)
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
			eN: {
				a5: node.scrollWidth,
				aX: node.scrollHeight
			},
			eV: {
				a6: node.scrollLeft,
				a7: node.scrollTop,
				a5: node.clientWidth,
				aX: node.clientHeight
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
			eN: _Browser_getScene(),
			eV: {
				a6: x,
				a7: y,
				a5: _Browser_doc.documentElement.clientWidth,
				aX: _Browser_doc.documentElement.clientHeight
			},
			fc: {
				a6: x + rect.left,
				a7: y + rect.top,
				a5: rect.width,
				aX: rect.height
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
		if (!builder.Q) {
			return A4(
				$elm$core$Array$Array_elm_builtin,
				$elm$core$Elm$JsArray$length(builder.S),
				$elm$core$Array$shiftStep,
				$elm$core$Elm$JsArray$empty,
				builder.S);
		} else {
			var treeLen = builder.Q * $elm$core$Array$branchFactor;
			var depth = $elm$core$Basics$floor(
				A2($elm$core$Basics$logBase, $elm$core$Array$branchFactor, treeLen - 1));
			var correctNodeList = reverseNodeList ? $elm$core$List$reverse(builder.V) : builder.V;
			var tree = A2($elm$core$Array$treeFromBuilder, correctNodeList, builder.Q);
			return A4(
				$elm$core$Array$Array_elm_builtin,
				$elm$core$Elm$JsArray$length(builder.S) + treeLen,
				A2($elm$core$Basics$max, 5, depth * $elm$core$Array$shiftStep),
				tree,
				builder.S);
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
					{V: nodeList, Q: (len / $elm$core$Array$branchFactor) | 0, S: tail});
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
		return {d7: fragment, be: host, ew: path, ez: port_, eE: protocol, c_: query};
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
var $author$project$OutcomeAnnouncements$Model = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$UInt64$Counter = $elm$core$Basics$identity;
var $author$project$UInt64$zero = '0';
var $author$project$OutcomeAnnouncements$initial = A2($author$project$OutcomeAnnouncements$Model, $author$project$UInt64$zero, $elm$core$Maybe$Nothing);
var $author$project$SurfaceController$Model = $elm$core$Basics$identity;
var $author$project$ReconciliationTracking$empty = {bf: $elm$core$Maybe$Nothing, bC: _List_Nil, N: _List_Nil};
var $author$project$Desktop$KeyboardEntry = 1;
var $author$project$Launch$Idle = {$: 0};
var $author$project$Launch$Model = $elm$core$Basics$identity;
var $author$project$Launch$init = {be: $elm$core$Maybe$Nothing, j: $author$project$Launch$Idle, c1: $author$project$UInt64$zero, c2: $author$project$UInt64$zero, c: $elm$core$Maybe$Nothing};
var $author$project$Files$initial = {fb: '', ft: 'Loading Files…', ex: $elm$core$Maybe$Nothing, c: $elm$core$Maybe$Nothing, ca: _List_Nil};
var $author$project$JumpList$initial = {ft: 'Reading application actions…', ex: $elm$core$Maybe$Nothing, c: $elm$core$Maybe$Nothing, ca: _List_Nil};
var $author$project$MotionPreferences$System = 0;
var $author$project$MotionPreferences$initial = {fb: 0, ft: 'Reading motion preference…', ex: $elm$core$Maybe$Nothing, c: $elm$core$Maybe$Nothing};
var $author$project$Motion$initial = {bT: $elm$core$Maybe$Nothing, bF: $elm$core$Maybe$Nothing, ex: $elm$core$Maybe$Nothing, a1: $author$project$MotionPreferences$initial};
var $author$project$Notifications$initial = {
	ci: $elm$core$Maybe$Nothing,
	ft: 'Loading notifications…',
	cZ: $elm$core$Maybe$Nothing,
	ex: $elm$core$Maybe$Nothing,
	fD: {cP: false, ef: false},
	c: $elm$core$Maybe$Nothing,
	ca: _List_Nil
};
var $author$project$OverviewRecovery$Idle = {$: 0};
var $author$project$OverviewRecovery$initial = $author$project$OverviewRecovery$Idle;
var $author$project$Pins$initial = {ft: '', ex: $elm$core$Maybe$Nothing, c: $elm$core$Maybe$Nothing};
var $author$project$PointerOwnership$initial = {bF: $elm$core$Maybe$Nothing};
var $author$project$Settings$Night = 0;
var $author$project$Settings$defaults = {cQ: false, c$: false, cy: 100, de: 0};
var $author$project$Settings$initial = {fb: $author$project$Settings$defaults, ft: 'Loading settings…', cZ: $elm$core$Maybe$Nothing, ex: $elm$core$Maybe$Nothing, c: $elm$core$Maybe$Nothing};
var $author$project$ShortcutPreferences$Undecided = 0;
var $author$project$ShortcutPreferences$defaults = {aD: 0, C: 0, bP: 0};
var $author$project$ShortcutPreferences$initial = {fb: $author$project$ShortcutPreferences$defaults, cV: $elm$core$Maybe$Nothing, ft: 'Loading shortcut choices…', ex: $elm$core$Maybe$Nothing, c: $elm$core$Maybe$Nothing};
var $author$project$Shortcuts$initial = {dk: $elm$core$Maybe$Nothing, bM: $author$project$UInt64$zero};
var $author$project$Switcher$Idle = 0;
var $author$project$Switcher$Model = $elm$core$Basics$identity;
var $elm$core$Dict$RBEmpty_elm_builtin = {$: -2};
var $elm$core$Dict$empty = $elm$core$Dict$RBEmpty_elm_builtin;
var $author$project$Switcher$initial = {ba: $elm$core$Maybe$Nothing, af: _List_Nil, fh: $author$project$UInt64$zero, cY: $elm$core$Maybe$Nothing, j: 0, b5: false, c0: $elm$core$Maybe$Nothing, dL: _List_Nil, fN: 0, bO: $elm$core$Dict$empty};
var $author$project$SystemMenu$initial = {ft: 'Loading system state…', ex: $elm$core$Maybe$Nothing, c: $elm$core$Maybe$Nothing, ca: _List_Nil};
var $author$project$MenuBridge$Model = $elm$core$Basics$identity;
var $author$project$ReceiptRouter$Model = $elm$core$Basics$identity;
var $author$project$ReceiptRouter$empty = _List_Nil;
var $author$project$Menu$Model = $elm$core$Basics$identity;
var $author$project$Menu$init = {az: false, aY: _List_Nil, co: $elm$core$Maybe$Nothing, aI: $elm$core$Maybe$Nothing, cr: 1, cs: 1, fx: _List_Nil, bL: _List_Nil, a3: _List_Nil};
var $author$project$MenuBridge$initial = {aI: $author$project$Menu$init, O: $elm$core$Maybe$Nothing, dG: $author$project$UInt64$zero, bJ: $elm$core$Maybe$Nothing, au: $author$project$ReceiptRouter$empty};
var $author$project$Shell$Detached = 0;
var $author$project$Effects$empty = {bb: false, fh: $author$project$UInt64$zero, as: $elm$core$Maybe$Nothing, c1: $author$project$UInt64$zero, fS: $elm$core$Maybe$Nothing, z: _List_Nil};
var $author$project$Shell$initial = {am: false, dk: $elm$core$Maybe$Nothing, d$: false, _: $author$project$Effects$empty, A: $elm$core$Maybe$Nothing, ap: $elm$core$Maybe$Nothing, ea: $elm$core$Maybe$Nothing, ds: $elm$core$Maybe$Nothing, eb: $elm$core$Maybe$Nothing, U: _List_Nil, ft: 'Connecting…', aA: false, j: 0, a2: false, ct: false, bm: true, b7: $elm$core$Maybe$Nothing, c1: $author$project$UInt64$zero, X: false};
var $author$project$TaskbarShell$initial = {fh: $author$project$UInt64$zero, h: $author$project$MenuBridge$initial, J: $elm$core$Maybe$Nothing, b: $author$project$Shell$initial};
var $author$project$Desktop$initial = {
	F: $elm$core$Maybe$Nothing,
	aD: $elm$core$Maybe$Nothing,
	bu: $elm$core$Maybe$Nothing,
	bv: false,
	k: $elm$core$Maybe$Nothing,
	G: '',
	A: $elm$core$Maybe$Nothing,
	T: $author$project$Files$initial,
	aW: $elm$core$Maybe$Nothing,
	p: false,
	B: false,
	cW: false,
	o: $elm$core$Maybe$Nothing,
	aZ: $elm$core$Maybe$Nothing,
	ar: $author$project$JumpList$initial,
	w: false,
	M: $author$project$Launch$init,
	H: $elm$core$Maybe$Nothing,
	I: $author$project$Motion$initial,
	aK: $elm$core$Maybe$Nothing,
	ah: $elm$core$Maybe$Nothing,
	C: $author$project$Notifications$initial,
	a0: $elm$core$Maybe$Nothing,
	t: false,
	D: false,
	q: false,
	m: false,
	aN: $author$project$OverviewRecovery$initial,
	aB: $elm$core$Maybe$Nothing,
	at: $elm$core$Maybe$Nothing,
	b1: false,
	bj: $elm$core$Maybe$Nothing,
	R: $author$project$Pins$initial,
	bH: $author$project$PointerOwnership$initial,
	bI: 1,
	aO: $elm$core$Maybe$Just($author$project$UInt64$zero),
	c_: '',
	c1: $author$project$UInt64$zero,
	u: $elm$core$Maybe$Nothing,
	aj: $author$project$Settings$initial,
	bo: $elm$core$Maybe$Nothing,
	c8: true,
	n: false,
	L: false,
	aQ: $elm$core$Maybe$Nothing,
	ac: $author$project$ShortcutPreferences$initial,
	b8: $author$project$Shortcuts$initial,
	x: $elm$core$Maybe$Nothing,
	i: $author$project$Switcher$initial,
	aR: $elm$core$Maybe$Nothing,
	aS: $elm$core$Maybe$Nothing,
	cw: $elm$core$Maybe$Nothing,
	ak: $author$project$SystemMenu$initial,
	s: $elm$core$Maybe$Nothing,
	aT: $elm$core$Maybe$Nothing,
	v: false,
	E: false,
	a: $author$project$TaskbarShell$initial
};
var $author$project$SurfaceController$initial = {d: $author$project$Desktop$initial, az: false, em: $author$project$UInt64$zero, eF: $author$project$UInt64$zero, ai: $author$project$ReconciliationTracking$empty};
var $author$project$OutputController$initial = {bS: $author$project$OutcomeAnnouncements$initial, aE: false, aw: _List_Nil, aF: false, cM: $author$project$SurfaceController$initial, cS: $author$project$UInt64$zero, bE: _List_Nil, c2: $author$project$UInt64$zero, fN: $elm$core$Maybe$Nothing, av: _List_Nil};
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
	return {$: 11, a: a};
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
	return {$: 67, a: a};
};
var $author$project$Desktop$Deadline = function (a) {
	return {$: 66, a: a};
};
var $author$project$Main$Deadline = function (a) {
	return {$: 6, a: a};
};
var $author$project$TaskbarShell$ExpirePrepared = function (a) {
	return {$: 6, a: a};
};
var $author$project$Desktop$Window = function (a) {
	return {$: 1, a: a};
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
	return model.cM;
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
	var _v0 = _Utils_Tuple2(model.dk, model._.as);
	if ((!_v0.a.$) && (!_v0.b.$)) {
		var binding = _v0.a.a;
		var observed = _v0.b.a;
		return A3($author$project$Binding$matchesContext, observed.P.fp, observed.P.fe, binding) ? $elm$core$Maybe$Just(
			A3($author$project$Shell$Stamp, binding, observed.P.y, observed.P.c2)) : $elm$core$Maybe$Nothing;
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
			return $.c;
		},
		state.bJ);
};
var $elm$json$Json$Decode$decodeValue = _Json_run;
var $author$project$SurfaceController$desktop = function (_v0) {
	var model = _v0;
	return model.d;
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
var $elm$core$Maybe$andThen = F2(
	function (callback, maybeValue) {
		if (!maybeValue.$) {
			var value = maybeValue.a;
			return callback(value);
		} else {
			return $elm$core$Maybe$Nothing;
		}
	});
var $author$project$Switcher$Forward = 0;
var $author$project$TaskbarShell$Native = function (a) {
	return {$: 0, a: a};
};
var $author$project$Desktop$OpenApplications = function (a) {
	return {$: 12, a: a};
};
var $author$project$Desktop$OpenFiles = function (a) {
	return {$: 18, a: a};
};
var $author$project$Desktop$OpenNotifications = function (a) {
	return {$: 30, a: a};
};
var $author$project$Desktop$OpenOverview = function (a) {
	return {$: 48, a: a};
};
var $author$project$Desktop$OpenSettings = function (a) {
	return {$: 36, a: a};
};
var $author$project$Desktop$OpenSwitcher = F2(
	function (a, b) {
		return {$: 49, a: a, b: b};
	});
var $author$project$Desktop$OpenSystemMenu = function (a) {
	return {$: 24, a: a};
};
var $author$project$TaskbarShell$Primary = F2(
	function (a, b) {
		return {$: 1, a: a, b: b};
	});
var $author$project$Shell$Reconnect = {$: 5};
var $author$project$Desktop$RetryWindows = {$: 68};
var $author$project$Desktop$Start = function (a) {
	return {$: 65, a: a};
};
var $author$project$Taskbar$Unavailable = {$: 3};
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
				return !transaction.W;
			},
			model.fS));
};
var $author$project$Shell$available = function (model) {
	return (!model.ct) && ((!model.X) && ((model.j === 2) && ((!model.am) && ((!$author$project$Effects$pending(model._)) && (_Utils_eq(model.ea, $elm$core$Maybe$Nothing) && ((!A2(
		$elm$core$Maybe$withDefault,
		false,
		A2(
			$elm$core$Maybe$map,
			function ($) {
				return $._;
			},
			model.ds))) || (_Utils_eq(model.eb, $elm$core$Maybe$Nothing) && (!_Utils_eq(model.ap, $elm$core$Maybe$Nothing)))))))));
};
var $author$project$Desktop$ViewStamp = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$Desktop$capture = function (model) {
	return A2(
		$elm$core$Maybe$map,
		$author$project$Desktop$ViewStamp(model.a.b.dk),
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
				return _Utils_eq(t.aa.P.fp, lifetime) && (_Utils_eq(t.aa.aq, incarnation) && A2(
					$elm$core$List$member,
					t.W,
					_List_fromArray(
						[0, 4])));
			},
			model.z);
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
				var _v1 = entry.dk;
				var value = _v1;
				return _Utils_eq(
					value.fR,
					$author$project$Menu$Window(window));
			},
			state.fx);
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
		az: state.az,
		eg: $elm$core$List$length(state.aY),
		co: state.co,
		aI: state.aI,
		fx: $elm$core$List$length(state.fx),
		bL: $elm$core$List$length(state.bL),
		eL: $elm$core$List$length(state.a3)
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
				return A2($author$project$ActionProjection$rootOf, incarnation, observed.eN);
			},
			shell._.as);
		var nativeBlocked = function () {
			var _v2 = _Utils_Tuple3(shell.dk, shell._.as, root);
			if (((!_v2.a.$) && (!_v2.b.$)) && (!_v2.c.$)) {
				var observed = _v2.b.a;
				var family = _v2.c.a;
				return A2(
					$elm$core$List$any,
					function (window) {
						return A3($author$project$Effects$blocked, observed.P.fp, window.aq, shell._);
					},
					A2(
						$elm$core$List$filter,
						function (window) {
							return _Utils_eq(
								A2($author$project$ActionProjection$rootOf, window.aq, observed.eN),
								$elm$core$Maybe$Just(family));
						},
						$author$project$ActionProjection$windows(observed.eN)));
			} else {
				return A2(
					$elm$core$List$any,
					function (transaction) {
						return A2(
							$elm$core$List$member,
							transaction.W,
							_List_fromArray(
								[0, 4]));
					},
					shell._.z);
			}
		}();
		var blocked = function () {
			var _v1 = _Utils_Tuple2(shell.dk, root);
			if ((!_v1.a.$) && (!_v1.b.$)) {
				var _native = _v1.a.a;
				var family = _v1.b.a;
				return A2(
					$author$project$Menu$hasOutstandingFor,
					A2(
						$author$project$Menu$windowId,
						$author$project$Binding$authorityIdentity(_native),
						$author$project$UInt64$string(family)),
					state.aI);
			} else {
				return $author$project$Menu$snapshot(state.aI).fx > 0;
			}
		}();
		return blocked || nativeBlocked;
	});
var $author$project$Surface$familyBlocked = F2(
	function (model, incarnation) {
		return A3($author$project$MenuBridge$blockedFor, incarnation, model.a.b, model.a.h);
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
					return _Utils_eq(g.a_, key);
				},
				accumulated) ? A2(
				$elm$core$List$map,
				function (g) {
					return _Utils_eq(g.a_, key) ? _Utils_update(
						g,
						{
							aG: _Utils_ap(
								g.aG,
								_List_fromArray(
									[entry]))
						}) : g;
				},
				accumulated) : _Utils_ap(
				accumulated,
				_List_fromArray(
					[
						{
						aG: _List_fromArray(
							[entry]),
						a_: key
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
					A2($author$project$ActionProjection$rootOf, w.aq, projection),
					$elm$core$Maybe$Just(root.aq));
			},
			rows);
		var key = $elm$core$String$isEmpty(root.di) ? ('window:' + $author$project$UInt64$string(root.aq)) : ('application:' + root.di);
		return _Utils_Tuple2(
			key,
			{
				bt: _Utils_eq(
					activeRoot,
					$elm$core$Maybe$Just(root.aq)),
				di: root.di,
				dS: A2(
					$elm$core$List$any,
					function ($) {
						return $.dS;
					},
					members),
				dj: A2(
					$elm$core$List$all,
					function ($) {
						return $.dj;
					},
					members),
				el: root.el,
				b_: root.b_,
				r: root.aq
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
						return A2($author$project$UInt64$compare, a.aq, b.aq);
					}),
				A2(
					$elm$core$List$filter,
					function (w) {
						return _Utils_eq(w.dD, $elm$core$Maybe$Nothing);
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
					return $.eN;
				},
				$author$project$Taskbar$groups),
			model.b._.as));
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
			A2($elm$core$Maybe$map, $author$project$Desktop$host, model.a.b.dk)) + (':' + (A2(
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
			model.aD);
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
							return _Utils_eq(family.di, identity) || ((!$elm$core$String$isEmpty(entry.fW)) && _Utils_eq(family.di, entry.fW));
						},
						group.aG);
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
				return $.fl;
			},
			model.R.c));
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
				return (!entry.dj) ? $author$project$Taskbar$Unavailable : (entry.b_ ? A2($author$project$Taskbar$Apply, $author$project$Effects$Restore, entry.r) : (entry.bt ? A2($author$project$Taskbar$Apply, $author$project$Effects$Minimize, entry.r) : A2($author$project$Taskbar$Apply, $author$project$Effects$Activate, entry.r)));
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
			f: 'Refresh window status; read observations without retrying actions',
			e: 'Observation only',
			g: A2($author$project$Desktop$key, model, identity),
			fd: (!(!model.a.b.j)) && ((model.a.b.j !== 3) && (!$author$project$Effects$pending(model.a.b._))),
			cl: identity,
			el: 'Refresh window status',
			aJ: $elm$core$Maybe$Just(
				$author$project$Desktop$Window(
					$author$project$TaskbarShell$Native($author$project$Shell$Refresh)))
		};
	});
var $author$project$Effects$Refused = 2;
var $author$project$MenuBridge$menuSnapshot = function (_v0) {
	var state = _v0;
	return $author$project$Menu$snapshot(state.aI);
};
var $author$project$Surface$recoveryNeeded = function (model) {
	return A2(
		$elm$core$List$any,
		function (transaction) {
			return A2(
				$elm$core$List$member,
				transaction.W,
				_List_fromArray(
					[0, 4]));
		},
		model.a.b._.z) || (A2(
		$elm$core$Maybe$withDefault,
		false,
		A2(
			$elm$core$Maybe$map,
			function (transaction) {
				return A2(
					$elm$core$List$member,
					transaction.W,
					_List_fromArray(
						[2, 4]));
			},
			model.a.b._.fS)) || ($author$project$MenuBridge$menuSnapshot(model.a.h).fx > 0));
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
	return {fh: generation, fp: lifetime};
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
								return A5($author$project$Launch$Selection, host, model.c2, scope.fp, scope.fh, entry.cU);
							},
							A2($author$project$Catalog$lookup, identity, snapshot));
					}),
				model.be,
				model.c));
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
		f: 'Open window switcher',
		e: '',
		g: A2($author$project$Desktop$key, model, 'control:switcher-opener'),
		fd: $author$project$Shell$available(model.a.b) && _Utils_eq(model.k, $elm$core$Maybe$Nothing),
		cl: 'bar:switcher',
		el: 'Switch windows',
		aJ: A2(
			$elm$core$Maybe$map,
			function (stamp) {
				return A2($author$project$Desktop$OpenSwitcher, stamp, 0);
			},
			$author$project$Desktop$capture(model))
	};
	var retry = {
		f: 'Refresh windows',
		e: '',
		g: A2($author$project$Desktop$key, model, 'refresh-windows'),
		fd: _Utils_eq(model.k, $elm$core$Maybe$Nothing),
		cl: 'bar:refresh-windows',
		el: 'Refresh windows',
		aJ: $elm$core$Maybe$Just($author$project$Desktop$RetryWindows)
	};
	var recovery = ($author$project$Surface$recoveryNeeded(model) && (!(!model.a.b.j))) ? _List_fromArray(
		[
			A2($author$project$Surface$recoveryControl, 'bar:recovery-refresh', model)
		]) : _List_Nil;
	var reconnect = {
		f: 'Reconnect to the window system',
		e: '',
		g: 'reconnect',
		fd: !model.a.b.bm,
		cl: 'bar:reconnect',
		el: 'Reconnect',
		aJ: $elm$core$Maybe$Just(
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
							return _Utils_eq(matched.a_, group.a_);
						},
						A2($author$project$Desktop$pinnedGroup, identity, model)));
			},
			pinIds);
	};
	var overview = {
		f: 'Open Task View',
		e: '',
		g: A2($author$project$Desktop$key, model, 'control:overview-opener'),
		fd: $author$project$Shell$available(model.a.b) && _Utils_eq(model.k, $elm$core$Maybe$Nothing),
		cl: 'bar:overview',
		el: 'Task View',
		aJ: A2(
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
			var _v6 = group.aG;
			if (_v6.b && (!_v6.b.b)) {
				var family = _v6.a;
				return family.b_ ? 'Minimized' : (family.bt ? 'Active' : 'Open');
			} else {
				return $elm$core$String$fromInt(
					$elm$core$List$length(group.aG)) + ' windows';
			}
		}();
		var scoped = $author$project$Shell$capture(model.a.b);
		var operation = function () {
			var _v2 = A2($author$project$Taskbar$primary, false, group.aG);
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
					return $.el;
				},
				$elm$core$List$head(group.aG)));
		var blocked = function () {
			var _v1 = A2($author$project$Taskbar$primary, false, group.aG);
			if (_v1.$ === 2) {
				var incarnation = _v1.b;
				return A2($author$project$Surface$familyBlocked, model, incarnation);
			} else {
				return false;
			}
		}();
		var ready = $author$project$Shell$available(model.a.b) && ((!_Utils_eq(
			A2($author$project$Taskbar$primary, false, group.aG),
			$author$project$Taskbar$Unavailable)) && (!blocked));
		var attention = A2(
			$elm$core$List$any,
			function ($) {
				return $.dS;
			},
			group.aG) && (!A2(
			$elm$core$List$any,
			function ($) {
				return $.bt;
			},
			group.aG));
		var observedState = attention ? ('Attention; ' + state) : state;
		return {
			f: operation + (label + ('; ' + (observedState + (blocked ? '; awaiting native confirmation' : '')))),
			e: blocked ? ('Awaiting native confirmation; ' + observedState) : observedState,
			g: A2(
				$elm$core$Maybe$withDefault,
				'detached-group',
				A2(
					$elm$core$Maybe$map,
					function (stamp) {
						return 'group:' + ($author$project$Shell$stampKey(stamp) + (':' + group.a_));
					},
					scoped)),
			fd: ready,
			cl: 'bar:group:' + group.a_,
			el: label,
			aJ: ready ? A2(
				$elm$core$Maybe$map,
				function (stamp) {
					return $author$project$Desktop$Window(
						A2($author$project$TaskbarShell$Primary, stamp, group.a_));
				},
				scoped) : $elm$core$Maybe$Nothing
		};
	};
	var pinControl = function (identity) {
		var entry = A2(
			$elm$core$Maybe$andThen,
			$author$project$Catalog$lookup(identity),
			model.aD);
		var label = A2(
			$elm$core$Maybe$withDefault,
			identity,
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.dA;
				},
				entry));
		var disabled = function (reason) {
			return {
				f: _Utils_ap(reason, label),
				e: reason,
				g: A2($author$project$Desktop$key, model, 'pin:' + identity),
				fd: false,
				cl: 'bar:pin:' + identity,
				el: label,
				aJ: $elm$core$Maybe$Nothing
			};
		};
		var choice = $author$project$Shell$available(model.a.b) ? A2(
			$elm$core$Maybe$map,
			$author$project$Desktop$Start,
			A2($author$project$Launch$select, identity, model.M)) : $elm$core$Maybe$Nothing;
		var _v0 = A2($author$project$Desktop$pinnedGroup, identity, model);
		if (!_v0.$) {
			var group = _v0.a;
			if ($elm$core$List$length(
				owners(group)) === 1) {
				var control = groupControl(group);
				return _Utils_update(
					control,
					{e: 'Pinned; ' + control.e, cl: 'bar:pin:' + identity, el: label});
			} else {
				return disabled('Ambiguous application identity: ');
			}
		} else {
			return _Utils_eq(entry, $elm$core$Maybe$Nothing) ? disabled('Unavailable application: ') : ((!$elm$core$List$isEmpty(
				A2($author$project$Desktop$pinGroups, identity, model))) ? disabled('Ambiguous application identity: ') : {
				f: 'Open ' + label,
				e: 'Pinned launcher',
				g: A2($author$project$Desktop$key, model, 'pin:' + identity),
				fd: !_Utils_eq(choice, $elm$core$Maybe$Nothing),
				cl: 'bar:pin:' + identity,
				el: label,
				aJ: choice
			});
		}
	};
	var applications = _Utils_ap(
		A2($elm$core$List$map, pinControl, pinIds),
		A2($elm$core$List$map, groupControl, ordinaryGroups));
	var application = {
		f: 'Open applications',
		e: '',
		g: A2($author$project$Desktop$key, model, 'control:opener'),
		fd: !(!model.a.b.j),
		cl: 'bar:applications',
		el: 'Applications',
		aJ: A2(
			$elm$core$Maybe$map,
			$author$project$Desktop$OpenApplications,
			$author$project$Desktop$capture(model))
	};
	var utilities = A2(
		$elm$core$List$cons,
		(!model.a.b.j) ? reconnect : application,
		A2(
			$elm$core$List$cons,
			overview,
			A2(
				$elm$core$List$cons,
				switcher,
				A2(
					$elm$core$List$cons,
					{
						f: 'Open notifications',
						e: '',
						g: A2($author$project$Desktop$key, model, 'notifications:opener'),
						fd: !_Utils_eq(model.a.b.dk, $elm$core$Maybe$Nothing),
						cl: 'bar:notifications',
						el: 'Notifications' + A2(
							$elm$core$Maybe$withDefault,
							'',
							A2(
								$elm$core$Maybe$map,
								function (snapshot) {
									var count = $elm$core$List$length(
										A2(
											$elm$core$List$filter,
											function (entry) {
												return entry.dc === 'live';
											},
											snapshot.af));
									return (!count) ? '' : (' · ' + $elm$core$String$fromInt(count));
								},
								model.C.c)),
						aJ: A2(
							$elm$core$Maybe$map,
							$author$project$Desktop$OpenNotifications,
							$author$project$Desktop$capture(model))
					},
					A2(
						$elm$core$List$cons,
						{
							f: 'Open Files menu',
							e: '',
							g: A2($author$project$Desktop$key, model, 'files:opener'),
							fd: !_Utils_eq(model.a.b.dk, $elm$core$Maybe$Nothing),
							cl: 'bar:files',
							el: 'Files',
							aJ: A2(
								$elm$core$Maybe$map,
								$author$project$Desktop$OpenFiles,
								$author$project$Desktop$capture(model))
						},
						A2(
							$elm$core$List$cons,
							{
								f: 'Open system menu',
								e: '',
								g: A2($author$project$Desktop$key, model, 'system:opener'),
								fd: !_Utils_eq(model.a.b.dk, $elm$core$Maybe$Nothing),
								cl: 'bar:system',
								el: 'System',
								aJ: A2(
									$elm$core$Maybe$map,
									$author$project$Desktop$OpenSystemMenu,
									$author$project$Desktop$capture(model))
							},
							A2(
								$elm$core$List$cons,
								{
									f: 'Open settings',
									e: '',
									g: A2($author$project$Desktop$key, model, 'settings:opener'),
									fd: !_Utils_eq(model.a.b.dk, $elm$core$Maybe$Nothing),
									cl: 'bar:settings',
									el: 'Settings',
									aJ: A2(
										$elm$core$Maybe$map,
										$author$project$Desktop$OpenSettings,
										$author$project$Desktop$capture(model))
								},
								_List_Nil)))))));
	return _Utils_ap(
		recovery,
		_Utils_ap(
			(!model.a.b.j) ? _Utils_ap(utilities, applications) : _Utils_ap(applications, utilities),
			((!$elm$core$String$isEmpty(model.G)) && (!(!model.a.b.j))) ? _List_fromArray(
				[retry]) : _List_Nil));
};
var $author$project$Desktop$Acknowledge = function (a) {
	return {$: 69, a: a};
};
var $author$project$Menu$Activate = F3(
	function (a, b, c) {
		return {$: 3, a: a, b: b, c: c};
	});
var $author$project$ShortcutPreferences$Alternate = 3;
var $author$project$Desktop$ApplySnap = function (a) {
	return {$: 5, a: a};
};
var $author$project$Switcher$Browsing = 2;
var $author$project$Desktop$CancelOverviewTransfer = function (a) {
	return {$: 58, a: a};
};
var $author$project$Desktop$CancelSystemChange = function (a) {
	return {$: 29, a: a};
};
var $author$project$TaskbarShell$Choose = F3(
	function (a, b, c) {
		return {$: 2, a: a, b: b, c: c};
	});
var $author$project$TaskbarShell$Close = F2(
	function (a, b) {
		return {$: 3, a: a, b: b};
	});
var $author$project$Desktop$CloseApplications = function (a) {
	return {$: 60, a: a};
};
var $author$project$Desktop$CloseFiles = function (a) {
	return {$: 19, a: a};
};
var $author$project$Desktop$CloseJumpList = function (a) {
	return {$: 15, a: a};
};
var $author$project$Desktop$CloseNotifications = function (a) {
	return {$: 31, a: a};
};
var $author$project$Desktop$CloseOverview = function (a) {
	return {$: 54, a: a};
};
var $author$project$Desktop$CloseSettings = function (a) {
	return {$: 37, a: a};
};
var $author$project$Desktop$CloseSnap = function (a) {
	return {$: 6, a: a};
};
var $author$project$Desktop$CloseSwitcher = function (a) {
	return {$: 53, a: a};
};
var $author$project$Desktop$CloseSystemMenu = function (a) {
	return {$: 25, a: a};
};
var $author$project$Desktop$CommitSwitcher = function (a) {
	return {$: 52, a: a};
};
var $author$project$Desktop$ConfigureNotificationPolicy = F2(
	function (a, b) {
		return {$: 34, a: a, b: b};
	});
var $author$project$Desktop$ConfirmSystemChange = F2(
	function (a, b) {
		return {$: 28, a: a, b: b};
	});
var $author$project$Settings$Dawn = 1;
var $author$project$ShortcutPreferences$Default = 2;
var $author$project$Menu$Dismiss = function (a) {
	return {$: 5, a: a};
};
var $author$project$Desktop$EditFilesPath = F2(
	function (a, b) {
		return {$: 21, a: a, b: b};
	});
var $author$project$Desktop$EditMotionPreference = F2(
	function (a, b) {
		return {$: 44, a: a, b: b};
	});
var $author$project$Desktop$EditSettings = F2(
	function (a, b) {
		return {$: 42, a: a, b: b};
	});
var $author$project$Desktop$EditShortcutChoice = F3(
	function (a, b, c) {
		return {$: 39, a: a, b: b, c: c};
	});
var $author$project$MotionPreferences$Full = 2;
var $author$project$Settings$HighContrast = 2;
var $author$project$Desktop$JumpAction = F2(
	function (a, b) {
		return {$: 17, a: a, b: b};
	});
var $author$project$ShortcutPreferences$Keep = 1;
var $author$project$SystemMenu$Lock = 6;
var $author$project$SystemMenu$Logout = 7;
var $author$project$TaskbarShell$MenuEvent = function (a) {
	return {$: 5, a: a};
};
var $author$project$Desktop$MovePin = F3(
	function (a, b, c) {
		return {$: 63, a: a, b: b, c: c};
	});
var $author$project$SystemMenu$Mute = 1;
var $author$project$SystemMenu$Network = 2;
var $author$project$Desktop$NotificationAction = F2(
	function (a, b) {
		return {$: 35, a: a, b: b};
	});
var $author$project$Desktop$OpenFilesPath = function (a) {
	return {$: 23, a: a};
};
var $author$project$Desktop$OpenFilesTarget = F2(
	function (a, b) {
		return {$: 22, a: a, b: b};
	});
var $author$project$Desktop$OpenJumpList = F2(
	function (a, b) {
		return {$: 14, a: a, b: b};
	});
var $author$project$Desktop$OpenOverviewTransfer = F2(
	function (a, b) {
		return {$: 57, a: a, b: b};
	});
var $author$project$Desktop$OpenSnap = F2(
	function (a, b) {
		return {$: 3, a: a, b: b};
	});
var $author$project$Desktop$OverviewChoose = F2(
	function (a, b) {
		return {$: 56, a: a, b: b};
	});
var $author$project$Desktop$OverviewTransfer = F3(
	function (a, b, c) {
		return {$: 59, a: a, b: b, c: c};
	});
var $author$project$Desktop$OverviewWorkspace = F2(
	function (a, b) {
		return {$: 55, a: a, b: b};
	});
var $author$project$SystemMenu$PowerOff = 5;
var $author$project$Menu$Ready = {$: 0};
var $author$project$SystemMenu$Reboot = 4;
var $author$project$MotionPreferences$Reduce = 1;
var $author$project$Desktop$RefreshApplications = function (a) {
	return {$: 13, a: a};
};
var $author$project$Desktop$RefreshFiles = function (a) {
	return {$: 20, a: a};
};
var $author$project$Desktop$RefreshJumpList = function (a) {
	return {$: 16, a: a};
};
var $author$project$Desktop$RefreshMotionPreference = function (a) {
	return {$: 46, a: a};
};
var $author$project$Desktop$RefreshNotifications = function (a) {
	return {$: 33, a: a};
};
var $author$project$Desktop$RefreshSettings = function (a) {
	return {$: 47, a: a};
};
var $author$project$Desktop$RefreshShortcutChoices = function (a) {
	return {$: 41, a: a};
};
var $author$project$Desktop$RefreshSystemMenu = function (a) {
	return {$: 26, a: a};
};
var $author$project$Switcher$Reverse = 1;
var $author$project$Desktop$SaveMotionPreference = function (a) {
	return {$: 45, a: a};
};
var $author$project$Desktop$SaveSettings = function (a) {
	return {$: 43, a: a};
};
var $author$project$Desktop$SaveShortcutChoices = function (a) {
	return {$: 40, a: a};
};
var $author$project$Desktop$SearchQuery = F2(
	function (a, b) {
		return {$: 61, a: a, b: b};
	});
var $author$project$Desktop$SelectSnap = F2(
	function (a, b) {
		return {$: 4, a: a, b: b};
	});
var $author$project$SystemMenu$Suspend = 3;
var $author$project$Desktop$SwitcherChoose = F2(
	function (a, b) {
		return {$: 51, a: a, b: b};
	});
var $author$project$Desktop$SwitcherStep = F2(
	function (a, b) {
		return {$: 50, a: a, b: b};
	});
var $author$project$Desktop$SystemChange = F2(
	function (a, b) {
		return {$: 27, a: a, b: b};
	});
var $author$project$Desktop$TogglePin = F2(
	function (a, b) {
		return {$: 62, a: a, b: b};
	});
var $author$project$Desktop$ToggleSettingsHelp = function (a) {
	return {$: 38, a: a};
};
var $author$project$SystemMenu$Volume = 0;
var $author$project$ShortcutPreferences$choices = F2(
	function (route, values) {
		switch (route) {
			case 'applications':
				return values.aD;
			case 'system':
				return values.bP;
			default:
				return values.C;
		}
	});
var $author$project$ShortcutPreferences$row = F2(
	function (route, inventory) {
		switch (route) {
			case 'applications':
				return inventory.aD;
			case 'system':
				return inventory.bP;
			default:
				return inventory.C;
		}
	});
var $author$project$ShortcutPreferences$changed = function (model) {
	return A2(
		$elm$core$Maybe$withDefault,
		false,
		A2(
			$elm$core$Maybe$map,
			function (current) {
				return !_Utils_eq(current.ae, model.fb);
			},
			model.c)) || A2(
		$elm$core$Maybe$withDefault,
		false,
		A2(
			$elm$core$Maybe$map,
			function (current) {
				return A2(
					$elm$core$List$any,
					function (route) {
						return !_Utils_eq(
							A2($author$project$ShortcutPreferences$choices, route, model.fb),
							A2($author$project$ShortcutPreferences$row, route, current).bt);
					},
					_List_fromArray(
						['applications', 'system', 'notifications']));
			},
			model.cV));
};
var $author$project$SystemMenu$code = function (operation) {
	switch (operation) {
		case 0:
			return 'volume-set';
		case 1:
			return 'volume-mute';
		case 2:
			return 'network-enable';
		case 3:
			return 'suspend';
		case 4:
			return 'reboot';
		case 5:
			return 'poweroff';
		case 6:
			return 'session-lock';
		default:
			return 'session-logout';
	}
};
var $author$project$Files$collections = _List_fromArray(
	[
		_Utils_Tuple2('recent', 'Recent'),
		_Utils_Tuple2('images', 'Images'),
		_Utils_Tuple2('videos', 'Videos'),
		_Utils_Tuple2('documents', 'Documents'),
		_Utils_Tuple2('downloads', 'Downloads'),
		_Utils_Tuple2('large', 'Large files'),
		_Utils_Tuple2('screenshots', 'Screenshots')
	]);
var $author$project$GeometryProjection$Maximized = 1;
var $author$project$GeometryProjection$window = F2(
	function (incarnation, snapshot) {
		return $elm$core$List$head(
			A2(
				$elm$core$List$filter,
				function (row) {
					return _Utils_eq(row.aq, incarnation);
				},
				snapshot.a));
	});
var $author$project$Surface$confirmedWindowState = F2(
	function (model, root) {
		var shell = model.a.b;
		return (!_Utils_eq(shell.eb, $elm$core$Maybe$Nothing)) ? '' : A2(
			$elm$core$Maybe$withDefault,
			'',
			A2(
				$elm$core$Maybe$map,
				function (window) {
					return A2(
						$elm$core$String$join,
						' • ',
						_Utils_ap(
							(window.es === 1) ? _List_fromArray(
								['Maximized']) : _List_Nil,
							A2(
								$elm$core$Maybe$withDefault,
								_List_Nil,
								A2(
									$elm$core$Maybe$map,
									function (pin) {
										return pin.fB ? _List_fromArray(
											['Always on top']) : _List_Nil;
									},
									window.dF))));
				},
				A2(
					$elm$core$Maybe$andThen,
					function (observed) {
						return (!_Utils_eq(
							shell.dk,
							$elm$core$Maybe$Just(observed.dk))) ? $elm$core$Maybe$Nothing : A2($author$project$GeometryProjection$window, root, observed);
					},
					shell.ap)));
	});
var $author$project$Transfer$ordinary = function (value) {
	return (!$elm$core$String$isEmpty(value)) && ((!A2($elm$core$String$startsWith, '0', value)) && (A2($elm$core$String$all, $elm$core$Char$isDigit, value) && (($elm$core$String$length(value) < 19) || (($elm$core$String$length(value) === 19) && (value <= '9223372036854775807')))));
};
var $author$project$Transfer$destinations = function (snapshot) {
	return A3(
		$elm$core$List$foldl,
		F2(
			function (w, ids) {
				var _v0 = w.e$;
				if (!_v0.$) {
					var id = _v0.a;
					return ($author$project$Transfer$ordinary(id) && (!A2($elm$core$List$member, id, ids))) ? _Utils_ap(
						ids,
						_List_fromArray(
							[id])) : ids;
				} else {
					return ids;
				}
			}),
		A2(
			$elm$core$List$map,
			$elm$core$String$fromInt,
			A2($elm$core$List$range, 1, 10)),
		snapshot.a);
};
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
var $author$project$Switcher$entries = function (_v0) {
	var model = _v0;
	return model.af;
};
var $author$project$TaskView$membership = F3(
	function (root, shell, geometry) {
		var pending = $elm$core$List$head(
			A2(
				$elm$core$List$filter,
				function (t) {
					return _Utils_eq(t.aa.aq, root) && (_Utils_eq(t.aa.P.fp, geometry.P.fp) && A2(
						$elm$core$List$member,
						t.W,
						_List_fromArray(
							[0, 4])));
				},
				shell._.z));
		var _v0 = A2(
			$elm$core$Maybe$map,
			A2(
				$elm$core$Basics$composeR,
				function ($) {
					return $.aa;
				},
				function ($) {
					return $.bh;
				}),
			pending);
		if ((!_v0.$) && (_v0.a.$ === 7)) {
			var p = _v0.a.a;
			return $elm$core$Maybe$Just(p.cv);
		} else {
			return A2(
				$elm$core$Maybe$andThen,
				function ($) {
					return $.e$;
				},
				A2($author$project$GeometryProjection$window, root, geometry));
		}
	});
var $author$project$TaskView$groups = function (shell) {
	var _v0 = _Utils_Tuple2(shell._.as, shell.ap);
	if ((!_v0.a.$) && (!_v0.b.$)) {
		var observed = _v0.a.a;
		var geometry = _v0.b.a;
		var rows = $author$project$ActionProjection$windows(observed.eN);
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
						return _Utils_eq(g.dD, row.dD) && _Utils_eq(g.b_, row.b_);
					},
					A2($author$project$GeometryProjection$window, row.aq, geometry)));
		};
		var sameAuthority = _Utils_eq(
			shell.dk,
			$elm$core$Maybe$Just(geometry.dk)) && (_Utils_eq(observed.P.fp, geometry.P.fp) && (_Utils_eq(observed.P.fe, geometry.P.fe) && (_Utils_eq(observed.P.y, geometry.P.y) && (_Utils_eq(
			$author$project$ActionProjection$focused(observed.eN),
			geometry.ci) && (_Utils_eq(
			$elm$core$List$length(rows),
			$elm$core$List$length(geometry.a)) && A2($elm$core$List$all, matching, rows))))));
		var focusedWorkspace = A2(
			$elm$core$Maybe$andThen,
			function ($) {
				return $.e$;
			},
			A2(
				$elm$core$Maybe$andThen,
				function (identity) {
					return A2($author$project$GeometryProjection$window, identity, geometry);
				},
				$author$project$ActionProjection$focused(observed.eN)));
		var families = A2(
			$elm$core$List$concatMap,
			function ($) {
				return $.aG;
			},
			$author$project$Taskbar$groups(observed.eN));
		var add = F2(
			function (family, accumulated) {
				var _v1 = A3($author$project$TaskView$membership, family.r, shell, geometry);
				if (!_v1.$) {
					var workspace = _v1.a;
					return (!positive(workspace)) ? accumulated : (A2(
						$elm$core$List$any,
						function (g) {
							return _Utils_eq(g.cU, workspace);
						},
						accumulated) ? A2(
						$elm$core$List$map,
						function (g) {
							return _Utils_eq(g.cU, workspace) ? _Utils_update(
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
								bt: _Utils_eq(
									focusedWorkspace,
									$elm$core$Maybe$Just(workspace)),
								cU: workspace,
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
								$elm$core$String$length(a.cU),
								a.cU),
							_Utils_Tuple2(
								$elm$core$String$length(b.cU),
								b.cU));
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
var $author$project$Notifications$identity = function (value) {
	return 'notification:' + ($author$project$UInt64$string(value.c7) + (':' + ($author$project$UInt64$string(value.aq) + (':' + (value.cb + (':' + value.e3))))));
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
	return value.aq;
};
var $author$project$Files$intent = F2(
	function (snapshot, target) {
		return {c2: snapshot.c2, c7: snapshot.c7, fR: target};
	});
var $author$project$JumpList$intent = F2(
	function (snapshot, action) {
		return {e3: action, d2: snapshot.d2, c2: snapshot.c2, c7: snapshot.c7};
	});
var $author$project$SystemMenu$intent = F3(
	function (snapshot, operation, value) {
		return {bh: operation, c2: snapshot.c2, c7: snapshot.c7, Y: value};
	});
var $author$project$MotionPreferences$label = function (override) {
	switch (override) {
		case 0:
			return 'Follow system';
		case 1:
			return 'Reduced motion';
		default:
			return 'Full motion';
	}
};
var $author$project$ShortcutPreferences$label = function (route) {
	switch (route) {
		case 'applications':
			return 'Apps menu';
		case 'system':
			return 'System menu';
		default:
			return 'Notification history';
	}
};
var $author$project$Notifications$live = F2(
	function (choice, model) {
		var _v0 = model.c;
		if (_v0.$ === 1) {
			return false;
		} else {
			var current = _v0.a;
			return current.dj && (_Utils_eq(current.c7, choice.c7) && ((!A2($elm$core$List$member, choice, model.ca)) && A2(
				$elm$core$List$any,
				function (row) {
					return _Utils_eq(row.cl, choice.cl) && (_Utils_eq(row.aq, choice.aq) && (_Utils_eq(row.ab, choice.ab) && ((row.dc === 'live') && (((choice.cb === 'dismiss') && (choice.e3 === '')) || ((choice.cb === 'invoke') && A2(
						$elm$core$List$any,
						function (action) {
							return _Utils_eq(action.a_, choice.e3);
						},
						row.cG))))));
				},
				current.af)));
		}
	});
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
			$author$project$MenuBridge$currentProvider(model.a.h)));
};
var $author$project$Menu$menuNumber = function (_v0) {
	var number = _v0;
	return number;
};
var $author$project$ShortcutPreferences$name = function (value) {
	switch (value) {
		case 0:
			return 'undecided';
		case 1:
			return 'keep';
		case 2:
			return 'default';
		default:
			return 'alternate';
	}
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
var $author$project$SystemMenu$name = function (operation) {
	switch (operation) {
		case 0:
			return 'Volume';
		case 1:
			return 'Mute';
		case 2:
			return 'Network';
		case 3:
			return 'Suspend';
		case 4:
			return 'Restart';
		case 5:
			return 'Shut down';
		case 6:
			return 'Lock session';
		default:
			return 'Log out';
	}
};
var $elm$core$Basics$negate = function (n) {
	return -n;
};
var $author$project$Motion$Reduced = 0;
var $author$project$Motion$Full = 1;
var $author$project$Motion$desired = function (model) {
	var _v0 = model.a1.c;
	if (_v0.$ === 1) {
		return 0;
	} else {
		var preference = _v0.a;
		var _v1 = preference.fy;
		switch (_v1) {
			case 1:
				return 0;
			case 2:
				return 1;
			default:
				return A2(
					$elm$core$Maybe$withDefault,
					0,
					A2(
						$elm$core$Maybe$map,
						function ($) {
							return $.aC;
						},
						model.bF));
		}
	}
};
var $author$project$MotionPreferences$selected = function (model) {
	return A2(
		$elm$core$Maybe$withDefault,
		0,
		A2(
			$elm$core$Maybe$map,
			function ($) {
				return $.fy;
			},
			model.c));
};
var $author$project$Motion$notice = function (model) {
	return _Utils_eq(model.a1.c, $elm$core$Maybe$Nothing) ? model.a1.ft : ((!_Utils_eq(model.ex, $elm$core$Maybe$Nothing)) ? 'Applying motion preference…' : (((!$author$project$Motion$desired(model)) ? 'Reduced motion: instant transitions' : 'Full motion') + (' · ' + $author$project$MotionPreferences$label(
		$author$project$MotionPreferences$selected(model.a1)))));
};
var $author$project$Snap$LeftHalf = 0;
var $author$project$GeometryProjection$Ordinary = 0;
var $author$project$Snap$proposal = function (choice) {
	return A2(
		$elm$core$Maybe$andThen,
		function (window) {
			var _v0 = _Utils_Tuple2(
				_Utils_Tuple2(window.cd, window.b$),
				_Utils_Tuple3(window.bi, window.cE, window.ce));
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
					var _v7 = choice.fN;
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
						P: choice.c.P,
						ap: geometry,
						b$: monitor,
						bi: output,
						cu: $author$project$Snap$identity(choice.fN),
						cE: area,
						ce: workspace
					});
			} else {
				return $elm$core$Maybe$Nothing;
			}
		},
		A2($author$project$GeometryProjection$window, choice.fR, choice.c));
};
var $author$project$Snap$open = F2(
	function (snapshot, target) {
		return A2(
			$elm$core$Maybe$andThen,
			function (window) {
				var choice = {fN: 0, c: snapshot, fR: target};
				return (snapshot.e6 || ((!window.dr) || (window.b_ || ((!(!window.es)) || ((!(!window.cg)) || _Utils_eq(
					$author$project$Snap$proposal(choice),
					$elm$core$Maybe$Nothing)))))) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(choice);
			},
			A2($author$project$GeometryProjection$window, target, snapshot));
	});
var $author$project$Switcher$phase = function (_v0) {
	var model = _v0;
	return model.j;
};
var $author$project$Transfer$propose = F3(
	function (snapshot, root, destination) {
		return A2(
			$elm$core$Maybe$andThen,
			function (w) {
				var _v0 = _Utils_Tuple2(w.e$, w.ce);
				if ((!_v0.a.$) && (!_v0.b.$)) {
					var source = _v0.a.a;
					var generation = _v0.b.a;
					return (snapshot.e6 || ((!_Utils_eq(w.dD, $elm$core$Maybe$Nothing)) || (w.bB || ((!($author$project$Transfer$ordinary(source) && $author$project$Transfer$ordinary(destination))) || _Utils_eq(source, destination))))) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(
						{bx: destination, cv: source, da: generation});
				} else {
					return $elm$core$Maybe$Nothing;
				}
			},
			A2($author$project$GeometryProjection$window, root, snapshot));
	});
var $author$project$ShortcutPreferences$allowed = F2(
	function (selected, observed) {
		switch (selected) {
			case 1:
				return true;
			case 2:
				return observed.dp;
			case 3:
				return observed.dh;
			default:
				return false;
		}
	});
var $author$project$ShortcutPreferences$writable = function (model) {
	return (!_Utils_eq(model.c, $elm$core$Maybe$Nothing)) && ((!_Utils_eq(model.cV, $elm$core$Maybe$Nothing)) && _Utils_eq(model.ex, $elm$core$Maybe$Nothing));
};
var $author$project$ShortcutPreferences$ready = function (model) {
	return $author$project$ShortcutPreferences$writable(model) && A2(
		$elm$core$Maybe$withDefault,
		false,
		A2(
			$elm$core$Maybe$map,
			function (inventory) {
				return A2(
					$elm$core$List$all,
					function (route) {
						return A2(
							$author$project$ShortcutPreferences$allowed,
							A2($author$project$ShortcutPreferences$choices, route, model.fb),
							A2($author$project$ShortcutPreferences$row, route, inventory));
					},
					_List_fromArray(
						['applications', 'system', 'notifications']));
			},
			model.cV));
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
					entry.dA,
					A2($elm$core$List$cons, entry.d9, entry.ei)));
			var name = $author$project$SearchFold$fold(entry.dA);
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
						$author$project$Catalog$id(a.cU),
						$author$project$Catalog$id(b.cU));
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
		A2($elm$core$List$drop, model.fN, model.af));
};
var $elm$core$List$singleton = function (value) {
	return _List_fromArray(
		[value]);
};
var $author$project$Launch$status = function (_v0) {
	var model = _v0;
	var _v1 = model.j;
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
var $elm$core$String$any = _String_any;
var $author$project$Files$textValid = function (value) {
	return ($elm$core$String$length(value) <= 512) && (!A2(
		$elm$core$String$any,
		function (c) {
			return ($elm$core$Char$toCode(c) < 32) || ($elm$core$Char$toCode(c) === 127);
		},
		value));
};
var $author$project$Files$validTarget = function (value) {
	return $author$project$Files$textValid(value) && ((value === 'home') || (A2(
		$elm$core$List$any,
		function (_v0) {
			var collection = _v0.a;
			return _Utils_eq(value, 'coll:' + collection);
		},
		$author$project$Files$collections) || (A2(
		$elm$core$String$startsWith,
		'/',
		$elm$core$String$trim(value)) || ((value === '~') || A2($elm$core$String$startsWith, '~/', value)))));
};
var $author$project$Files$supported = F2(
	function (value, model) {
		return _Utils_eq(model.ex, $elm$core$Maybe$Nothing) && ($author$project$Files$validTarget(value.fR) && ((!A2($elm$core$List$member, value, model.ca)) && A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (snapshot) {
					return snapshot.dj && (_Utils_eq(value.c7, snapshot.c7) && _Utils_eq(value.c2, snapshot.c2));
				},
				model.c))));
	});
var $author$project$JumpList$supported = F2(
	function (value, model) {
		return _Utils_eq(model.ex, $elm$core$Maybe$Nothing) && ((!A2($elm$core$List$member, value, model.ca)) && A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (snapshot) {
					return snapshot.dj && (_Utils_eq(snapshot.c7, value.c7) && (_Utils_eq(snapshot.c2, value.c2) && (_Utils_eq(snapshot.d2, value.d2) && A2(
						$elm$core$List$any,
						function (row) {
							return _Utils_eq(row.cl, value.e3);
						},
						snapshot.cG))));
				},
				model.c)));
	});
var $elm$core$Basics$ge = _Utils_ge;
var $author$project$SystemMenu$supported = F2(
	function (value, model) {
		var _v0 = model.c;
		if (_v0.$ === 1) {
			return false;
		} else {
			var current = _v0.a;
			return _Utils_eq(value.c7, current.c7) && (_Utils_eq(value.c2, current.c2) && ((!A2($elm$core$List$member, value, model.ca)) && function () {
				var _v1 = value.bh;
				switch (_v1) {
					case 0:
						return A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (v) {
									return (value.Y >= 0) && ((value.Y <= 100) && (!_Utils_eq(value.Y, v.fz)));
								},
								current.fV));
					case 1:
						return A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (v) {
									return A2(
										$elm$core$List$member,
										value.Y,
										_List_fromArray(
											[0, 1])) && (!_Utils_eq(value.Y === 1, v.dz));
								},
								current.fV));
					case 2:
						return A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (v) {
									return A2(
										$elm$core$List$member,
										v.fA,
										_List_fromArray(
											['yes', 'auth'])) && (A2(
										$elm$core$List$member,
										value.Y,
										_List_fromArray(
											[0, 1])) && (!_Utils_eq(value.Y === 1, v.fd)));
								},
								current.fs));
					case 3:
						return A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (v) {
									return A2(
										$elm$core$List$member,
										v.fQ,
										_List_fromArray(
											['yes', 'challenge'])) && (!value.Y);
								},
								current.fE));
					case 4:
						return A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (v) {
									return A2(
										$elm$core$List$member,
										v.fH,
										_List_fromArray(
											['yes', 'challenge'])) && (!value.Y);
								},
								current.fE));
					case 5:
						return A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (v) {
									return A2(
										$elm$core$List$member,
										v.fF,
										_List_fromArray(
											['yes', 'challenge'])) && (!value.Y);
								},
								current.fE));
					case 6:
						return A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (v) {
									return (!v.fq) && (!value.Y);
								},
								current.fO));
					default:
						return A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (v) {
									return (v.dc !== 'closing') && (!value.Y);
								},
								current.fO));
				}
			}()));
		}
	});
var $author$project$Switcher$Waiting = 1;
var $author$project$Desktop$switcherOpen = function (model) {
	return A2(
		$elm$core$List$member,
		$author$project$Switcher$phase(model.i),
		_List_fromArray(
			[1, 2]));
};
var $author$project$Notifications$target = F4(
	function (snapshot, entry, verb, action) {
		return {e3: action, cl: entry.cl, aq: entry.aq, ab: entry.ab, c7: snapshot.c7, cb: verb};
	});
var $author$project$Settings$themeName = function (theme) {
	switch (theme) {
		case 0:
			return 'night';
		case 1:
			return 'dawn';
		default:
			return 'high-contrast';
	}
};
var $author$project$Launch$Acknowledgement = $elm$core$Basics$identity;
var $author$project$Launch$uncertain = function (_v0) {
	var model = _v0;
	var _v1 = model.j;
	if ((_v1.$ === 2) && (_v1.b === 2)) {
		var intent = _v1.a;
		var _v2 = _v1.b;
		return $elm$core$Maybe$Just(intent);
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$MotionPreferences$writable = function (model) {
	return (!_Utils_eq(model.c, $elm$core$Maybe$Nothing)) && _Utils_eq(model.ex, $elm$core$Maybe$Nothing);
};
var $author$project$Pins$writable = function (model) {
	return (!_Utils_eq(model.c, $elm$core$Maybe$Nothing)) && _Utils_eq(model.ex, $elm$core$Maybe$Nothing);
};
var $author$project$Settings$writable = function (model) {
	return (!_Utils_eq(model.c, $elm$core$Maybe$Nothing)) && _Utils_eq(model.ex, $elm$core$Maybe$Nothing);
};
var $author$project$Surface$controls = function (model) {
	if (!_Utils_eq(model.o, $elm$core$Maybe$Nothing)) {
		var scoped = function (message) {
			return A2(
				$elm$core$Maybe$map,
				message,
				$author$project$Desktop$capture(model));
		};
		var current = A2(
			$elm$core$Maybe$andThen,
			function (snapshot) {
				return _Utils_eq(
					$elm$core$Maybe$Just(snapshot.d2),
					model.o) ? $elm$core$Maybe$Just(snapshot) : $elm$core$Maybe$Nothing;
			},
			model.ar.c);
		var title = A2(
			$elm$core$Maybe$withDefault,
			'Application actions',
			A2(
				$elm$core$Maybe$map,
				function (snapshot) {
					return 'Actions for ' + snapshot.dA;
				},
				current));
		var control = F5(
			function (identity, label, detail, enabled, message) {
				return {
					f: label,
					e: detail,
					g: A2(
						$author$project$Desktop$key,
						model,
						(identity === 'control:close') ? 'jump:close' : identity),
					fd: enabled,
					cl: identity,
					el: label,
					aJ: enabled ? scoped(message) : $elm$core$Maybe$Nothing
				};
			});
		var row = F2(
			function (snapshot, action) {
				var intent = A2($author$project$JumpList$intent, snapshot, action.cl);
				return A5(
					control,
					'jump:action:' + action.cl,
					action.el,
					(action.ej === 'recent') ? 'Recent file' : 'Application action',
					_Utils_eq(model.aZ, $elm$core$Maybe$Nothing) && A2($author$project$JumpList$supported, intent, model.ar),
					function (stamp) {
						return A2($author$project$Desktop$JumpAction, stamp, intent);
					});
			});
		var entries = A2(
			$elm$core$Maybe$withDefault,
			_List_Nil,
			A2(
				$elm$core$Maybe$map,
				function (snapshot) {
					return A2(
						$elm$core$List$map,
						row(snapshot),
						snapshot.cG);
				},
				current));
		return _Utils_ap(
			_List_fromArray(
				[
					A5(control, 'control:close', 'Close application actions', '', true, $author$project$Desktop$CloseJumpList),
					A5(
					control,
					'jump:refresh',
					'Refresh application actions',
					'Read actions; never repeat a request',
					_Utils_eq(model.aZ, $elm$core$Maybe$Nothing),
					$author$project$Desktop$RefreshJumpList),
					A5(control, 'jump:title:state', title, '', false, $author$project$Desktop$CloseJumpList)
				]),
			_Utils_ap(
				entries,
				($elm$core$List$isEmpty(entries) && _Utils_eq(model.aZ, $elm$core$Maybe$Nothing)) ? _List_fromArray(
					[
						A5(control, 'jump:empty:state', 'No supported actions or recent files.', '', false, $author$project$Desktop$CloseJumpList)
					]) : _List_Nil));
	} else {
		if (model.p) {
			var scoped = function (message) {
				return A2(
					$elm$core$Maybe$map,
					message,
					$author$project$Desktop$capture(model));
			};
			var ready = function (target) {
				return _Utils_eq(model.aW, $elm$core$Maybe$Nothing) && A2(
					$elm$core$Maybe$withDefault,
					false,
					A2(
						$elm$core$Maybe$map,
						function (snapshot) {
							return A2(
								$author$project$Files$supported,
								A2($author$project$Files$intent, snapshot, target),
								model.T);
						},
						model.T.c));
			};
			var openTarget = F2(
				function (target, stamp) {
					return A2(
						$elm$core$Maybe$withDefault,
						$author$project$Desktop$CloseFiles(stamp),
						A2(
							$elm$core$Maybe$map,
							function (snapshot) {
								return A2(
									$author$project$Desktop$OpenFilesTarget,
									stamp,
									A2($author$project$Files$intent, snapshot, target));
							},
							model.T.c));
				});
			var location = A2(
				$elm$core$Maybe$withDefault,
				'No Files window observed.',
				A2(
					$elm$core$Maybe$map,
					function (peer) {
						return 'Current location: ' + peer.fR;
					},
					A2(
						$elm$core$Maybe$andThen,
						function ($) {
							return $.b2;
						},
						model.T.c)));
			var control = F5(
				function (identity, label, detail, enabled, message) {
					return {
						f: label,
						e: detail,
						g: A2(
							$author$project$Desktop$key,
							model,
							(identity === 'control:close') ? 'files:close' : identity),
						fd: enabled,
						cl: identity,
						el: label,
						aJ: enabled ? scoped(message) : $elm$core$Maybe$Nothing
					};
				});
			var collection = function (_v0) {
				var identifier = _v0.a;
				var label = _v0.b;
				return A5(
					control,
					'files:collection:' + identifier,
					label,
					'',
					ready('coll:' + identifier),
					openTarget('coll:' + identifier));
			};
			return _Utils_ap(
				_List_fromArray(
					[
						A5(control, 'control:close', 'Close Files menu', '', true, $author$project$Desktop$CloseFiles),
						A5(
						control,
						'files:refresh',
						'Refresh Files state',
						'Read location; never repeat an opening',
						_Utils_eq(model.aW, $elm$core$Maybe$Nothing),
						$author$project$Desktop$RefreshFiles),
						A5(control, 'files:location:state', location, '', false, $author$project$Desktop$CloseFiles),
						A5(
						control,
						'files:home',
						'Home',
						'',
						ready('home'),
						openTarget('home'))
					]),
				_Utils_ap(
					A2($elm$core$List$map, collection, $author$project$Files$collections),
					_List_fromArray(
						[
							{
							f: 'Folder path',
							e: '',
							g: A2($author$project$Desktop$key, model, 'files:path'),
							fd: true,
							cl: 'control:files-path',
							el: model.T.fb,
							aJ: scoped(
								function (stamp) {
									return A2($author$project$Desktop$EditFilesPath, stamp, model.T.fb);
								})
						},
							A5(
							control,
							'files:open-path',
							'Open folder',
							'Open this path in Files',
							ready(model.T.fb),
							$author$project$Desktop$OpenFilesPath)
						])));
		} else {
			if (model.v) {
				var scoped = function (action) {
					return A2(
						$elm$core$Maybe$map,
						action,
						$author$project$Desktop$capture(model));
				};
				var control = F5(
					function (identity, label, detail, enabled, message) {
						return {
							f: label,
							e: detail,
							g: A2(
								$author$project$Desktop$key,
								model,
								(identity === 'control:close') ? 'system:close' : identity),
							fd: enabled,
							cl: identity,
							el: label,
							aJ: enabled ? scoped(message) : $elm$core$Maybe$Nothing
						};
					});
				var state = F2(
					function (section, value) {
						return A5(control, 'system:' + (section + ':state'), value, '', false, $author$project$Desktop$CloseSystemMenu);
					});
				var rows = function (snapshot) {
					var change = F3(
						function (operation, value, label) {
							var intent = A3($author$project$SystemMenu$intent, snapshot, operation, value);
							var ready = _Utils_eq(model.ak.ex, $elm$core$Maybe$Nothing) && (_Utils_eq(model.aT, $elm$core$Maybe$Nothing) && (_Utils_eq(model.s, $elm$core$Maybe$Nothing) && A2($author$project$SystemMenu$supported, intent, model.ak)));
							return A5(
								control,
								'system:' + ($author$project$SystemMenu$code(operation) + (':' + $elm$core$String$fromInt(value))),
								label,
								'',
								ready,
								function (stamp) {
									return A2($author$project$Desktop$SystemChange, stamp, intent);
								});
						});
					var network = function () {
						var _v5 = snapshot.fs;
						if (_v5.$ === 1) {
							return _List_fromArray(
								[
									A2(state, 'network', 'Network unavailable')
								]);
						} else {
							var current = _v5.a;
							return _List_fromArray(
								[
									A2(
									state,
									'network',
									'Network ' + ((current.fd ? 'enabled' : 'disabled') + (' · ' + (current.dc + ((current.fA === 'no') ? '; changes unavailable' : ''))))),
									A3(
									change,
									2,
									current.fd ? 0 : 1,
									current.fd ? 'Disable networking' : 'Enable networking')
								]);
						}
					}();
					var session = function () {
						var _v4 = snapshot.fO;
						if (_v4.$ === 1) {
							return _List_fromArray(
								[
									A2(state, 'session', 'Session controls unavailable')
								]);
						} else {
							var current = _v4.a;
							return _List_fromArray(
								[
									A2(
									state,
									'session',
									'Session ' + (current.dA + (' · ' + (current.dc + (current.fq ? '; locked' : '; unlocked'))))),
									A3(change, 6, 0, 'Lock session'),
									A3(change, 7, 0, 'Log out')
								]);
						}
					}();
					var volume = function () {
						var _v3 = snapshot.fV;
						if (_v3.$ === 1) {
							return _List_fromArray(
								[
									A2(state, 'volume', 'Volume unavailable')
								]);
						} else {
							var current = _v3.a;
							return A2(
								$elm$core$List$cons,
								A2(
									state,
									'volume',
									'Volume ' + ($elm$core$String$fromInt(current.fz) + ('%' + ((current.dz ? '; muted' : '; unmuted') + (' · ' + current.el))))),
								_Utils_ap(
									A2(
										$elm$core$List$map,
										function (percent) {
											return A3(
												change,
												0,
												percent,
												'Set volume ' + ($elm$core$String$fromInt(percent) + '%'));
										},
										_List_fromArray(
											[0, 25, 50, 75, 100])),
									_List_fromArray(
										[
											A3(
											change,
											1,
											current.dz ? 0 : 1,
											current.dz ? 'Unmute' : 'Mute')
										])));
						}
					}();
					var capability = function (value) {
						return (value === 'yes') ? 'available' : ((value === 'challenge') ? 'authorization required' : 'unavailable');
					};
					var power = function () {
						var _v2 = snapshot.fE;
						if (_v2.$ === 1) {
							return _List_fromArray(
								[
									A2(state, 'power', 'Power controls unavailable')
								]);
						} else {
							var current = _v2.a;
							return _List_fromArray(
								[
									A2(
									state,
									'power',
									'Power · suspend ' + (capability(current.fQ) + (', restart ' + (capability(current.fH) + (', shutdown ' + capability(current.fF)))))),
									A3(change, 3, 0, 'Suspend'),
									A3(change, 4, 0, 'Restart'),
									A3(change, 5, 0, 'Shut down')
								]);
						}
					}();
					return _Utils_ap(
						volume,
						_Utils_ap(
							network,
							_Utils_ap(power, session)));
				};
				var confirmation = function () {
					var _v1 = model.s;
					if (_v1.$ === 1) {
						return _List_Nil;
					} else {
						var intent = _v1.a;
						return _List_fromArray(
							[
								A2(
								state,
								'confirmation',
								'Confirm ' + ($author$project$SystemMenu$name(intent.bh) + '? Unsaved work or active connections may be affected.')),
								A5(control, 'system:cancel', 'Cancel system change', '', true, $author$project$Desktop$CancelSystemChange),
								A5(
								control,
								'system:confirm',
								'Confirm ' + $author$project$SystemMenu$name(intent.bh),
								'',
								A2($author$project$SystemMenu$supported, intent, model.ak) && (_Utils_eq(model.ak.ex, $elm$core$Maybe$Nothing) && _Utils_eq(model.aT, $elm$core$Maybe$Nothing)),
								function (stamp) {
									return A2($author$project$Desktop$ConfirmSystemChange, stamp, intent);
								})
							]);
					}
				}();
				return _Utils_ap(
					_List_fromArray(
						[
							A5(control, 'control:close', 'Close system menu', '', true, $author$project$Desktop$CloseSystemMenu),
							A5(
							control,
							'system:refresh',
							'Refresh system state',
							'Read current state; never repeat a change',
							_Utils_eq(model.aT, $elm$core$Maybe$Nothing),
							$author$project$Desktop$RefreshSystemMenu)
						]),
					_Utils_ap(
						A2(
							$elm$core$Maybe$withDefault,
							_List_Nil,
							A2($elm$core$Maybe$map, rows, model.ak.c)),
						confirmation));
			} else {
				if (model.t) {
					var scoped = function (message) {
						return A2(
							$elm$core$Maybe$map,
							message,
							$author$project$Desktop$capture(model));
					};
					var control = F5(
						function (identity, label, detail, enabled, message) {
							return {
								f: label,
								e: detail,
								g: A2(
									$author$project$Desktop$key,
									model,
									(identity === 'control:close') ? 'notifications:close' : identity),
								fd: enabled,
								cl: identity,
								el: label,
								aJ: enabled ? scoped(message) : $elm$core$Maybe$Nothing
							};
						});
					var clean = function (value) {
						return A2(
							$elm$core$String$join,
							' ',
							$elm$core$String$words(value));
					};
					var entryRows = F2(
						function (snapshot, entry) {
							var textRow = F3(
								function (identity, label, detail) {
									return {
										f: clean(label),
										e: detail,
										g: A2($author$project$Desktop$key, model, identity),
										fd: false,
										cl: identity,
										el: clean(label),
										aJ: $elm$core$Maybe$Nothing
									};
								});
							var prefix = 'notification:' + ($author$project$UInt64$string(snapshot.c7) + (':' + $author$project$UInt64$string(entry.aq)));
							var action = F3(
								function (verb, key, label) {
									var target = A4($author$project$Notifications$target, snapshot, entry, verb, key);
									var ready = A2($author$project$Notifications$live, target, model.C) && (_Utils_eq(model.C.ex, $elm$core$Maybe$Nothing) && _Utils_eq(model.a0, $elm$core$Maybe$Nothing));
									return A5(
										control,
										$author$project$Notifications$identity(target),
										clean(label),
										'',
										ready,
										function (stamp) {
											return A2($author$project$Desktop$NotificationAction, stamp, target);
										});
								});
							return _Utils_ap(
								_List_fromArray(
									[
										A3(
										textRow,
										prefix + ':summary',
										entry.dR + (': ' + entry.eS),
										(entry.dc === 'live') ? 'Live' : ('History · ' + entry.dc))
									]),
								_Utils_ap(
									$elm$core$String$isEmpty(entry.dU) ? _List_Nil : _List_fromArray(
										[
											A3(textRow, prefix + ':body', entry.dU, '')
										]),
									(entry.dc === 'live') ? _Utils_ap(
										A2(
											$elm$core$List$map,
											function (item) {
												return A3(action, 'invoke', item.a_, item.el);
											},
											entry.cG),
										_List_fromArray(
											[
												A3(action, 'dismiss', '', 'Dismiss notification')
											])) : A2(
										$elm$core$Maybe$withDefault,
										_List_Nil,
										A2(
											$elm$core$Maybe$andThen,
											function (selected) {
												return (_Utils_eq(selected.fR.c7, snapshot.c7) && (_Utils_eq(selected.fR.cl, entry.cl) && (_Utils_eq(selected.fR.aq, entry.aq) && _Utils_eq(selected.fR.ab, entry.ab)))) ? $elm$core$Maybe$Just(
													_List_fromArray(
														[
															{
															f: selected.el + '; unavailable',
															e: entry.dc + ' · Action unavailable',
															g: A2(
																$author$project$Desktop$key,
																model,
																$author$project$Notifications$identity(selected.fR)),
															fd: false,
															cl: $author$project$Notifications$identity(selected.fR),
															el: selected.el,
															aJ: $elm$core$Maybe$Nothing
														}
														])) : $elm$core$Maybe$Nothing;
											},
											model.C.ci))));
						});
					var retained = A2(
						$elm$core$Maybe$withDefault,
						_List_Nil,
						A2(
							$elm$core$Maybe$andThen,
							function (selected) {
								return A2(
									$elm$core$Maybe$map,
									function (snapshot) {
										var state = A2(
											$elm$core$Maybe$withDefault,
											'unavailable',
											A2(
												$elm$core$Maybe$map,
												function ($) {
													return $.dc;
												},
												$elm$core$List$head(
													A2(
														$elm$core$List$filter,
														function (entry) {
															return _Utils_eq(entry.cl, selected.fR.cl) && (_Utils_eq(entry.aq, selected.fR.aq) && _Utils_eq(entry.ab, selected.fR.ab));
														},
														snapshot.af))));
										var exists = A2(
											$elm$core$List$any,
											function (row) {
												return _Utils_eq(
													row.cl,
													$author$project$Notifications$identity(selected.fR));
											},
											A2(
												$elm$core$List$concatMap,
												entryRows(snapshot),
												snapshot.af));
										return exists ? _List_Nil : _List_fromArray(
											[
												{
												f: selected.el + '; unavailable',
												e: state + ' · Action unavailable',
												g: A2(
													$author$project$Desktop$key,
													model,
													$author$project$Notifications$identity(selected.fR)),
												fd: false,
												cl: $author$project$Notifications$identity(selected.fR),
												el: selected.el,
												aJ: $elm$core$Maybe$Nothing
											}
											]);
									},
									model.C.c);
							},
							model.C.ci));
					return _Utils_ap(
						_List_fromArray(
							[
								A5(control, 'control:close', 'Close notifications', '', true, $author$project$Desktop$CloseNotifications),
								A5(
								control,
								'notifications:refresh',
								'Refresh notifications',
								(!_Utils_eq(model.a0, $elm$core$Maybe$Nothing)) ? 'Reading current targets…' : 'Read current targets; no action is repeated',
								true,
								$author$project$Desktop$RefreshNotifications)
							]),
						_Utils_ap(
							_List_fromArray(
								[
									A5(
									control,
									'notifications:dnd',
									'Do not disturb for this session',
									model.C.fD.cP ? 'On · History still updates' : 'Off',
									true,
									function (stamp) {
										return A2(
											$author$project$Desktop$ConfigureNotificationPolicy,
											stamp,
											{cP: !model.C.fD.cP, ef: model.C.fD.ef});
									}),
									A5(
									control,
									'notifications:critical-interrupt',
									'Allow critical notification interruptions for this session',
									model.C.fD.ef ? 'On · Only when Do not disturb is off' : 'Off · New notifications are polite',
									true,
									function (stamp) {
										return A2(
											$author$project$Desktop$ConfigureNotificationPolicy,
											stamp,
											{cP: model.C.fD.cP, ef: !model.C.fD.ef});
									})
								]),
							_Utils_ap(
								A2(
									$elm$core$Maybe$withDefault,
									_List_Nil,
									A2(
										$elm$core$Maybe$map,
										function (snapshot) {
											return A2(
												$elm$core$List$concatMap,
												entryRows(snapshot),
												snapshot.af);
										},
										model.C.c)),
								retained)));
				} else {
					if (model.n) {
						var shortcutReady = $author$project$ShortcutPreferences$writable(model.ac) && _Utils_eq(model.aQ, $elm$core$Maybe$Nothing);
						var scoped = function (message) {
							return A2(
								$elm$core$Maybe$map,
								message,
								$author$project$Desktop$capture(model));
						};
						var ready = $author$project$Settings$writable(model.aj) && _Utils_eq(model.bo, $elm$core$Maybe$Nothing);
						var motionReady = $author$project$MotionPreferences$writable(model.I.a1) && _Utils_eq(model.aK, $elm$core$Maybe$Nothing);
						var draft = model.aj.fb;
						var control = F5(
							function (identity, label, detail, enabled, message) {
								return {
									f: label,
									e: detail,
									g: A2(
										$author$project$Desktop$key,
										model,
										(identity === 'control:close') ? 'settings:close' : identity),
									fd: enabled,
									cl: identity,
									el: label,
									aJ: enabled ? scoped(message) : $elm$core$Maybe$Nothing
								};
							});
						var guidance = (!model.c8) ? _List_Nil : _List_fromArray(
							[
								A5(control, 'settings:help:text:keyboard', 'Keyboard navigation', 'Tab and Shift+Tab move focus. Arrows move through lists; Home/End reach endpoints. Enter chooses; Escape closes.', false, $author$project$Desktop$ToggleSettingsHelp),
								A5(control, 'settings:help:text:preferences', 'Keeping your preferences', 'Save applies appearance preferences. Motion has its own Save. Dismissing help keeps unsaved edits.', false, $author$project$Desktop$ToggleSettingsHelp),
								A5(control, 'settings:help:text:recovery', 'When an action is not confirmed', 'Pending is waiting; Refused did not proceed; Unknown is unconfirmed. Refresh reads state without repeating an action.', false, $author$project$Desktop$ToggleSettingsHelp)
							]);
						var motionOption = function (selected) {
							return A5(
								control,
								'settings:motion:' + function () {
									switch (selected) {
										case 0:
											return 'system';
										case 1:
											return 'reduced';
										default:
											return 'full';
									}
								}(),
								$author$project$MotionPreferences$label(selected),
								_Utils_eq(model.I.a1.fb, selected) ? 'Selected' : '',
								motionReady,
								function (stamp) {
									return A2($author$project$Desktop$EditMotionPreference, stamp, selected);
								});
						};
						var scale = function (percent) {
							return A5(
								control,
								'settings:scale:' + $elm$core$String$fromInt(percent),
								'Text size ' + ($elm$core$String$fromInt(percent) + '%'),
								_Utils_eq(model.aj.fb.cy, percent) ? 'Selected' : '',
								ready,
								function (stamp) {
									return A2(
										$author$project$Desktop$EditSettings,
										stamp,
										_Utils_update(
											draft,
											{cy: percent}));
								});
						};
						var shortcutRoute = function (route) {
							var option = F3(
								function (selected, suffix, enabled) {
									return A5(
										control,
										'settings:shortcuts:' + (route + (':' + $author$project$ShortcutPreferences$name(selected))),
										suffix,
										_Utils_eq(
											A2($author$project$ShortcutPreferences$choices, route, model.ac.fb),
											selected) ? 'Selected' : '',
										shortcutReady && enabled,
										function (stamp) {
											return A3($author$project$Desktop$EditShortcutChoice, stamp, route, selected);
										});
								});
							var observed = A2(
								$elm$core$Maybe$map,
								$author$project$ShortcutPreferences$row(route),
								model.ac.cV);
							var label = $author$project$ShortcutPreferences$label(route);
							var state = A2(
								$elm$core$Maybe$withDefault,
								label + ': live bindings unavailable',
								A2(
									$elm$core$Maybe$map,
									function (row) {
										return label + (': ' + ((row.bt === 1) ? 'existing shortcut preserved' : ((row.bt === 2) ? row.e9 : row.e4)));
									},
									observed));
							return _List_fromArray(
								[
									A5(control, 'settings:shortcuts:' + (route + ':state'), state, '', false, $author$project$Desktop$RefreshShortcutChoices),
									A3(option, 1, 'Keep existing shortcut for ' + label, true),
									A3(
									option,
									2,
									'Use ' + (label + ' default'),
									A2(
										$elm$core$Maybe$withDefault,
										false,
										A2(
											$elm$core$Maybe$map,
											function ($) {
												return $.dp;
											},
											observed))),
									A5(
									control,
									'settings:shortcuts:' + (route + ':default:state'),
									A2(
										$elm$core$Maybe$withDefault,
										'Default unavailable',
										A2(
											$elm$core$Maybe$map,
											function (row) {
												return _Utils_ap(
													row.e9,
													row.dp ? ' · Available' : ' · Unavailable: existing binding');
											},
											observed)),
									'',
									false,
									$author$project$Desktop$RefreshShortcutChoices),
									A3(
									option,
									3,
									'Use ' + (label + ' alternative'),
									A2(
										$elm$core$Maybe$withDefault,
										false,
										A2(
											$elm$core$Maybe$map,
											function ($) {
												return $.dh;
											},
											observed))),
									A5(
									control,
									'settings:shortcuts:' + (route + ':alternate:state'),
									A2(
										$elm$core$Maybe$withDefault,
										'Alternative unavailable',
										A2(
											$elm$core$Maybe$map,
											function (row) {
												return _Utils_ap(
													row.e4,
													row.dh ? ' · Available' : ' · Unavailable: existing binding');
											},
											observed)),
									'',
									false,
									$author$project$Desktop$RefreshShortcutChoices)
								]);
						};
						var shortcutControls = A2(
							$elm$core$List$cons,
							A5(control, 'settings:shortcuts:notice:state', model.ac.ft, '', false, $author$project$Desktop$RefreshShortcutChoices),
							_Utils_ap(
								A2(
									$elm$core$List$concatMap,
									shortcutRoute,
									_List_fromArray(
										['applications', 'system', 'notifications'])),
								_List_fromArray(
									[
										A5(
										control,
										'settings:shortcuts:save',
										'Save shortcut choices',
										'Apply only the free chosen chords; preserve existing bindings',
										_Utils_eq(model.aQ, $elm$core$Maybe$Nothing) && ($author$project$ShortcutPreferences$ready(model.ac) && $author$project$ShortcutPreferences$changed(model.ac)),
										$author$project$Desktop$SaveShortcutChoices),
										A5(
										control,
										'settings:shortcuts:refresh',
										'Refresh shortcut choices',
										'Read stored choices and live bindings without repeating an action',
										_Utils_eq(model.aQ, $elm$core$Maybe$Nothing),
										$author$project$Desktop$RefreshShortcutChoices)
									])));
						var theme = F2(
							function (selected, label) {
								return A5(
									control,
									'settings:theme:' + $author$project$Settings$themeName(selected),
									label,
									_Utils_eq(model.aj.fb.de, selected) ? 'Selected' : '',
									ready,
									function (stamp) {
										return A2(
											$author$project$Desktop$EditSettings,
											stamp,
											_Utils_update(
												draft,
												{de: selected}));
									});
							});
						var changed = A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (current) {
									return !_Utils_eq(current.bs, model.aj.fb);
								},
								model.aj.c));
						return _Utils_ap(
							_List_fromArray(
								[
									A5(control, 'control:close', 'Close settings', '', true, $author$project$Desktop$CloseSettings),
									A5(
									control,
									'settings:help',
									model.c8 ? 'Dismiss help' : 'Show help',
									model.c8 ? 'Expanded' : 'Collapsed',
									true,
									$author$project$Desktop$ToggleSettingsHelp)
								]),
							_Utils_ap(
								guidance,
								_Utils_ap(
									_List_fromArray(
										[
											A5(
											control,
											'settings:effects-off',
											'Disable soft effects',
											draft.cQ ? 'On' : 'Off',
											ready,
											function (stamp) {
												return A2(
													$author$project$Desktop$EditSettings,
													stamp,
													_Utils_update(
														draft,
														{cQ: !draft.cQ}));
											}),
											A5(
											control,
											'settings:reduced-transparency',
											'Reduce transparency',
											draft.c$ ? 'On' : 'Off',
											ready,
											function (stamp) {
												return A2(
													$author$project$Desktop$EditSettings,
													stamp,
													_Utils_update(
														draft,
														{c$: !draft.c$}));
											})
										]),
									_Utils_ap(
										_List_fromArray(
											[
												A5(
												control,
												'settings:motion',
												$author$project$Motion$notice(model.I),
												model.I.a1.ft,
												false,
												$author$project$Desktop$RefreshMotionPreference),
												motionOption(0),
												motionOption(1),
												motionOption(2),
												A5(
												control,
												'settings:motion:save',
												'Save motion preference',
												'Apply and keep across restart',
												motionReady && (!_Utils_eq(
													model.I.a1.fb,
													$author$project$MotionPreferences$selected(model.I.a1))),
												$author$project$Desktop$SaveMotionPreference),
												A5(
												control,
												'settings:motion:refresh',
												'Refresh motion preference',
												'Read stored preference; no write is repeated',
												_Utils_eq(model.aK, $elm$core$Maybe$Nothing),
												$author$project$Desktop$RefreshMotionPreference),
												A2(theme, 0, 'Night theme'),
												A2(theme, 1, 'Dawn theme'),
												A2(theme, 2, 'High contrast theme')
											]),
										_Utils_ap(
											A2(
												$elm$core$List$map,
												scale,
												_List_fromArray(
													[100, 125, 150, 200])),
											_Utils_ap(
												_List_fromArray(
													[
														A5(control, 'settings:save', 'Save settings', 'Apply and keep across restart', ready && changed, $author$project$Desktop$SaveSettings),
														A5(
														control,
														'settings:refresh',
														'Refresh settings',
														'Read stored values; discard unsaved changes',
														_Utils_eq(model.bo, $elm$core$Maybe$Nothing),
														$author$project$Desktop$RefreshSettings)
													]),
												shortcutControls))))));
					} else {
						if (!_Utils_eq(model.x, $elm$core$Maybe$Nothing)) {
							var _v7 = model.x;
							if (_v7.$ === 1) {
								return _List_Nil;
							} else {
								var choice = _v7.a;
								var scoped = function (message) {
									return A2(
										$elm$core$Maybe$map,
										message,
										$author$project$Desktop$capture(model));
								};
								var ready = $author$project$Shell$available(model.a.b);
								var regionControl = function (region) {
									var selected = _Utils_eq(region, choice.fN);
									var identity = 'snap:region:' + $author$project$Snap$identity(region);
									return {
										f: _Utils_ap(
											$author$project$Snap$name(region),
											selected ? '; selected preview' : ''),
										e: selected ? 'Selected' : '',
										g: A2($author$project$Desktop$key, model, identity),
										fd: ready,
										cl: identity,
										el: $author$project$Snap$name(region),
										aJ: ready ? scoped(
											function (stamp) {
												return A2($author$project$Desktop$SelectSnap, stamp, region);
											}) : $elm$core$Maybe$Nothing
									};
								};
								var placement = $author$project$Snap$proposal(choice);
								var applyReady = ready && (_Utils_eq(model.k, $elm$core$Maybe$Nothing) && (A2(
									$elm$core$Maybe$withDefault,
									false,
									A2(
										$elm$core$Maybe$map,
										function (caps) {
											return A2($elm$core$List$member, 'snap', caps.ev);
										},
										model.a.b.ds)) && (!_Utils_eq(placement, $elm$core$Maybe$Nothing))));
								var applyLabel = applyReady ? ('Snap to ' + $elm$core$String$toLower(
									$author$project$Snap$name(choice.fN))) : 'Snapping unavailable';
								return A2(
									$elm$core$List$cons,
									{
										f: 'Close snapping',
										e: '',
										g: A2($author$project$Desktop$key, model, 'snap:close'),
										fd: true,
										cl: 'control:close',
										el: 'Close',
										aJ: scoped($author$project$Desktop$CloseSnap)
									},
									_Utils_ap(
										A2($elm$core$List$map, regionControl, $author$project$Snap$regions),
										_List_fromArray(
											[
												{
												f: applyLabel,
												e: '',
												g: A2($author$project$Desktop$key, model, 'snap:apply'),
												fd: applyReady,
												cl: 'snap:apply',
												el: applyLabel,
												aJ: applyReady ? scoped($author$project$Desktop$ApplySnap) : $elm$core$Maybe$Nothing
											}
											])));
							}
						} else {
							if ($author$project$Desktop$switcherOpen(model)) {
								var selected = A2(
									$elm$core$Maybe$map,
									function ($) {
										return $.r;
									},
									$author$project$Switcher$selected(model.i));
								var scoped = function (message) {
									return A2(
										$elm$core$Maybe$map,
										message,
										$author$project$Desktop$capture(model));
								};
								var control = F4(
									function (identity, label, enabled, message) {
										return {
											f: label,
											e: '',
											g: A2($author$project$Desktop$key, model, identity),
											fd: enabled,
											cl: identity,
											el: label,
											aJ: enabled ? scoped(message) : $elm$core$Maybe$Nothing
										};
									});
								var browsing = $author$project$Switcher$phase(model.i) === 2;
								var row = function (family) {
									var ready = browsing && (family.dj && (!A2($author$project$Surface$familyBlocked, model, family.r)));
									var identity = 'switcher:family:' + $author$project$UInt64$string(family.r);
									var detail = _Utils_eq(
										selected,
										$elm$core$Maybe$Just(family.r)) ? 'Selected' : (family.b_ ? 'Minimized' : 'Open');
									return {
										f: _Utils_ap(
											family.b_ ? 'Restore ' : 'Activate ',
											_Utils_ap(
												family.el,
												_Utils_eq(
													selected,
													$elm$core$Maybe$Just(family.r)) ? '; selected' : '')),
										e: detail,
										g: A2($author$project$Desktop$key, model, identity),
										fd: ready,
										cl: identity,
										el: family.el,
										aJ: ready ? scoped(
											function (stamp) {
												return A2($author$project$Desktop$SwitcherChoose, stamp, family.r);
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
										$author$project$Switcher$entries(model.i)));
							} else {
								if (model.m) {
									var transferReady = $author$project$Shell$available(model.a.b) && _Utils_eq(model.k, $elm$core$Maybe$Nothing);
									var scoped = function (message) {
										return A2(
											$elm$core$Maybe$map,
											message,
											$author$project$Desktop$capture(model));
									};
									var transferControl = function (family) {
										var identity = 'overview:transfer:' + $author$project$UInt64$string(family.r);
										var enabled = transferReady && (family.dj && ((!A2($author$project$Surface$familyBlocked, model, family.r)) && A2(
											$elm$core$Maybe$withDefault,
											false,
											A2(
												$elm$core$Maybe$map,
												function (caps) {
													return A2($elm$core$List$member, 'transfer-workspace', caps.ev);
												},
												model.a.b.ds))));
										return {
											f: 'Move ' + (family.el + ' to another workspace'),
											e: '',
											g: A2($author$project$Desktop$key, model, identity),
											fd: enabled,
											cl: identity,
											el: 'Move ' + (family.el + '…'),
											aJ: enabled ? scoped(
												function (stamp) {
													return A2($author$project$Desktop$OpenOverviewTransfer, stamp, family.r);
												}) : $elm$core$Maybe$Nothing
										};
									};
									var workspaceControl = function (group) {
										return {
											f: 'Browse workspace ' + (group.cU + (group.bt ? '; active workspace' : '')),
											e: _Utils_ap(
												group.bt ? 'Active workspace' : '',
												_Utils_eq(
													model.at,
													$elm$core$Maybe$Just(group.cU)) ? ' • Selected' : ''),
											g: A2($author$project$Desktop$key, model, 'overview:workspace:' + group.cU),
											fd: true,
											cl: 'overview:workspace:' + group.cU,
											el: 'Workspace ' + group.cU,
											aJ: scoped(
												function (stamp) {
													return A2(
														$author$project$Desktop$OverviewWorkspace,
														stamp,
														$elm$core$Maybe$Just(group.cU));
												})
										};
									};
									var groups = A2(
										$elm$core$Maybe$withDefault,
										_List_Nil,
										$author$project$TaskView$groups(model.a.b));
									var familyControl = F2(
										function (group, family) {
											var ready = $author$project$Shell$available(model.a.b) && (family.dj && (!A2($author$project$Surface$familyBlocked, model, family.r)));
											var identity = 'overview:family:' + $author$project$UInt64$string(family.r);
											var detail = 'Workspace ' + (group.cU + (' • ' + (A2($author$project$Surface$familyBlocked, model, family.r) ? 'Awaiting native confirmation' : ((!family.dj) ? 'Unavailable for activation' : (family.b_ ? 'Minimized' : 'Open')))));
											return {
												f: (family.b_ ? 'Restore ' : 'Activate ') + (family.el + (' on workspace ' + group.cU)),
												e: detail,
												g: A2($author$project$Desktop$key, model, identity),
												fd: ready,
												cl: identity,
												el: family.el,
												aJ: ready ? scoped(
													function (stamp) {
														return A2($author$project$Desktop$OverviewChoose, stamp, family.r);
													}) : $elm$core$Maybe$Nothing
											};
										});
									var workspaceRows = function (group) {
										return A2(
											$elm$core$List$cons,
											workspaceControl(group),
											(_Utils_eq(model.at, $elm$core$Maybe$Nothing) || _Utils_eq(
												model.at,
												$elm$core$Maybe$Just(group.cU))) ? A2(
												$elm$core$List$concatMap,
												function (family) {
													return _List_fromArray(
														[
															A2(familyControl, group, family),
															transferControl(family)
														]);
												},
												group.a) : _List_Nil);
									};
									var destinationRows = function (root) {
										return A2(
											$elm$core$Maybe$withDefault,
											_List_Nil,
											A2(
												$elm$core$Maybe$map,
												function (geometry) {
													return A2(
														$elm$core$List$filterMap,
														function (destination) {
															return A2(
																$elm$core$Maybe$map,
																function (_v8) {
																	var identity = 'overview:destination:' + destination;
																	return {
																		f: 'Move selected window to workspace ' + destination,
																		e: '',
																		g: A2($author$project$Desktop$key, model, identity),
																		fd: transferReady,
																		cl: identity,
																		el: 'Move to workspace ' + destination,
																		aJ: transferReady ? scoped(
																			function (stamp) {
																				return A3($author$project$Desktop$OverviewTransfer, stamp, root, destination);
																			}) : $elm$core$Maybe$Nothing
																	};
																},
																A3($author$project$Transfer$propose, geometry, root, destination));
														},
														$author$project$Transfer$destinations(geometry));
												},
												model.a.b.ap));
									};
									return (!_Utils_eq(model.aB, $elm$core$Maybe$Nothing)) ? _Utils_ap(
										_List_fromArray(
											[
												{
												f: 'Cancel window transfer',
												e: '',
												g: A2($author$project$Desktop$key, model, 'overview:transfer-cancel'),
												fd: true,
												cl: 'control:close',
												el: 'Cancel transfer',
												aJ: scoped($author$project$Desktop$CancelOverviewTransfer)
											}
											]),
										A2(
											$elm$core$Maybe$withDefault,
											_List_Nil,
											A2($elm$core$Maybe$map, destinationRows, model.aB))) : _Utils_ap(
										_List_fromArray(
											[
												{
												f: 'Close Task View and return to windows',
												e: '',
												g: A2($author$project$Desktop$key, model, 'overview:close'),
												fd: true,
												cl: 'control:close',
												el: 'Close Task View',
												aJ: scoped($author$project$Desktop$CloseOverview)
											},
												{
												f: 'Browse all workspaces',
												e: _Utils_eq(model.at, $elm$core$Maybe$Nothing) ? 'Selected' : '',
												g: A2($author$project$Desktop$key, model, 'overview:all'),
												fd: true,
												cl: 'overview:all',
												el: 'All windows',
												aJ: scoped(
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
											$author$project$Launch$status(model.M),
											_List_fromArray(
												['Pending', 'Unknown']));
										var pinIds = $author$project$Desktop$pinIdentities(model);
										var pinAction = F5(
											function (suffix, label, detail, allowed, message) {
												return {
													f: label,
													e: detail,
													g: A2($author$project$Desktop$key, model, suffix),
													fd: $author$project$Pins$writable(model.R) && allowed,
													cl: suffix,
													el: label,
													aJ: ($author$project$Pins$writable(model.R) && allowed) ? scoped(message) : $elm$core$Maybe$Nothing
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
															return $.dA;
														},
														A2(
															$elm$core$Maybe$andThen,
															$author$project$Catalog$lookup(identity),
															model.aD)));
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
													$author$project$Catalog$id(entry.cU),
													model.M)) : $elm$core$Maybe$Nothing;
											return {
												f: 'Open ' + entry.dA,
												e: '',
												g: A2(
													$author$project$Desktop$key,
													model,
													'entry:' + $author$project$Catalog$id(entry.cU)),
												fd: !_Utils_eq(choice, $elm$core$Maybe$Nothing),
												cl: 'entry:' + $author$project$Catalog$id(entry.cU),
												el: 'Open ' + entry.dA,
												aJ: choice
											};
										};
										var entries = A2(
											$elm$core$Maybe$withDefault,
											_List_Nil,
											A2(
												$elm$core$Maybe$map,
												$author$project$Catalog$search(model.c_),
												model.aD));
										var jump = A2(
											$elm$core$Maybe$withDefault,
											_List_Nil,
											A2(
												$elm$core$Maybe$map,
												$elm$core$List$singleton,
												A2(
													$elm$core$Maybe$map,
													function (entry) {
														return {
															f: 'Actions for ' + entry.dA,
															e: 'Application actions and recent files',
															g: A2(
																$author$project$Desktop$key,
																model,
																'jump:open:' + $author$project$Catalog$id(entry.cU)),
															fd: true,
															cl: 'jump:open:' + $author$project$Catalog$id(entry.cU),
															el: 'Actions for ' + entry.dA,
															aJ: scoped(
																function (stamp) {
																	return A2(
																		$author$project$Desktop$OpenJumpList,
																		stamp,
																		$author$project$Catalog$id(entry.cU));
																})
														};
													},
													$elm$core$List$head(entries))));
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
															$author$project$Catalog$id(entry.cU),
															pinIds) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(
															A5(
																pinAction,
																'pin:' + $author$project$Catalog$id(entry.cU),
																'Pin ' + entry.dA,
																'Add to taskbar',
																true,
																function (stamp) {
																	return A2(
																		$author$project$Desktop$TogglePin,
																		stamp,
																		$author$project$Catalog$id(entry.cU));
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
															f: 'I checked; allow another launch',
															e: '',
															g: A2($author$project$Desktop$key, model, 'control:acknowledge'),
															fd: true,
															cl: 'control:acknowledge',
															el: 'I checked; allow another launch',
															aJ: $elm$core$Maybe$Just(
																$author$project$Desktop$Acknowledge(token))
														};
													},
													$author$project$Launch$uncertain(model.M))));
										return _Utils_ap(
											_List_fromArray(
												[
													{
													f: 'Search applications',
													e: '',
													g: 'launcher-search',
													fd: true,
													cl: 'control:search',
													el: model.c_,
													aJ: scoped(
														function (stamp) {
															return A2($author$project$Desktop$SearchQuery, stamp, model.c_);
														})
												},
													{
													f: 'Close applications and return to windows',
													e: '',
													g: A2($author$project$Desktop$key, model, 'control:close'),
													fd: true,
													cl: 'control:close',
													el: 'Windows',
													aJ: scoped($author$project$Desktop$CloseApplications)
												},
													{
													f: 'Refresh applications',
													e: '',
													g: A2($author$project$Desktop$key, model, 'control:refresh'),
													fd: true,
													cl: 'control:refresh',
													el: 'Refresh',
													aJ: scoped($author$project$Desktop$RefreshApplications)
												}
												]),
											_Utils_ap(
												acknowledge,
												_Utils_ap(
													jump,
													_Utils_ap(
														pinFirst,
														_Utils_ap(
															$elm$core$List$concat(
																A2($elm$core$List$indexedMap, pinRows, pinIds)),
															A2($elm$core$List$map, entryControl, entries))))));
									} else {
										if (!_Utils_eq(
											$author$project$MenuBridge$menuSnapshot(model.a.h).aI,
											$elm$core$Maybe$Nothing)) {
											var _v9 = $author$project$MenuBridge$menuSnapshot(model.a.h).aI;
											if (_v9.$ === 1) {
												return _List_Nil;
											} else {
												var menu = _v9.a;
												var ready = $author$project$Shell$available(model.a.b) && (_Utils_eq(menu.W, $author$project$Menu$Ready) && (!$author$project$Surface$menuBlocked(model)));
												var prefix = 'menu:' + ($elm$core$String$fromInt(
													$author$project$Menu$menuNumber(menu.cl)) + ':');
												var row = F2(
													function (index, item) {
														var committed = A2(
															$elm$core$Maybe$withDefault,
															'',
															A2(
																$elm$core$Maybe$map,
																A2(
																	$elm$core$Basics$composeR,
																	$author$project$Provider$incarnation,
																	$author$project$Surface$confirmedWindowState(model)),
																$author$project$MenuBridge$currentProvider(model.a.h)));
														var detail = A2(
															$elm$core$String$join,
															' • ',
															A2(
																$elm$core$List$filter,
																A2($elm$core$Basics$composeL, $elm$core$Basics$not, $elm$core$String$isEmpty),
																_List_fromArray(
																	[
																		committed,
																		$author$project$Surface$menuBlocked(model) ? 'Awaiting native confirmation' : (_Utils_eq(
																		menu.fN,
																		$elm$core$Maybe$Just(index)) ? 'Selected' : '')
																	])));
														return {
															f: _Utils_ap(
																item.el,
																$author$project$Surface$menuBlocked(model) ? ('; ' + detail) : ''),
															e: detail,
															g: _Utils_ap(
																prefix,
																$elm$core$String$fromInt(index)),
															fd: ready && item.fd,
															cl: _Utils_ap(
																prefix,
																$elm$core$String$fromInt(index)),
															el: item.el,
															aJ: (ready && item.fd) ? $elm$core$Maybe$Just(
																$author$project$Desktop$Window(
																	$author$project$TaskbarShell$MenuEvent(
																		A3($author$project$Menu$Activate, menu.cl, menu.dk, index)))) : $elm$core$Maybe$Nothing
														};
													});
												var snap = A2(
													$elm$core$Maybe$andThen,
													function (provider) {
														return A2(
															$elm$core$Maybe$map,
															function (_v11) {
																return {
																	f: 'Open snapping',
																	e: '',
																	g: prefix + 'snap',
																	fd: ready,
																	cl: 'control:snap-open',
																	el: 'Snap window',
																	aJ: ready ? A2(
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
																model.a.b.ap));
													},
													$author$project$MenuBridge$currentProvider(model.a.h));
												var applicationActions = A2(
													$elm$core$Maybe$andThen,
													function (provider) {
														return function (matches) {
															if (matches.b && (!matches.b.b)) {
																var entry = matches.a;
																return $elm$core$Maybe$Just(
																	{
																		f: 'Actions for ' + entry.dA,
																		e: 'Declared actions and recent files',
																		g: prefix + 'application-actions',
																		fd: ready,
																		cl: 'jump:open:' + $author$project$Catalog$id(entry.cU),
																		el: 'Application actions',
																		aJ: ready ? A2(
																			$elm$core$Maybe$map,
																			function (stamp) {
																				return A2(
																					$author$project$Desktop$OpenJumpList,
																					stamp,
																					$author$project$Catalog$id(entry.cU));
																			},
																			$author$project$Desktop$capture(model)) : $elm$core$Maybe$Nothing
																	});
															} else {
																return $elm$core$Maybe$Nothing;
															}
														}(
															A2(
																$elm$core$List$filter,
																function (entry) {
																	return A2(
																		$elm$core$List$any,
																		function (group) {
																			return A2(
																				$elm$core$List$any,
																				function (family) {
																					return _Utils_eq(
																						family.r,
																						$author$project$Provider$incarnation(provider));
																				},
																				group.aG);
																		},
																		A2(
																			$author$project$Desktop$pinGroups,
																			$author$project$Catalog$id(entry.cU),
																			model));
																},
																A2(
																	$elm$core$Maybe$withDefault,
																	_List_Nil,
																	A2($elm$core$Maybe$map, $author$project$Catalog$entries, model.aD))));
													},
													$author$project$MenuBridge$currentProvider(model.a.h));
												return A2(
													$elm$core$List$cons,
													{
														f: 'Close window actions',
														e: '',
														g: prefix + 'close',
														fd: true,
														cl: 'control:menu-close',
														el: 'Close',
														aJ: $elm$core$Maybe$Just(
															$author$project$Desktop$Window(
																$author$project$TaskbarShell$MenuEvent(
																	$author$project$Menu$Dismiss(menu.cl))))
													},
													_Utils_ap(
														A2($elm$core$List$indexedMap, row, menu.fo),
														_Utils_ap(
															A2(
																$elm$core$Maybe$withDefault,
																_List_Nil,
																A2($elm$core$Maybe$map, $elm$core$List$singleton, snap)),
															_Utils_ap(
																A2(
																	$elm$core$Maybe$withDefault,
																	_List_Nil,
																	A2($elm$core$Maybe$map, $elm$core$List$singleton, applicationActions)),
																$author$project$Surface$recoveryPopup(model)))));
											}
										} else {
											var _v12 = model.a.J;
											if (!_v12.$) {
												var picker = _v12.a;
												var familyControl = function (family) {
													var ready = $author$project$Shell$available(model.a.b) && (family.dj && ((!A2($author$project$Surface$familyBlocked, model, family.r)) && _Utils_eq(
														$author$project$Shell$capture(model.a.b),
														$elm$core$Maybe$Just(picker.c5))));
													var detail = A2(
														$elm$core$String$join,
														' • ',
														A2(
															$elm$core$List$filter,
															A2($elm$core$Basics$composeL, $elm$core$Basics$not, $elm$core$String$isEmpty),
															_List_fromArray(
																[
																	A2($author$project$Surface$confirmedWindowState, model, family.r),
																	A2($author$project$Surface$familyBlocked, model, family.r) ? 'Awaiting native confirmation' : (family.b_ ? 'Minimized' : 'Open')
																])));
													return {
														f: _Utils_ap(
															family.b_ ? 'Restore ' : 'Activate ',
															_Utils_ap(
																family.el,
																A2($author$project$Surface$familyBlocked, model, family.r) ? ('; ' + detail) : '')),
														e: detail,
														g: 'picker:' + ($author$project$Shell$stampKey(picker.c5) + (':' + ($author$project$UInt64$string(picker.fh) + (':' + $author$project$UInt64$string(family.r))))),
														fd: ready,
														cl: 'family:' + $author$project$UInt64$string(family.r),
														el: _Utils_ap(
															family.b_ ? 'Restore ' : 'Activate ',
															family.el),
														aJ: ready ? $elm$core$Maybe$Just(
															$author$project$Desktop$Window(
																A3($author$project$TaskbarShell$Choose, picker.c5, picker.fh, family.r))) : $elm$core$Maybe$Nothing
													};
												};
												var families = A2(
													$elm$core$List$concatMap,
													function ($) {
														return $.aG;
													},
													A2(
														$elm$core$List$filter,
														function (group) {
															return _Utils_eq(group.a_, picker.a_);
														},
														$author$project$TaskbarShell$groups(model.a)));
												return A2(
													$elm$core$List$cons,
													{
														f: 'Close window picker',
														e: '',
														g: 'picker-close:' + ($author$project$Shell$stampKey(picker.c5) + (':' + $author$project$UInt64$string(picker.fh))),
														fd: true,
														cl: 'control:close',
														el: 'Close',
														aJ: $elm$core$Maybe$Just(
															$author$project$Desktop$Window(
																A2($author$project$TaskbarShell$Close, picker.c5, picker.fh)))
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
					}
				}
			}
		}
	}
};
var $elm$json$Json$Encode$int = _Json_wrap;
var $author$project$Settings$encodeValues = function (values) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'theme',
				$elm$json$Json$Encode$string(
					$author$project$Settings$themeName(values.de))),
				_Utils_Tuple2(
				'textScale',
				$elm$json$Json$Encode$int(values.cy)),
				_Utils_Tuple2(
				'effectsOff',
				$elm$json$Json$Encode$bool(values.cQ)),
				_Utils_Tuple2(
				'reducedTransparency',
				$elm$json$Json$Encode$bool(values.c$))
			]));
};
var $author$project$Notifications$focusedIdentity = function (model) {
	return A2(
		$elm$core$Maybe$map,
		A2(
			$elm$core$Basics$composeR,
			function ($) {
				return $.fR;
			},
			$author$project$Notifications$identity),
		model.ci);
};
var $author$project$Provider$geometryObservation = function (_v0) {
	var state = _v0;
	return state.ap;
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
var $author$project$Provider$getBinding = function (_v0) {
	var value = _v0;
	return value.dk;
};
var $author$project$Provider$menuBinding = $author$project$Provider$getBinding;
var $author$project$Surface$mode = function (model) {
	return (!_Utils_eq(model.o, $elm$core$Maybe$Nothing)) ? 'jump' : (model.p ? 'files' : (model.v ? 'system' : (model.t ? 'notifications' : (model.n ? 'settings' : ((!_Utils_eq(model.x, $elm$core$Maybe$Nothing)) ? 'snap' : ($author$project$Desktop$switcherOpen(model) ? 'switcher' : (model.m ? 'overview' : (model.q ? 'applications' : ((!_Utils_eq(
		$author$project$MenuBridge$menuSnapshot(model.a.h).aI,
		$elm$core$Maybe$Nothing)) ? 'menu' : ((!_Utils_eq(model.a.J, $elm$core$Maybe$Nothing)) ? 'picker' : 'closed'))))))))));
};
var $author$project$Motion$name = function (profile) {
	if (!profile) {
		return 'reduced';
	} else {
		return 'full';
	}
};
var $author$project$Provider$nativeBinding = function (_v0) {
	var value = _v0;
	return value.P.er;
};
var $author$project$Effects$Cancelled = 3;
var $author$project$Surface$reservationReason = 'Window action awaits native confirmation. Refresh status only reads observations; it does not retry the action.';
var $author$project$Shell$status = function (model) {
	if (model.ct) {
		return 'Window recovery history is full. Restart the shell to continue.';
	} else {
		if (model.X) {
			return 'Window transport is full or unavailable. Waiting for a verified output or capacity update.';
		} else {
			var _v0 = A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.W;
				},
				model._.fS);
			_v0$3:
			while (true) {
				if (!_v0.$) {
					switch (_v0.a) {
						case 0:
							var _v1 = _v0.a;
							return 'Applying window change…';
						case 4:
							var _v2 = _v0.a;
							return model.ft + ' The last request could not be confirmed.';
						case 2:
							var _v3 = _v0.a;
							return model.ft + ' The window change was refused.';
						default:
							break _v0$3;
					}
				} else {
					break _v0$3;
				}
			}
			return model.ft;
		}
	}
};
var $author$project$Surface$windowNotice = function (model) {
	var subject = function (transaction) {
		var operation = function () {
			var _v3 = transaction.aa.bh;
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
				case 5:
					return 'Exit fullscreen';
				case 8:
					return 'Always on top';
				case 9:
					return 'Unpin window';
				case 6:
					return 'Snap';
				default:
					var p = _v3.a;
					return 'Move to workspace ' + p.bx;
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
						return $.el;
					},
					$elm$core$String$left(512)),
				$elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (family) {
							return _Utils_eq(family.r, transaction.aa.aq);
						},
						A2(
							$elm$core$List$concatMap,
							function ($) {
								return $.aG;
							},
							$author$project$TaskbarShell$groups(model.a))))));
		return _Utils_Tuple2(operation, label);
	};
	var _v0 = model.a.b._.fS;
	if (!_v0.$) {
		var transaction = _v0.a;
		var _v1 = subject(transaction);
		var operation = _v1.a;
		var label = _v1.b;
		var _v2 = transaction.W;
		switch (_v2) {
			case 0:
				return operation + (': applying to ' + (label + '…'));
			case 4:
				return operation + (': not confirmed for ' + (label + ((!model.a.b.j) ? '. Reconnect to read window status; the action will not be repeated.' : '. Check your windows; Refresh only reads status.')));
			case 2:
				return operation + (': refused for ' + (label + '. Refresh window status, then choose again.'));
			case 3:
				return operation + (': cancelled for ' + (label + '.'));
			default:
				return $author$project$Surface$recoveryNeeded(model) ? $author$project$Surface$reservationReason : $author$project$Shell$status(model.a.b);
		}
	} else {
		return ($author$project$Surface$recoveryNeeded(model) && (!(!model.a.b.j))) ? $author$project$Surface$reservationReason : $author$project$Shell$status(model.a.b);
	}
};
var $author$project$Surface$notice = function (model) {
	if (!_Utils_eq(model.o, $elm$core$Maybe$Nothing)) {
		return (!_Utils_eq(model.aZ, $elm$core$Maybe$Nothing)) ? 'Reading application actions…' : model.ar.ft;
	} else {
		if (model.p) {
			return (!_Utils_eq(model.aW, $elm$core$Maybe$Nothing)) ? 'Reading Files state…' : model.T.ft;
		} else {
			if (model.v) {
				return (!_Utils_eq(model.aT, $elm$core$Maybe$Nothing)) ? 'Reading native system state…' : ((!_Utils_eq(model.s, $elm$core$Maybe$Nothing)) ? 'Confirm or cancel the requested system change.' : model.ak.ft);
			} else {
				if (model.t) {
					return (!_Utils_eq(model.a0, $elm$core$Maybe$Nothing)) ? 'Loading notifications…' : model.C.ft;
				} else {
					if (model.n) {
						return ((!_Utils_eq(model.bo, $elm$core$Maybe$Nothing)) ? 'Loading settings…' : model.aj.ft) + (' · ' + model.ac.ft);
					} else {
						if ($author$project$Desktop$switcherOpen(model)) {
							return ($author$project$Switcher$phase(model.i) === 1) ? 'Loading window activation history…' : ((!_Utils_eq(model.ah, $elm$core$Maybe$Nothing)) ? 'Alt+Tab: next window. Alt+Shift+Tab: previous. Release Alt: activate. Escape: cancel.' : 'Tab or Right: next window. Shift+Tab or Left: previous. Enter: activate. Escape: cancel.');
						} else {
							if (model.m) {
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
											return $.W;
										},
										$author$project$MenuBridge$menuSnapshot(model.a.h).aI);
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
									if (!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) {
										return 'Updating your window choice…';
									} else {
										if (!$elm$core$String$isEmpty(model.G)) {
											return model.G;
										} else {
											if ((!model.q) && A2(
												$elm$core$Maybe$withDefault,
												false,
												A2(
													$elm$core$Maybe$map,
													function (transaction) {
														return A2(
															$elm$core$List$member,
															transaction.W,
															_List_fromArray(
																[0, 4, 2, 3]));
													},
													model.a.b._.fS))) {
												return $author$project$Surface$windowNotice(model);
											} else {
												if ((!$elm$core$String$isEmpty(model.R.ft)) && (model.R.ft !== 'Pin order saved.')) {
													return model.R.ft;
												} else {
													var _v2 = $author$project$Launch$status(model.M);
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
															return (!_Utils_eq(model.bu, $elm$core$Maybe$Nothing)) ? (($author$project$Surface$recoveryNeeded(model) && (!(!model.a.b.j))) ? $author$project$Surface$reservationReason : 'Applications were not opened. Choose Applications again.') : (model.q ? ((!_Utils_eq(model.A, $elm$core$Maybe$Nothing)) ? 'Loading applications…' : (_Utils_eq(model.aD, $elm$core$Maybe$Nothing) ? 'Application list unavailable. Refresh to try again.' : (A2(
																$elm$core$Maybe$withDefault,
																false,
																A2(
																	$elm$core$Maybe$map,
																	A2(
																		$elm$core$Basics$composeR,
																		$author$project$Catalog$search(model.c_),
																		$elm$core$List$isEmpty),
																	model.aD)) ? 'No matching applications. Change your search or Refresh.' : ($elm$core$String$isEmpty(
																$elm$core$String$trim(model.c_)) ? 'Type to search applications.' : 'Choose a matching application.')))) : $author$project$Surface$windowNotice(model));
													}
												}
											}
										}
									}
								}
							}
						}
					}
				}
			}
		}
	}
};
var $elm$core$Tuple$pair = F2(
	function (a, b) {
		return _Utils_Tuple2(a, b);
	});
var $author$project$Surface$packet = F3(
	function (publication, lease, model) {
		var checked = function (control) {
			return A2(
				$elm$core$Maybe$andThen,
				function (menu) {
					return A2(
						$elm$core$Maybe$andThen,
						function (_v1) {
							var item = _v1.b;
							var _v2 = item.e3;
							if (_v2.$ === 8) {
								return A2(
									$elm$core$Maybe$andThen,
									function (provider) {
										return ((!_Utils_eq(
											$author$project$Provider$menuBinding(provider),
											menu.dk)) || (!_Utils_eq(
											$elm$core$Maybe$Just(
												$author$project$Provider$nativeBinding(provider)),
											model.a.b.dk))) ? $elm$core$Maybe$Nothing : A2(
											$elm$core$Maybe$map,
											function ($) {
												return $.fB;
											},
											A2(
												$elm$core$Maybe$andThen,
												function ($) {
													return $.dF;
												},
												A2(
													$elm$core$Maybe$andThen,
													$author$project$GeometryProjection$window(
														$author$project$Provider$incarnation(provider)),
													$author$project$Provider$geometryObservation(provider))));
									},
									$author$project$MenuBridge$currentProvider(model.a.h));
							} else {
								return $elm$core$Maybe$Nothing;
							}
						},
						$elm$core$List$head(
							A2(
								$elm$core$List$filter,
								function (_v0) {
									var index = _v0.a;
									var item = _v0.b;
									return _Utils_eq(
										control.cl,
										'menu:' + ($elm$core$String$fromInt(
											$author$project$Menu$menuNumber(menu.cl)) + (':' + $elm$core$String$fromInt(index))));
								},
								A2($elm$core$List$indexedMap, $elm$core$Tuple$pair, menu.fo))));
				},
				$author$project$MenuBridge$menuSnapshot(model.a.h).aI);
		};
		var encode = function (control) {
			return $elm$json$Json$Encode$object(
				_Utils_ap(
					_List_fromArray(
						[
							_Utils_Tuple2(
							'id',
							$elm$json$Json$Encode$string(control.cl)),
							_Utils_Tuple2(
							'domId',
							$elm$json$Json$Encode$string(control.g)),
							_Utils_Tuple2(
							'label',
							$elm$json$Json$Encode$string(control.el)),
							_Utils_Tuple2(
							'ariaLabel',
							$elm$json$Json$Encode$string(control.f)),
							_Utils_Tuple2(
							'detail',
							$elm$json$Json$Encode$string(control.e)),
							_Utils_Tuple2(
							'enabled',
							$elm$json$Json$Encode$bool(
								control.fd && (!_Utils_eq(control.aJ, $elm$core$Maybe$Nothing)))),
							_Utils_Tuple2(
							'focusOnly',
							$elm$json$Json$Encode$bool(
								model.t && ((!control.fd) && _Utils_eq(
									$author$project$Notifications$focusedIdentity(model.C),
									$elm$core$Maybe$Just(control.cl)))))
						]),
					A2(
						$elm$core$Maybe$withDefault,
						_List_Nil,
						A2(
							$elm$core$Maybe$map,
							function (value) {
								return _List_fromArray(
									[
										_Utils_Tuple2(
										'checked',
										$elm$json$Json$Encode$bool(value))
									]);
							},
							checked(control)))));
		};
		return $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'surfaceProtocol',
					$elm$json$Json$Encode$int(2)),
					_Utils_Tuple2(
					'keyboardParent',
					$elm$json$Json$Encode$bool(model.bI === 1)),
					_Utils_Tuple2(
					'motion',
					$elm$json$Json$Encode$string(
						$author$project$Motion$name(
							$author$project$Motion$desired(model.I)))),
					_Utils_Tuple2(
					'appearance',
					$author$project$Settings$encodeValues(
						A2(
							$elm$core$Maybe$withDefault,
							$author$project$Settings$defaults,
							A2(
								$elm$core$Maybe$map,
								function ($) {
									return $.bs;
								},
								model.aj.c)))),
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
						_Utils_ap(
							$author$project$Surface$notice(model),
							_Utils_ap(
								((!model.p) && ((!_Utils_eq(model.T.ex, $elm$core$Maybe$Nothing)) || A2($elm$core$String$startsWith, 'Files:', model.T.ft))) ? (' · ' + model.T.ft) : '',
								(_Utils_eq(model.o, $elm$core$Maybe$Nothing) && ((!_Utils_eq(model.ar.ex, $elm$core$Maybe$Nothing)) || A2($elm$core$String$startsWith, 'Application action:', model.ar.ft))) ? (' · ' + model.ar.ft) : '')))),
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
	return A3($author$project$Surface$packet, model.eF, model.em, model.d);
};
var $elm$json$Json$Encode$null = _Json_encodeNull;
var $author$project$ReceiptRouter$count = function (_v0) {
	var entries = _v0;
	return $elm$core$List$length(entries);
};
var $author$project$MenuBridge$receiptCount = function (_v0) {
	var state = _v0;
	return $author$project$ReceiptRouter$count(state.au);
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
	return value.cA;
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
		var provider = $author$project$MenuBridge$currentProvider(model.h);
		var prefix = 'menu:' + ($elm$core$String$fromInt(
			$author$project$Menu$menuNumber(current.cl)) + ':');
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
							$elm$json$Json$Encode$string(item.el)),
							_Utils_Tuple2(
							'enabled',
							$elm$json$Json$Encode$bool(item.fd))
						]));
			});
		return $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'id',
					$elm$json$Json$Encode$int(
						$author$project$Menu$menuNumber(current.cl))),
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
						A2($elm$core$Maybe$map, $elm$json$Json$Encode$int, current.fN))),
					_Utils_Tuple2(
					'actions',
					A2(
						$elm$json$Json$Encode$list,
						$elm$core$Basics$identity,
						A2($elm$core$List$indexedMap, row, current.fo)))
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
							$author$project$UInt64$string(item.r))),
						_Utils_Tuple2(
						'title',
						$elm$json$Json$Encode$string(item.el)),
						_Utils_Tuple2(
						'state',
						$elm$json$Json$Encode$string(
							item.b_ ? 'Minimized' : 'Open')),
						_Utils_Tuple2(
						'domId',
						$elm$json$Json$Encode$string(
							'picker:' + ($author$project$Shell$stampKey(current.c5) + (':' + ($author$project$UInt64$string(current.fh) + (':' + $author$project$UInt64$string(item.r)))))))
					]));
		};
		return $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'generation',
					$elm$json$Json$Encode$string(
						$author$project$UInt64$string(current.fh))),
					_Utils_Tuple2(
					'closeId',
					$elm$json$Json$Encode$string(
						'picker-close:' + ($author$project$Shell$stampKey(current.c5) + (':' + $author$project$UInt64$string(current.fh))))),
					_Utils_Tuple2(
					'selections',
					A2(
						$elm$json$Json$Encode$list,
						family,
						A2(
							$elm$core$List$concatMap,
							function ($) {
								return $.aG;
							},
							A2(
								$elm$core$List$filter,
								function (item) {
									return _Utils_eq(item.a_, current.a_);
								},
								$author$project$TaskbarShell$groups(model)))))
				]));
	};
	var shell = model.b;
	var phase = function () {
		var _v0 = shell.j;
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
					$elm$json$Json$Encode$string(item.a_)),
					_Utils_Tuple2(
					'domId',
					$elm$json$Json$Encode$string('group:' + (stamp + (':' + item.a_)))),
					_Utils_Tuple2(
					'title',
					$elm$json$Json$Encode$string(
						A2(
							$elm$core$Maybe$withDefault,
							'Windows',
							A2(
								$elm$core$Maybe$map,
								function ($) {
									return $.el;
								},
								$elm$core$List$head(item.aG))))),
					_Utils_Tuple2(
					'active',
					$elm$json$Json$Encode$bool(
						A2(
							$elm$core$List$any,
							function ($) {
								return $.bt;
							},
							item.aG))),
					_Utils_Tuple2(
					'expanded',
					$elm$json$Json$Encode$bool(
						A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (picker) {
									return _Utils_eq(picker.a_, item.a_);
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
												return $.W;
											},
											$author$project$Effects$statusName),
										shell._.fS)))),
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
									$author$project$MenuBridge$menuSnapshot(model.h).aI))),
							_Utils_Tuple2(
							'mode',
							field('mode')),
							_Utils_Tuple2(
							'outstanding',
							$elm$json$Json$Encode$int(
								$author$project$MenuBridge$menuSnapshot(model.h).fx)),
							_Utils_Tuple2(
							'registry',
							$elm$json$Json$Encode$int(
								$author$project$MenuBridge$receiptCount(model.h))),
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
var $author$project$Notifications$arrivals = F2(
	function (before, after) {
		var _v0 = _Utils_Tuple2(before.c, after.c);
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var old = _v0.a.a;
			var current = _v0.b.a;
			return ((!current.dj) || ((!_Utils_eq(current.c7, old.c7)) || ((A2($author$project$UInt64$compare, current.c2, old.c2) !== 2) || after.fD.cP))) ? _List_Nil : A2(
				$elm$core$List$sortWith,
				F2(
					function (a, b) {
						return A2($author$project$UInt64$compare, a.aq, b.aq);
					}),
				A2(
					$elm$core$List$filter,
					function (entry) {
						return (entry.dc === 'live') && (!A2(
							$elm$core$List$any,
							function (prior) {
								return _Utils_eq(prior.aq, entry.aq);
							},
							old.af));
					},
					current.af));
		} else {
			return _List_Nil;
		}
	});
var $author$project$Notifications$clearFocus = function (model) {
	return _Utils_update(
		model,
		{ci: $elm$core$Maybe$Nothing});
};
var $author$project$Notifications$Critical = 2;
var $author$project$Notifications$critical = function (entry) {
	return entry.dg === 2;
};
var $author$project$AdapterNotice$name = function (source) {
	switch (source) {
		case 0:
			return 'applications';
		case 1:
			return 'notifications';
		case 2:
			return 'files';
		case 3:
			return 'application-actions';
		case 4:
			return 'system';
		case 5:
			return 'settings';
		case 6:
			return 'motion-preferences';
		case 7:
			return 'shortcut-choices';
		default:
			return 'windows';
	}
};
var $author$project$AdapterNotice$encode = function (notice) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'adapter',
				$elm$json$Json$Encode$string(
					$author$project$AdapterNotice$name(notice.cv))),
				_Utils_Tuple2(
				'request',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(notice.c1))),
				_Utils_Tuple2(
				'service',
				A2(
					$elm$core$Maybe$withDefault,
					$elm$json$Json$Encode$null,
					A2(
						$elm$core$Maybe$map,
						A2($elm$core$Basics$composeR, $author$project$UInt64$string, $elm$json$Json$Encode$string),
						notice.c7))),
				_Utils_Tuple2(
				'revision',
				A2(
					$elm$core$Maybe$withDefault,
					$elm$json$Json$Encode$null,
					A2(
						$elm$core$Maybe$map,
						A2($elm$core$Basics$composeR, $author$project$UInt64$string, $elm$json$Json$Encode$string),
						notice.c2)))
			]));
};
var $author$project$Notifications$encodeIntent = function (value) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'service',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(value.c7))),
				_Utils_Tuple2(
				'id',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(value.cl))),
				_Utils_Tuple2(
				'incarnation',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(value.aq))),
				_Utils_Tuple2(
				'producer',
				$elm$json$Json$Encode$string(value.ab)),
				_Utils_Tuple2(
				'action',
				$elm$json$Json$Encode$string(value.e3)),
				_Utils_Tuple2(
				'verb',
				$elm$json$Json$Encode$string(value.cb))
			]));
};
var $author$project$Notifications$same = F3(
	function (choice, service, entry) {
		return _Utils_eq(choice.c7, service) && (_Utils_eq(choice.cl, entry.cl) && (_Utils_eq(choice.aq, entry.aq) && _Utils_eq(choice.ab, entry.ab)));
	});
var $author$project$Notifications$expirations = F2(
	function (before, after) {
		var _v0 = _Utils_Tuple2(before.c, after.c);
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var old = _v0.a.a;
			var current = _v0.b.a;
			return ((!_Utils_eq(current.c7, old.c7)) || ((A2($author$project$UInt64$compare, current.c2, old.c2) !== 2) || after.fD.cP)) ? _List_Nil : A2(
				$elm$core$List$sortWith,
				F2(
					function (a, b) {
						return A2($author$project$UInt64$compare, a.aq, b.aq);
					}),
				A2(
					$elm$core$List$filter,
					function (entry) {
						return (entry.dc === 'expired') && (A2(
							$elm$core$List$any,
							function (prior) {
								return (prior.dc === 'live') && (_Utils_eq(prior.cl, entry.cl) && (_Utils_eq(prior.aq, entry.aq) && _Utils_eq(prior.ab, entry.ab)));
							},
							old.af) && (A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (selected) {
									return A3($author$project$Notifications$same, selected.fR, current.c7, entry);
								},
								before.ci)) || A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (waiting) {
									return A3($author$project$Notifications$same, waiting.fR, current.c7, entry);
								},
								before.ex))));
					},
					current.af));
		} else {
			return _List_Nil;
		}
	});
var $author$project$Launch$refusal = function (_v0) {
	var model = _v0;
	var _v1 = model.j;
	if ((_v1.$ === 2) && (_v1.b === 1)) {
		var intent = _v1.a;
		var _v2 = _v1.b;
		return $elm$core$Maybe$Just(
			{
				d2: intent.d2,
				aa: $elm$json$Json$Encode$object(
					_List_fromArray(
						[
							_Utils_Tuple2(
							'request',
							$elm$json$Json$Encode$string(
								$author$project$UInt64$string(intent.c1))),
							_Utils_Tuple2(
							'lifetime',
							$elm$json$Json$Encode$string(
								$author$project$UInt64$string(intent.fp))),
							_Utils_Tuple2(
							'generation',
							$elm$json$Json$Encode$string(
								$author$project$UInt64$string(intent.fh))),
							_Utils_Tuple2(
							'entry',
							$elm$json$Json$Encode$string(intent.d2))
						]))
			});
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$OutcomeAnnouncements$launch = function (model) {
	return $author$project$Launch$refusal(model.M);
};
var $author$project$AdapterNotice$message = function (notice) {
	var _v0 = notice.cv;
	switch (_v0) {
		case 0:
			return 'Applications unavailable. Refresh applications, then choose again.';
		case 1:
			return 'Notifications unavailable. Refresh notifications to read current status. No action will be repeated.';
		case 2:
			return 'Files unavailable. Refresh Files state to read current access. No opening will be repeated.';
		case 3:
			return 'Application actions unavailable. Refresh application actions, then choose again.';
		case 4:
			return 'System controls unavailable. Refresh system state to read current capabilities. No change will be repeated.';
		case 5:
			return 'Settings unavailable or unsupported. Refresh settings; the stored copy is preserved.';
		case 6:
			return 'Motion preferences unavailable or unsupported. Refresh motion preferences; the stored copy is preserved.';
		case 7:
			return 'Shortcut choices unavailable or unsupported. Refresh shortcut choices; existing bindings are preserved.';
		default:
			return 'Window adapter unavailable. Reconnect to read current state. Unconfirmed actions will not be repeated.';
	}
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
var $author$project$Settings$Refused = 1;
var $author$project$OutcomeAnnouncements$settings = function (model) {
	return A2(
		$elm$core$Maybe$andThen,
		function (outcome) {
			return (outcome.fJ === 1) ? $elm$core$Maybe$Just(outcome.c1) : $elm$core$Maybe$Nothing;
		},
		model.aj.cZ);
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
var $author$project$Effects$counter = A2($elm$core$Basics$composeR, $author$project$UInt64$string, $elm$json$Json$Encode$string);
var $author$project$Transfer$encode = function (p) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'source',
				$elm$json$Json$Encode$string(p.cv)),
				_Utils_Tuple2(
				'sourceGeneration',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(p.da))),
				_Utils_Tuple2(
				'destination',
				$elm$json$Json$Encode$string(p.bx))
			]));
};
var $author$project$Effects$encodeContext = function (context) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'lifetime',
				$author$project$Effects$counter(context.fp)),
				_Utils_Tuple2(
				'epoch',
				$author$project$Effects$counter(context.fe)),
				_Utils_Tuple2(
				'output',
				$author$project$Effects$counter(context.y)),
				_Utils_Tuple2(
				'revision',
				$author$project$Effects$counter(context.c2))
			]));
};
var $elm$json$Json$Encode$float = _Json_wrap;
var $author$project$Snap$encodeProposal = function (proposed) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'region',
				$elm$json$Json$Encode$string(proposed.cu)),
				_Utils_Tuple2(
				'geometry',
				A2($elm$json$Json$Encode$list, $elm$json$Json$Encode$float, proposed.ap)),
				_Utils_Tuple2(
				'monitor',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(proposed.b$))),
				_Utils_Tuple2(
				'outputOwnershipGeneration',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(proposed.bi))),
				_Utils_Tuple2(
				'workAreaRevision',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(proposed.cE))),
				_Utils_Tuple2(
				'workspaceGeneration',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(proposed.ce)))
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
		case 5:
			return 'exit-fullscreen';
		case 8:
			return 'pin';
		case 9:
			return 'unpin';
		case 6:
			return 'snap';
		default:
			return 'transfer-workspace';
	}
};
var $author$project$Effects$encodeIntent = function (intent) {
	return $elm$json$Json$Encode$object(
		_Utils_ap(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'request',
					$author$project$Effects$counter(intent.c1)),
					_Utils_Tuple2(
					'generation',
					$author$project$Effects$counter(intent.fh)),
					_Utils_Tuple2(
					'incarnation',
					$author$project$Effects$counter(intent.aq)),
					_Utils_Tuple2(
					'operation',
					$elm$json$Json$Encode$string(
						$author$project$Effects$operationName(intent.bh))),
					_Utils_Tuple2(
					'context',
					$author$project$Effects$encodeContext(intent.P))
				]),
			function () {
				var _v0 = intent.bh;
				switch (_v0.$) {
					case 6:
						var proposed = _v0.a;
						return _List_fromArray(
							[
								_Utils_Tuple2(
								'placement',
								$author$project$Snap$encodeProposal(proposed))
							]);
					case 7:
						var proposed = _v0.a;
						return _List_fromArray(
							[
								_Utils_Tuple2(
								'transfer',
								$author$project$Transfer$encode(proposed))
							]);
					default:
						return _List_Nil;
				}
			}()));
};
var $author$project$OutcomeAnnouncements$transfer = function (model) {
	return A2(
		$elm$core$Maybe$andThen,
		function (transaction) {
			var _v0 = transaction.aa.bh;
			if (_v0.$ === 7) {
				return (transaction.W === 2) ? $elm$core$Maybe$Just(
					$elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'effectProtocol',
								$elm$json$Json$Encode$int(transaction.ay)),
								_Utils_Tuple2(
								'intent',
								$author$project$Effects$encodeIntent(transaction.aa))
							]))) : $elm$core$Maybe$Nothing;
			} else {
				return $elm$core$Maybe$Nothing;
			}
		},
		model.a.b._.fS);
};
var $author$project$OutcomeAnnouncements$observe = F3(
	function (before, after, prior) {
		var sequence = prior.a;
		var correlated = F3(
			function (kind, value, text) {
				return {
					cN: A2(
						$elm$json$Json$Encode$encode,
						0,
						$elm$json$Json$Encode$object(
							_List_fromArray(
								[
									_Utils_Tuple2(
									'outcome',
									$elm$json$Json$Encode$string(kind)),
									_Utils_Tuple2(
									'binding',
									A2(
										$elm$core$Maybe$withDefault,
										$elm$json$Json$Encode$null,
										A2($elm$core$Maybe$map, $author$project$Binding$encode, after.a.b.dk))),
									_Utils_Tuple2('identity', value)
								]))),
					cm: false,
					dd: text
				};
			});
		var candidate = function () {
			if ((!_Utils_eq(before.F, after.F)) && (!_Utils_eq(after.F, $elm$core$Maybe$Nothing))) {
				return A2(
					$elm$core$Maybe$map,
					function (notice) {
						return {
							cN: A2(
								$elm$json$Json$Encode$encode,
								0,
								$elm$json$Json$Encode$object(
									_List_fromArray(
										[
											_Utils_Tuple2(
											'outcome',
											$elm$json$Json$Encode$string('adapter-unavailable')),
											_Utils_Tuple2(
											'binding',
											$author$project$Binding$encode(notice.dk)),
											_Utils_Tuple2(
											'identity',
											$author$project$AdapterNotice$encode(notice))
										]))),
							cm: false,
							dd: $author$project$AdapterNotice$message(notice)
						};
					},
					after.F);
			} else {
				if (!_Utils_eq(
					$author$project$OutcomeAnnouncements$launch(before),
					$author$project$OutcomeAnnouncements$launch(after))) {
					return A2(
						$elm$core$Maybe$map,
						function (refusal) {
							var label = A2(
								$elm$core$Maybe$withDefault,
								refusal.d2,
								A2(
									$elm$core$Maybe$map,
									function ($) {
										return $.dA;
									},
									A2(
										$elm$core$Maybe$andThen,
										$author$project$Catalog$lookup(refusal.d2),
										after.aD)));
							return A3(
								correlated,
								'launch-refused',
								refusal.aa,
								'Launch refused for ' + (A2($elm$core$String$left, 512, label) + '. Refresh applications, then choose again.'));
						},
						$author$project$OutcomeAnnouncements$launch(after));
				} else {
					if (!_Utils_eq(
						$author$project$OutcomeAnnouncements$transfer(before),
						$author$project$OutcomeAnnouncements$transfer(after))) {
						return A2(
							$elm$core$Maybe$map,
							function (intent) {
								return A3(
									correlated,
									'transfer-refused',
									intent,
									$author$project$Surface$windowNotice(after));
							},
							$author$project$OutcomeAnnouncements$transfer(after));
					} else {
						if (!_Utils_eq(
							$author$project$OutcomeAnnouncements$settings(before),
							$author$project$OutcomeAnnouncements$settings(after))) {
							return A2(
								$elm$core$Maybe$map,
								function (request) {
									return A3(
										correlated,
										'settings-refused',
										$elm$json$Json$Encode$string(
											$author$project$UInt64$string(request)),
										after.aj.ft);
								},
								$author$project$OutcomeAnnouncements$settings(after));
						} else {
							if ((!_Utils_eq(before.C.cZ, after.C.cZ)) && (!after.C.fD.cP)) {
								return A2(
									$elm$core$Maybe$andThen,
									function (outcome) {
										return ((outcome.W === 'Refused') && outcome.bV) ? $elm$core$Maybe$Just(
											A3(
												correlated,
												'notification-expired-action-refused',
												$elm$json$Json$Encode$object(
													_List_fromArray(
														[
															_Utils_Tuple2(
															'request',
															$elm$json$Json$Encode$string(
																$author$project$UInt64$string(outcome.c1))),
															_Utils_Tuple2(
															'target',
															$author$project$Notifications$encodeIntent(outcome.fR))
														])),
												'Notification action refused because the target expired. Refresh notifications, then choose a current notification.')) : $elm$core$Maybe$Nothing;
									},
									after.C.cZ);
							} else {
								var expired = (_Utils_eq(before.a.b.dk, after.a.b.dk) && (!_Utils_eq(after.a.b.dk, $elm$core$Maybe$Nothing))) ? A2(
									$author$project$Notifications$expirations,
									before.t ? before.C : $author$project$Notifications$clearFocus(before.C),
									after.C) : _List_Nil;
								var expiryIdentity = A2(
									$elm$core$Maybe$withDefault,
									$elm$json$Json$Encode$null,
									A2(
										$elm$core$Maybe$map,
										function (snapshot) {
											return $elm$json$Json$Encode$object(
												_List_fromArray(
													[
														_Utils_Tuple2(
														'service',
														$elm$json$Json$Encode$string(
															$author$project$UInt64$string(snapshot.c7))),
														_Utils_Tuple2(
														'revision',
														$elm$json$Json$Encode$string(
															$author$project$UInt64$string(snapshot.c2))),
														_Utils_Tuple2(
														'incarnations',
														A2(
															$elm$json$Json$Encode$list,
															function (entry) {
																return $elm$json$Json$Encode$string(
																	$author$project$UInt64$string(entry.aq));
															},
															expired))
													]));
										},
										after.C.c));
								var expiryText = A2(
									$elm$core$String$join,
									'; ',
									A2(
										$elm$core$List$map,
										function (entry) {
											return A2(
												$elm$core$String$left,
												200,
												A2(
													$elm$core$String$join,
													' ',
													$elm$core$String$words(entry.dR + (': ' + entry.eS))));
										},
										A2($elm$core$List$take, 3, expired))) + ' expired. Its actions are unavailable. Refresh notifications for current history.';
								var clean = function (value) {
									return A2(
										$elm$core$String$join,
										' ',
										$elm$core$String$words(value));
								};
								var summary = function (entry) {
									return A2(
										$elm$core$String$left,
										200,
										clean(entry.dR + (': ' + entry.eS)));
								};
								var arrivals = (_Utils_eq(before.a.b.dk, after.a.b.dk) && (!_Utils_eq(after.a.b.dk, $elm$core$Maybe$Nothing))) ? A2($author$project$Notifications$arrivals, before.C, after.C) : _List_Nil;
								var details = _Utils_ap(
									A2(
										$elm$core$String$join,
										'; ',
										A2(
											$elm$core$List$map,
											summary,
											A2($elm$core$List$take, 3, arrivals))),
									($elm$core$List$length(arrivals) > 3) ? ('; and ' + ($elm$core$String$fromInt(
										$elm$core$List$length(arrivals) - 3) + ' more')) : '');
								var identity = A2(
									$elm$core$Maybe$withDefault,
									$elm$json$Json$Encode$null,
									A2(
										$elm$core$Maybe$map,
										function (snapshot) {
											return $elm$json$Json$Encode$object(
												_List_fromArray(
													[
														_Utils_Tuple2(
														'service',
														$elm$json$Json$Encode$string(
															$author$project$UInt64$string(snapshot.c7))),
														_Utils_Tuple2(
														'revision',
														$elm$json$Json$Encode$string(
															$author$project$UInt64$string(snapshot.c2))),
														_Utils_Tuple2(
														'incarnations',
														A2(
															$elm$json$Json$Encode$list,
															function (entry) {
																return $elm$json$Json$Encode$string(
																	$author$project$UInt64$string(entry.aq));
															},
															arrivals))
													]));
										},
										after.C.c));
								var event = A3(correlated, 'notification-arrival', identity, details + '. Open Notifications for details and current actions.');
								return (!$elm$core$List$isEmpty(expired)) ? $elm$core$Maybe$Just(
									A3(correlated, 'notification-expiration', expiryIdentity, expiryText)) : ($elm$core$List$isEmpty(arrivals) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(
									_Utils_update(
										event,
										{
											cm: after.C.fD.ef && A2($elm$core$List$all, $author$project$Notifications$critical, arrivals)
										})));
							}
						}
					}
				}
			}
		}();
		var _v0 = _Utils_Tuple2(
			candidate,
			$author$project$UInt64$next(sequence));
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var event = _v0.a.a;
			var next = _v0.b.a;
			return A2(
				$author$project$OutcomeAnnouncements$Model,
				next,
				$elm$core$Maybe$Just(
					{cN: event.cN, cm: event.cm, bN: next, dd: event.dd}));
		} else {
			return prior;
		}
	});
var $author$project$OutputController$track = F2(
	function (_v0, result) {
		var before = _v0;
		var after = result;
		return (!_Utils_eq(before.bS, after.bS)) ? result : _Utils_update(
			after,
			{
				bS: A3(
					$author$project$OutcomeAnnouncements$observe,
					$author$project$SurfaceController$desktop(before.cM),
					$author$project$SurfaceController$desktop(after.cM),
					after.bS)
			});
	});
var $author$project$Desktop$InvalidateSnap = {$: 7};
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
		return {dk: binding, fi: grantState, ej: kind, bh: operation, fG: protocolVersion, eG: queriedBinding, eK: requestId, fL: retirementProtocol, bN: sequence};
	});
var $elm$json$Json$Decode$andThen = _Json_andThen;
var $author$project$Binding$Binding = F3(
	function (a, b, c) {
		return {$: 0, a: a, b: b, c: c};
	});
var $elm$json$Json$Decode$fail = _Json_fail;
var $elm$json$Json$Decode$keyValuePairs = _Json_decodeKeyValuePairs;
var $elm$json$Json$Decode$map3 = _Json_map3;
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
								return A2($author$project$UInt64$compare, proof.bN, old.bN) === 2;
							},
							slot.eC));
				};
				var informationalScopeChanged = A2(
					$elm$core$Maybe$withDefault,
					false,
					A2(
						$elm$core$Maybe$map,
						function (active) {
							return !_Utils_eq(active.eG, proof.eG);
						},
						model.bf));
				var eligible = function (slot) {
					return _Utils_eq(slot.eI.dk, proof.eG) && A2($author$project$Binding$sameLifetime, slot.eI.aa.P.fp, current);
				};
				var anotherActiveScope = A2(
					$elm$core$List$any,
					function (slot) {
						return (!slot.c0) && A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (active) {
									return !_Utils_eq(active.eG, proof.eG);
								},
								slot.eC));
					},
					model.N);
				return (anotherActiveScope || (informationalScopeChanged || ((!_Utils_eq(proof.dk, current)) || (_Utils_eq(proof.eG, current) || ((!A2($elm$core$List$any, eligible, model.N)) || (!A2(
					$elm$core$List$all,
					function (slot) {
						return (!eligible(slot)) || newer(slot);
					},
					model.N))))))) ? $elm$core$Result$Err('Uncorrelated proof announcement') : $elm$core$Result$Ok(
					_Utils_update(
						model,
						{
							bf: A2(
								$elm$core$List$any,
								function (slot) {
									return eligible(slot) && (!slot.c0);
								},
								model.N) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(proof),
							N: A2(
								$elm$core$List$map,
								function (slot) {
									return eligible(slot) ? _Utils_update(
										slot,
										{
											e3: $elm$core$Maybe$Nothing,
											bR: $elm$core$Maybe$Nothing,
											ap: $elm$core$Maybe$Nothing,
											bd: $elm$core$Maybe$Nothing,
											eC: $elm$core$Maybe$Just(proof)
										}) : slot;
								},
								model.N)
						}));
			},
			A2(
				$elm$core$Result$mapError,
				$elm$json$Json$Decode$errorToString,
				A2($elm$json$Json$Decode$decodeValue, $author$project$ReconciliationFrame$proofDecoder, raw)));
	});
var $author$project$Switcher$generation = function (_v0) {
	var model = _v0;
	return model.fh;
};
var $author$project$AdapterNotice$ApplicationActions = 3;
var $author$project$AdapterNotice$Applications = 0;
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
var $author$project$AdapterNotice$Files = 2;
var $author$project$Desktop$Focus = function (a) {
	return {$: 4, a: a};
};
var $author$project$Shell$Incoming = function (a) {
	return {$: 3, a: a};
};
var $author$project$Menu$Invalidate = function (a) {
	return {$: 6, a: a};
};
var $author$project$AdapterNotice$Motion = 6;
var $author$project$AdapterNotice$Notifications = 1;
var $author$project$TaskbarShell$OpenMenu = function (a) {
	return {$: 4, a: a};
};
var $author$project$Desktop$OverviewOpener = {$: 1};
var $author$project$Desktop$ScopedShortcut = F2(
	function (a, b) {
		return {$: 9, a: a, b: b};
	});
var $author$project$AdapterNotice$Settings = 5;
var $author$project$AdapterNotice$Shortcuts = 7;
var $author$project$AdapterNotice$System = 4;
var $author$project$Desktop$TaskbarGroup = function (a) {
	return {$: 0, a: a};
};
var $author$project$Launch$advance = function (_v0) {
	var model = _v0;
	var _v1 = $author$project$UInt64$next(model.c2);
	if (!_v1.$) {
		var revision = _v1.a;
		return _Utils_update(
			model,
			{c2: revision});
	} else {
		return _Utils_update(
			model,
			{be: $elm$core$Maybe$Nothing, c: $elm$core$Maybe$Nothing});
	}
};
var $author$project$Launch$acknowledgeUnknown = F2(
	function (_v0, current) {
		var intent = _v0;
		var model = current;
		var _v1 = model.j;
		if ((_v1.$ === 2) && (_v1.b === 2)) {
			var active = _v1.a;
			var _v2 = _v1.b;
			return _Utils_eq(active, intent) ? $author$project$Launch$advance(
				_Utils_update(
					model,
					{j: $author$project$Launch$Idle})) : current;
		} else {
			return current;
		}
	});
var $author$project$TaskView$activeWorkspace = function (shell) {
	return A2(
		$elm$core$Maybe$map,
		function ($) {
			return $.cU;
		},
		A2(
			$elm$core$Maybe$andThen,
			A2(
				$elm$core$Basics$composeR,
				$elm$core$List$filter(
					function ($) {
						return $.bt;
					}),
				$elm$core$List$head),
			$author$project$TaskView$groups(shell)));
};
var $author$project$Switcher$Cancelled = 4;
var $author$project$Switcher$writable = function (model) {
	return A2(
		$elm$core$List$member,
		model.j,
		_List_fromArray(
			[1, 2]));
};
var $author$project$Switcher$cancel = F2(
	function (token, original) {
		var model = original;
		return ((!_Utils_eq(token, model.fh)) || (!$author$project$Switcher$writable(model))) ? original : _Utils_update(
			model,
			{af: _List_Nil, j: 4});
	});
var $author$project$Desktop$retireSwitcher = function (model) {
	return _Utils_update(
		model,
		{
			i: A2(
				$author$project$Switcher$cancel,
				$author$project$Switcher$generation(model.i),
				model.i),
			aR: $elm$core$Maybe$Nothing,
			aS: $elm$core$Maybe$Nothing,
			cw: $elm$core$Maybe$Nothing
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
				{aD: $elm$core$Maybe$Nothing, A: $elm$core$Maybe$Nothing, q: false, m: false, aO: $elm$core$Maybe$Nothing}));
	}
};
var $author$project$OverviewRecovery$Choosing = F2(
	function (a, b) {
		return {$: 1, a: a, b: b};
	});
var $author$project$OverviewRecovery$begin = $author$project$OverviewRecovery$Choosing;
var $author$project$PointerOwnership$Idle = 0;
var $author$project$PointerOwnership$blocked = F2(
	function (expected, model) {
		if (expected.$ === 1) {
			return false;
		} else {
			var binding = expected.a;
			var _v1 = model.bF;
			if (!_v1.$) {
				var snapshot = _v1.a;
				return (!_Utils_eq(snapshot.dk, binding)) || (!(!snapshot.dc));
			} else {
				return true;
			}
		}
	});
var $author$project$Desktop$canProveCatalogUnsent = F3(
	function (binding, request, model) {
		return _Utils_eq(
			model.a.b.dk,
			$elm$core$Maybe$Just(binding)) && (_Utils_eq(
			model.A,
			$elm$core$Maybe$Just(request)) && ((!(!model.a.b.j)) && (model.a.b.j !== 3)));
	});
var $author$project$OverviewRecovery$cancelChoice = F2(
	function (read, model) {
		if (model.$ === 1) {
			var expected = model.b;
			return _Utils_eq(read, expected) ? $author$project$OverviewRecovery$Idle : model;
		} else {
			return model;
		}
	});
var $author$project$Catalog$Snapshot = F3(
	function (a, b, c) {
		return {$: 0, a: a, b: b, c: c};
	});
var $author$project$Catalog$Entry = F6(
	function (identity, name, iconHint, wmclass, genericName, keywords) {
		return {d9: genericName, fk: iconHint, cU: identity, ei: keywords, dA: name, fW: wmclass};
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
							$author$project$Catalog$id(entry.cU),
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
			var _v1 = _Utils_Tuple2(snapshot, model.j);
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
			return model.j;
		}();
		return $author$project$Launch$advance(
			_Utils_update(
				model,
				{j: phase, c: snapshot}));
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
						return _Utils_eq(row.r, root);
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
			$elm$core$Dict$keys(model.bO)));
};
var $author$project$Switcher$choose = F3(
	function (token, root, original) {
		var model = original;
		return ((!_Utils_eq(token, model.fh)) || ((model.j !== 2) || (!_Utils_eq(model.c0, $elm$core$Maybe$Nothing)))) ? original : A2(
			$elm$core$Maybe$withDefault,
			original,
			A2(
				$elm$core$Maybe$map,
				function (position) {
					return _Utils_update(
						model,
						{
							ba: $elm$core$Maybe$Just(
								{
									r: root,
									df: $author$project$Switcher$lastOrdinal(model)
								}),
							fN: position
						});
				},
				A2($author$project$Switcher$index, root, model.af)));
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
	var _v1 = model.j;
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
		var _v1 = model.j;
		if (_v1.$ === 1) {
			var owner = _v1.a;
			var active = _v1.b;
			return (_Utils_eq(owner, host) && _Utils_eq(active, intent)) ? $author$project$Launch$advance(
				_Utils_update(
					model,
					{
						j: A2($author$project$Launch$Settled, intent, 2)
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
			{be: $elm$core$Maybe$Nothing, c: $elm$core$Maybe$Nothing}));
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
				model.be,
				$elm$core$Maybe$Just(host))) {
				return current;
			} else {
				var _v0 = $author$project$Launch$disconnect(current);
				var retired = _v0;
				return $author$project$Launch$advance(
					_Utils_update(
						retired,
						{
							be: $elm$core$Maybe$Just(host)
						}));
			}
		}
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
var $author$project$AdapterNotice$Windows = 8;
var $author$project$AdapterNotice$connectionLost = F2(
	function (binding, request) {
		return {dk: binding, c1: request, c2: $elm$core$Maybe$Nothing, c7: $elm$core$Maybe$Nothing, cv: 8};
	});
var $author$project$Files$disconnect = function (model) {
	return _Utils_update(
		model,
		{
			ft: (!_Utils_eq(model.ex, $elm$core$Maybe$Nothing)) ? 'Files: opening not confirmed after connection loss. Open the menu to read current state; this request will not be repeated.' : model.ft,
			ex: $elm$core$Maybe$Nothing,
			c: $elm$core$Maybe$Nothing,
			ca: _List_Nil
		});
};
var $author$project$JumpList$disconnect = function (model) {
	return _Utils_update(
		model,
		{
			ft: (!_Utils_eq(model.ex, $elm$core$Maybe$Nothing)) ? 'Application action: not confirmed after connection loss. This request will not be repeated.' : model.ft,
			ex: $elm$core$Maybe$Nothing,
			c: $elm$core$Maybe$Nothing,
			ca: _List_Nil
		});
};
var $author$project$Desktop$motionPreferencesRequest = F2(
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
						$elm$json$Json$Encode$string('motion-preferences-request')),
						_Utils_Tuple2(
						'binding',
						$author$project$Binding$encode(binding)),
						_Utils_Tuple2(
						'requestId',
						$elm$json$Json$Encode$string(
							$author$project$UInt64$string(request)))
					])));
	});
var $author$project$Motion$rebind = function (model) {
	return _Utils_update(
		model,
		{bT: $elm$core$Maybe$Nothing, ex: $elm$core$Maybe$Nothing, a1: $author$project$MotionPreferences$initial});
};
var $author$project$Desktop$settingsRequest = F2(
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
						$elm$json$Json$Encode$string('shell-settings-request')),
						_Utils_Tuple2(
						'binding',
						$author$project$Binding$encode(binding)),
						_Utils_Tuple2(
						'requestId',
						$elm$json$Json$Encode$string(
							$author$project$UInt64$string(request)))
					])));
	});
var $author$project$Desktop$shortcutPreferencesRequest = F2(
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
						$elm$json$Json$Encode$string('shortcut-preferences-request')),
						_Utils_Tuple2(
						'binding',
						$author$project$Binding$encode(binding)),
						_Utils_Tuple2(
						'requestId',
						$elm$json$Json$Encode$string(
							$author$project$UInt64$string(request)))
					])));
	});
var $author$project$Shell$Act = F3(
	function (a, b, c) {
		return {$: 9, a: a, b: b, c: c};
	});
var $author$project$Menu$ExitFullscreen = {$: 7};
var $author$project$Menu$Maximize = {$: 5};
var $author$project$Menu$RestoreGeometry = {$: 1};
var $author$project$Provider$actionProtocol = function (action) {
	return (_Utils_eq(action, $author$project$Menu$Maximize) || (_Utils_eq(action, $author$project$Menu$RestoreGeometry) || (_Utils_eq(action, $author$project$Menu$ExitFullscreen) || function () {
		if (action.$ === 8) {
			return true;
		} else {
			return false;
		}
	}()))) ? 2 : 1;
};
var $author$project$MenuBridge$answer = F4(
	function (bridge, shell, effects, error) {
		return {dW: bridge, _: effects, d3: error, b: shell};
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
					return item.fd ? $elm$core$Maybe$Just(index) : $elm$core$Maybe$Nothing;
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
		var enabled = $author$project$Menu$enabledIndices(menu.fo);
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
					var _v1 = menu.fN;
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
					var _v2 = menu.fN;
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
			{fN: selected});
	});
var $author$project$Menu$outputTuple = function (_v0) {
	var value = _v0;
	return _Utils_Tuple2(value.y, value.fw);
};
var $author$project$Menu$sameTarget = F2(
	function (_v0, _v1) {
		var left = _v0;
		var right = _v1;
		return _Utils_eq(left.fR, right.fR);
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
					if (A2($elm$core$List$member, item.e3, seen)) {
						return false;
					} else {
						var $temp$remaining = rest,
							$temp$seen = A2($elm$core$List$cons, item.e3, seen);
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
				$elm$core$String$length(item.el),
				$author$project$Menu$maxLabel) < 1) && (!$elm$core$String$isEmpty(
				$elm$core$String$trim(item.el)));
		},
		items) && A2(uniqueActions, items, _List_Nil));
};
var $author$project$Menu$update = F2(
	function (message, model) {
		var state = model;
		var valid = function (target) {
			return (!A2($elm$core$List$member, target, state.aY)) && (!A2(
				$elm$core$List$member,
				$author$project$Menu$outputTuple(target),
				state.a3));
		};
		var unchanged = _Utils_Tuple2(model, _List_Nil);
		var editMenu = F2(
			function (id, transform) {
				var _v8 = state.aI;
				if (!_v8.$) {
					var menu = _v8.a;
					return _Utils_eq(menu.cl, id) ? _Utils_Tuple2(
						_Utils_update(
							state,
							{
								aI: transform(menu)
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
				if (state.az || ((!valid(target)) || ((!$author$project$Menu$validItems(items)) || (state.cs > 2147483647)))) {
					return unchanged;
				} else {
					var status = function () {
						var _v1 = $elm$core$List$head(
							A2(
								$elm$core$List$filter,
								function (entry) {
									return A2($author$project$Menu$sameTarget, entry.dk, target);
								},
								state.fx));
						if (_v1.$ === 1) {
							return $author$project$Menu$Ready;
						} else {
							var entry = _v1.a;
							return entry.bq ? $author$project$Menu$Unknown(entry.cl) : $author$project$Menu$Pending(entry.cl);
						}
					}();
					var menu = {
						dk: target,
						cl: state.cs,
						fo: items,
						fN: $elm$core$List$head(
							$author$project$Menu$enabledIndices(items)),
						W: status
					};
					return _Utils_Tuple2(
						_Utils_update(
							state,
							{
								aI: $elm$core$Maybe$Just(menu),
								cs: state.cs + 1
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
						if (_Utils_eq(menu.dk, target) && valid(target)) {
							var _v2 = A2($author$project$Menu$itemAt, index, menu.fo);
							if (!_v2.$) {
								var item = _v2.a;
								return item.fd ? $elm$core$Maybe$Just(
									_Utils_update(
										menu,
										{
											fN: $elm$core$Maybe$Just(index)
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
				var _v3 = state.aI;
				if (_v3.$ === 1) {
					return unchanged;
				} else {
					var menu = _v3.a;
					if (state.az || ((!_Utils_eq(menu.cl, id)) || ((!_Utils_eq(menu.dk, target)) || ((!valid(target)) || (state.cr > 2147483647))))) {
						return unchanged;
					} else {
						if (A2(
							$elm$core$List$any,
							function (entry) {
								return A2($author$project$Menu$sameTarget, entry.dk, target);
							},
							state.fx)) {
							return unchanged;
						} else {
							var _v4 = A2($author$project$Menu$itemAt, index, menu.fo);
							if (!_v4.$) {
								var item = _v4.a;
								if (item.fd && (_Utils_cmp(
									$elm$core$List$length(state.fx),
									$author$project$Menu$maxOutstanding) > -1)) {
									return _Utils_Tuple2(
										_Utils_update(
											state,
											{
												aI: $elm$core$Maybe$Just(
													_Utils_update(
														menu,
														{
															W: $author$project$Menu$Refused('Outstanding operation limit reached; reconcile existing requests.')
														}))
											}),
										_List_Nil);
								} else {
									if (item.fd) {
										var intent = state.cr;
										var entry = {dk: target, cl: intent, bq: false};
										return _Utils_Tuple2(
											_Utils_update(
												state,
												{
													aI: $elm$core$Maybe$Just(
														_Utils_update(
															menu,
															{
																fN: $elm$core$Maybe$Just(index),
																W: $author$project$Menu$Pending(intent)
															})),
													cr: state.cr + 1,
													fx: A2($elm$core$List$cons, entry, state.fx)
												}),
											_List_fromArray(
												[
													A3($author$project$Menu$Dispatch, intent, target, item.e3)
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
							return _Utils_eq(entry.cl, intent) && _Utils_eq(entry.dk, receiptBinding);
						},
						state.fx));
				if (_v5.$ === 1) {
					return unchanged;
				} else {
					var entry = _v5.a;
					var outcome = $author$project$Menu$boundedOutcome(receivedOutcome);
					var outstanding = _Utils_eq(outcome, $author$project$Menu$Uncertain) ? A2(
						$elm$core$List$map,
						function (current) {
							return _Utils_eq(current.cl, intent) ? _Utils_update(
								current,
								{bq: true}) : current;
						},
						state.fx) : A2(
						$elm$core$List$filter,
						function (current) {
							return !_Utils_eq(current.cl, intent);
						},
						state.fx);
					var menu = A2(
						$elm$core$Maybe$andThen,
						function (current) {
							if (!A2($author$project$Menu$awaits, intent, current.W)) {
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
													W: $author$project$Menu$Refused(reason)
												}));
									case 2:
										return $elm$core$Maybe$Just(
											_Utils_update(
												current,
												{W: $author$project$Menu$Cancelled}));
									default:
										return $elm$core$Maybe$Just(
											_Utils_update(
												current,
												{
													W: $author$project$Menu$Unknown(intent)
												}));
								}
							}
						},
						state.aI);
					return _Utils_Tuple2(
						_Utils_update(
							state,
							{
								co: $elm$core$Maybe$Just(
									_Utils_Tuple2(intent, outcome)),
								aI: menu,
								fx: outstanding
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
				if (A2($elm$core$List$member, target, state.aY) || state.az) {
					return unchanged;
				} else {
					if (_Utils_cmp(
						$elm$core$List$length(state.aY) + $elm$core$List$length(state.a3),
						$author$project$Menu$maxRetired) > -1) {
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{az: true, aI: $elm$core$Maybe$Nothing}),
							_List_Nil);
					} else {
						var menu = A2(
							$elm$core$Maybe$andThen,
							function (current) {
								return _Utils_eq(current.dk, target) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(current);
							},
							state.aI);
						var invalidated = A2($elm$core$List$cons, target, state.aY);
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{aY: invalidated, aI: menu}),
							_List_Nil);
					}
				}
			default:
				var output = message.a;
				var generation = message.b;
				var retired = _Utils_Tuple2(output, generation);
				if (A2($elm$core$List$member, retired, state.a3) || state.az) {
					return unchanged;
				} else {
					if (_Utils_cmp(
						$elm$core$List$length(state.aY) + $elm$core$List$length(state.a3),
						$author$project$Menu$maxRetired) > -1) {
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{az: true, aI: $elm$core$Maybe$Nothing}),
							_List_Nil);
					} else {
						var retiredOutputs = A2($elm$core$List$cons, retired, state.a3);
						var menu = A2(
							$elm$core$Maybe$andThen,
							function (current) {
								return _Utils_eq(
									$author$project$Menu$outputTuple(current.dk),
									retired) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(current);
							},
							state.aI);
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{aI: menu, a3: retiredOutputs}),
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
			state.aI);
		var menu = _v1.a;
		return _Utils_update(
			state,
			{aI: menu});
	});
var $author$project$Shell$Reconciling = 1;
var $author$project$Shell$Send = function (a) {
	return {$: 0, a: a};
};
var $author$project$Shell$refresh = function (model) {
	var _v0 = _Utils_Tuple2(
		model.dk,
		$author$project$UInt64$next(model.c1));
	if ((!_v0.a.$) && (!_v0.b.$)) {
		var binding = _v0.a.a;
		var request = _v0.b.a;
		return ((!model.j) || model.X) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
			_Utils_update(
				model,
				{
					A: $elm$core$Maybe$Just(request),
					j: 1,
					a2: false,
					c1: request
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
				{A: $elm$core$Maybe$Nothing, ft: 'Restart the shell to continue.', j: 3, a2: false}),
			_List_Nil);
	}
};
var $author$project$Shell$geometryRequest = F2(
	function (attach, model) {
		if (model.X) {
			return _Utils_Tuple2(model, _List_Nil);
		} else {
			var _v0 = _Utils_Tuple2(
				model.dk,
				$author$project$UInt64$next(model.c1));
			if ((!_v0.a.$) && (!_v0.b.$)) {
				var binding = _v0.a.a;
				var request = _v0.b.a;
				if ((!model.j) || ((attach && (!_Utils_eq(model.ea, $elm$core$Maybe$Nothing))) || ((!attach) && (_Utils_eq(model.ds, $elm$core$Maybe$Nothing) || (!_Utils_eq(model.eb, $elm$core$Maybe$Nothing)))))) {
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
							$elm$json$Json$Encode$int(3)),
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
													return $.bN;
												},
												$author$project$UInt64$string),
											model.ap))))
							]));
					return _Utils_Tuple2(
						_Utils_update(
							model,
							{
								am: attach || model.am,
								ea: attach ? $elm$core$Maybe$Just(request) : model.ea,
								eb: attach ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(request),
								c1: request
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
				return $._;
			},
			model.ds));
};
var $author$project$Shell$refreshObservations = function (model) {
	if (model.X) {
		return _Utils_Tuple2(model, _List_Nil);
	} else {
		var _v0 = $author$project$Shell$refresh(
			_Utils_update(
				model,
				{aA: false}));
		var legacy = _v0.a;
		var commands = _v0.b;
		if (legacy.am) {
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
	return model.a2 ? (((!model.j) || ((model.j === 3) || _Utils_eq(model.dk, $elm$core$Maybe$Nothing))) ? _Utils_Tuple2(
		_Utils_update(
			model,
			{a2: false}),
		_List_Nil) : ((model.X || (model.d$ || ($author$project$Effects$pending(model._) || ((!_Utils_eq(model.A, $elm$core$Maybe$Nothing)) || (!_Utils_eq(model.ea, $elm$core$Maybe$Nothing)))))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$refresh(model))) : (((!model.X) && ((!model.d$) && (model.aA && ((model.j === 2) && ((!$author$project$Effects$pending(model._)) && (_Utils_eq(model.A, $elm$core$Maybe$Nothing) && (_Utils_eq(model.eb, $elm$core$Maybe$Nothing) && _Utils_eq(model.ea, $elm$core$Maybe$Nothing)))))))) ? $author$project$Shell$refreshObservations(model) : _Utils_Tuple2(model, _List_Nil));
};
var $author$project$Shell$resumeNotifications = function (model) {
	return $author$project$Shell$drainNotifications(
		_Utils_update(
			model,
			{d$: false}));
};
var $author$project$MenuBridge$cancelPrepared = F3(
	function (reason, shell, model) {
		var state = model;
		var _v0 = state.O;
		if (_v0.$ === 1) {
			return A4($author$project$MenuBridge$answer, model, shell, _List_Nil, $elm$core$Maybe$Nothing);
		} else {
			var slot = _v0.a;
			var cleared = A4(
				$author$project$MenuBridge$refuse,
				slot.cq,
				slot.b0,
				reason,
				_Utils_update(
					state,
					{O: $elm$core$Maybe$Nothing}));
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
			return A3($author$project$Shell$Stamp, observed.dk, observed.P.y, observed.P.c2);
		},
		model.ap);
};
var $author$project$Provider$nativeContext = function (_v0) {
	var value = _v0;
	return {fe: value.P.d8, fp: value.P.fp, y: value.P.fw, c2: value.P.c2};
};
var $author$project$MenuBridge$sameWindowFacts = F2(
	function (before, after) {
		var ordered = $elm$core$List$sortWith(
			F2(
				function (a, b) {
					return A2($author$project$UInt64$compare, a.aq, b.aq);
				}));
		return _Utils_eq(
			ordered(before),
			ordered(after));
	});
var $author$project$MenuBridge$compatiblePrepared = F2(
	function (slot, shell) {
		var original = slot.ax.c;
		var sameGeometry = function () {
			var _v0 = _Utils_Tuple2(
				$author$project$Provider$geometryObservation(original),
				shell.ap);
			if (_v0.a.$ === 1) {
				var _v1 = _v0.a;
				return _Utils_eq(slot.bd, $elm$core$Maybe$Nothing);
			} else {
				if (!_v0.b.$) {
					var before = _v0.a.a;
					var after = _v0.b.a;
					return _Utils_eq(before.dk, after.dk) && (_Utils_eq(before.P.fp, after.P.fp) && (_Utils_eq(before.P.fe, after.P.fe) && (_Utils_eq(before.P.y, after.P.y) && ((!(!A2($author$project$UInt64$compare, after.P.c2, before.P.c2))) && ((!(!A2($author$project$UInt64$compare, after.bN, before.bN))) && ((!after.e6) && A2($author$project$MenuBridge$sameWindowFacts, before.a, after.a)))))));
				} else {
					return false;
				}
			}
		}();
		var old = $author$project$Provider$nativeContext(original);
		var legacy = shell._.as;
		var sameLegacy = A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (observed) {
					return _Utils_eq(observed.P.fp, old.fp) && (_Utils_eq(observed.P.fe, old.fe) && (_Utils_eq(observed.P.y, old.y) && ((!(!A2($author$project$UInt64$compare, observed.P.c2, old.c2))) && (A2(
						$author$project$MenuBridge$sameWindowFacts,
						$author$project$ActionProjection$windows(observed.eN),
						slot.dw) && _Utils_eq(
						A2(
							$author$project$ActionProjection$rootOf,
							$author$project$Provider$incarnation(original),
							observed.eN),
						$elm$core$Maybe$Just(
							$author$project$Provider$incarnation(original)))))));
				},
				legacy));
		return _Utils_eq(
			shell.dk,
			$elm$core$Maybe$Just(
				$author$project$Provider$nativeBinding(original))) && (_Utils_eq(shell.ds, slot.ds) && (sameLegacy && sameGeometry));
	});
var $author$project$NativeProvider$counter = A2($elm$core$Basics$composeR, $author$project$UInt64$string, $elm$json$Json$Encode$string);
var $author$project$Provider$Raw = F7(
	function (provider, capabilitiesGeneration, context, target, heading, capabilities, entries) {
		return {cI: capabilities, dm: capabilitiesGeneration, P: context, af: entries, ed: heading, bJ: provider, fR: target};
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
		return {d8: frontend, fp: lifetime, er: _native, fw: outputGeneration, dC: outputId, c2: revision, fO: session};
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
					cl: $author$project$UInt64$string(identity),
					cn: {e3: action, fd: enabled, el: label},
					ej: kind
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
		return {aq: incarnation, fp: lifetime, fO: session};
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
					return entry.cn.fd && (!A2($elm$core$List$member, entry.ej, raw.cI));
				},
				raw.af);
			var identities = A2(
				$elm$core$List$map,
				function ($) {
					return $.cl;
				},
				raw.af);
			var duplicateIds = !_Utils_eq(
				$elm$core$List$length(identities),
				$elm$core$Set$size(
					$elm$core$Set$fromList(identities)));
			var duplicateCapabilities = !_Utils_eq(
				$elm$core$List$length(raw.cI),
				$elm$core$Set$size(
					$elm$core$Set$fromList(raw.cI)));
			var coherent = _Utils_eq(raw.fR.fp, raw.P.fp) && _Utils_eq(raw.fR.fO, raw.P.fO);
			var authority = A2(
				$elm$json$Json$Encode$encode,
				0,
				A2(
					$elm$json$Json$Encode$list,
					$elm$core$Basics$identity,
					_List_fromArray(
						[
							$author$project$Binding$encode(raw.P.er),
							$elm$json$Json$Encode$string(
							$author$project$UInt64$string(raw.bJ)),
							$elm$json$Json$Encode$string(
							$author$project$UInt64$string(raw.dm))
						])));
			var actions = A2(
				$elm$core$List$map,
				A2(
					$elm$core$Basics$composeR,
					function ($) {
						return $.cn;
					},
					function ($) {
						return $.e3;
					}),
				raw.af);
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
					dk: $author$project$Menu$binding(
						{
							dT: authority,
							y: $author$project$Menu$outputId(
								$author$project$UInt64$string(raw.P.dC)),
							fw: $author$project$UInt64$string(raw.P.fw),
							c2: $author$project$UInt64$string(raw.P.c2),
							fR: $author$project$Menu$Window(
								A2(
									$author$project$Menu$windowId,
									$author$project$Binding$authorityIdentity(raw.P.er),
									$author$project$UInt64$string(raw.fR.aq)))
						}),
					e7: raw.dm,
					P: raw.P,
					ap: $elm$core$Maybe$Nothing,
					aq: raw.fR.aq,
					fo: A2(
						$elm$core$List$map,
						function ($) {
							return $.cn;
						},
						raw.af),
					dI: raw.bJ,
					cA: raw.ed
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
		if (_Utils_eq(scope.dC, $author$project$UInt64$zero) || (_Utils_eq(scope.dI, $author$project$UInt64$zero) || _Utils_eq(scope.e7, $author$project$UInt64$zero))) {
			return $elm$core$Result$Err('Missing registered provider/output identity');
		} else {
			if (shell.j !== 2) {
				return $elm$core$Result$Err('Native window facts are not ready');
			} else {
				var _v0 = _Utils_Tuple2(shell.dk, shell._.as);
				if ((!_v0.a.$) && (!_v0.b.$)) {
					var binding = _v0.a.a;
					var observed = _v0.b.a;
					if (!A3($author$project$Binding$matchesContext, observed.P.fp, observed.P.fe, binding)) {
						return $elm$core$Result$Err('Native observation binding mismatch');
					} else {
						var _v1 = A2(
							$elm$core$Maybe$andThen,
							function (root) {
								return $elm$core$List$head(
									A2(
										$elm$core$List$filter,
										function (window) {
											return _Utils_eq(window.aq, root);
										},
										$author$project$ActionProjection$windows(observed.eN)));
							},
							A2($author$project$ActionProjection$rootOf, incarnation, observed.eN));
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
												$author$project$NativeProvider$counter(scope.dI)),
												_Utils_Tuple2(
												'capabilityGeneration',
												$author$project$NativeProvider$counter(scope.e7)),
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
															$author$project$NativeProvider$counter(observed.P.c2)),
															_Utils_Tuple2(
															'outputId',
															$author$project$NativeProvider$counter(scope.dC)),
															_Utils_Tuple2(
															'outputGeneration',
															$author$project$NativeProvider$counter(observed.P.y))
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
															$author$project$NativeProvider$counter(window.aq))
														]))),
												_Utils_Tuple2(
												'title',
												$elm$json$Json$Encode$string(
													($elm$core$String$trim(window.el) === '') ? 'Window actions' : window.el)),
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
															A4(item, '1', 'Restore', window.dj && window.b_, 'Restore'),
															A4(item, '2', 'Minimize', window.dj && (!window.b_), 'Minimize')
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
					return _Utils_eq(w.aq, identity);
				},
				rows));
	});
var $author$project$ActionProjection$minimized = F2(
	function (identity, projection) {
		return A2(
			$elm$core$Maybe$map,
			function ($) {
				return $.b_;
			},
			A2(
				$author$project$ActionProjection$find,
				identity,
				$author$project$ActionProjection$windows(projection)));
	});
var $author$project$GeometryProjection$Fullscreen = 2;
var $author$project$GeometryProjection$canExitFullscreen = function (row) {
	return (row.es === 2) && ((row.cg === 2) && (_Utils_eq(row.dD, $elm$core$Maybe$Nothing) && ((!row.bB) && ((!row.b_) && ((!_Utils_eq(row.e$, $elm$core$Maybe$Nothing)) && ((!_Utils_eq(row.b$, $elm$core$Maybe$Nothing)) && A2(
		$elm$core$Maybe$withDefault,
		false,
		A2(
			$elm$core$Maybe$map,
			function (pin) {
				return !pin.fB;
			},
			row.dF))))))));
};
var $author$project$Provider$withGeometry = F3(
	function (caps, observed, snapshot) {
		var state = snapshot;
		if ((!_Utils_eq(observed.dk, state.P.er)) || (!_Utils_eq(observed.P.y, state.P.fw))) {
			return $elm$core$Result$Err('Geometry/legacy authority mismatch');
		} else {
			var _v0 = A2($author$project$GeometryProjection$window, state.aq, observed);
			if (_v0.$ === 1) {
				return $elm$core$Result$Err('Geometry target missing');
			} else {
				var window = _v0.a;
				var supported = function (op) {
					return caps._ && A2($elm$core$List$member, op, caps.ev);
				};
				var restoreGeometry = supported('restore-geometry') && (!window.b_);
				var ready = A2(
					$elm$core$List$any,
					function ($) {
						return $.fd;
					},
					state.fo) && ((!observed.e6) && (window.dr && (!window.fg)));
				var pinItems = A2(
					$elm$core$Maybe$withDefault,
					_List_Nil,
					A2(
						$elm$core$Maybe$map,
						function (pin) {
							return (supported('pin') && supported('unpin')) ? _List_fromArray(
								[
									{
									e3: $author$project$Menu$AlwaysOnTop(!pin.fB),
									fd: (!observed.e6) && pin.dr,
									el: 'Always on top'
								}
								]) : _List_Nil;
						},
						window.dF));
				var legacyRestore = $elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (item) {
							return _Utils_eq(item.e3, $author$project$Menu$Restore);
						},
						state.fo));
				var restore = restoreGeometry ? {e3: $author$project$Menu$RestoreGeometry, fd: ready && (window.fI && ((window.es === 1) && window.fC)), el: 'Restore'} : A2(
					$elm$core$Maybe$withDefault,
					{e3: $author$project$Menu$Restore, fd: false, el: 'Restore'},
					legacyRestore);
				var legacyMinimize = $elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (item) {
							return _Utils_eq(item.e3, $author$project$Menu$Minimize);
						},
						state.fo));
				var minimize = A2(
					$elm$core$Maybe$withDefault,
					{e3: $author$project$Menu$Minimize, fd: false, el: 'Minimize'},
					legacyMinimize);
				var exitItems = (supported('exit-fullscreen') && (window.es === 2)) ? _List_fromArray(
					[
						{
						e3: $author$project$Menu$ExitFullscreen,
						fd: A2(
							$elm$core$List$any,
							function ($) {
								return $.fd;
							},
							state.fo) && ((!observed.e6) && $author$project$GeometryProjection$canExitFullscreen(window)),
						el: 'Exit fullscreen'
					}
					]) : _List_Nil;
				var items = _Utils_ap(
					_List_fromArray(
						[restore, minimize]),
					_Utils_ap(
						exitItems,
						_Utils_ap(
							pinItems,
							supported('maximize') ? _List_fromArray(
								[
									{e3: $author$project$Menu$Maximize, fd: ready && (window.fr && ((!window.b_) && (!window.es))), el: 'Maximize'}
								]) : _List_Nil)));
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
									$author$project$Binding$encode(state.P.er)) + (':' + ($author$project$UInt64$string(state.dI) + (':' + ($author$project$UInt64$string(state.e7) + (':' + $author$project$UInt64$string(state.P.c2))))))),
								$elm$json$Json$Encode$string(
								$author$project$UInt64$string(observed.P.c2)),
								$elm$json$Json$Encode$string(
								$author$project$UInt64$string(observed.P.y)),
								A2($elm$json$Json$Encode$list, $elm$json$Json$Encode$string, caps.ev)
							])));
				return $elm$core$Result$Ok(
					_Utils_update(
						state,
						{
							dk: $author$project$Menu$binding(
								{
									dT: authority,
									y: $author$project$Menu$outputId(
										$author$project$UInt64$string(state.P.dC)),
									fw: $author$project$UInt64$string(observed.P.y),
									c2: $author$project$UInt64$string(observed.P.c2),
									fR: $author$project$Menu$Window(
										A2(
											$author$project$Menu$windowId,
											$author$project$Binding$authorityIdentity(state.P.er),
											$author$project$UInt64$string(state.aq)))
								}),
							ap: $elm$core$Maybe$Just(observed),
							fo: items
						}));
			}
		}
	});
var $author$project$NativeProvider$fromShell = F3(
	function (scope, incarnation, shell) {
		return A2(
			$elm$core$Result$andThen,
			function (legacy) {
				var _v0 = shell.ds;
				if (_v0.$ === 1) {
					return $elm$core$Result$Ok(legacy);
				} else {
					var caps = _v0.a;
					if (!caps._) {
						return $elm$core$Result$Ok(legacy);
					} else {
						var _v1 = _Utils_Tuple3(shell.ap, shell.eb, shell._.as);
						if (((!_v1.a.$) && (_v1.b.$ === 1)) && (!_v1.c.$)) {
							var observed = _v1.a.a;
							var _v2 = _v1.b;
							var legacyObserved = _v1.c.a;
							var root = $author$project$Provider$incarnation(legacy);
							var legacyMinimized = A2($author$project$ActionProjection$minimized, root, legacyObserved.eN);
							var geometryMinimized = A2(
								$elm$core$Maybe$map,
								function ($) {
									return $.b_;
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
var $author$project$Effects$ExitFullscreen = {$: 5};
var $author$project$Effects$Maximize = {$: 3};
var $author$project$Effects$Pin = {$: 8};
var $author$project$Effects$RestoreGeometry = {$: 4};
var $author$project$Effects$Unpin = {$: 9};
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
		case 7:
			return $elm$core$Maybe$Just($author$project$Effects$ExitFullscreen);
		case 8:
			var desired = action.a;
			return $elm$core$Maybe$Just(
				desired ? $author$project$Effects$Pin : $author$project$Effects$Unpin);
		default:
			return $elm$core$Maybe$Nothing;
	}
};
var $author$project$Provider$presentationScope = function (_v0) {
	var value = _v0;
	return {dC: value.P.dC, dI: value.dI};
};
var $author$project$Provider$getItems = function (_v0) {
	var value = _v0;
	return value.fo;
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
var $author$project$ReceiptRouter$ExitFullscreen = 4;
var $author$project$ReceiptRouter$Maximize = 2;
var $author$project$ReceiptRouter$Minimize = 0;
var $author$project$ReceiptRouter$Pin = 5;
var $author$project$ReceiptRouter$Restore = 1;
var $author$project$ReceiptRouter$RestoreGeometry = 3;
var $author$project$ReceiptRouter$Unpin = 6;
var $author$project$Provider$actionContext = F2(
	function (action, snapshot) {
		var state = snapshot;
		return ($author$project$Provider$actionProtocol(action) === 2) ? A2(
			$elm$core$Maybe$withDefault,
			$author$project$Provider$nativeContext(snapshot),
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.P;
				},
				state.ap)) : $author$project$Provider$nativeContext(snapshot);
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
		return {aa: intent, er: _native, eE: protocol};
	});
var $author$project$ReceiptRouter$Intent = F5(
	function (request, generation, incarnation, operation, context) {
		return {P: context, fh: generation, aq: incarnation, bh: operation, c1: request};
	});
var $author$project$ReceiptRouter$Context = F4(
	function (lifetime, epoch, output, revision) {
		return {fe: epoch, fp: lifetime, y: output, c2: revision};
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
			case 'exit-fullscreen':
				return $elm$json$Json$Decode$succeed(4);
			case 'pin':
				return $elm$json$Json$Decode$succeed(5);
			case 'unpin':
				return $elm$json$Json$Decode$succeed(6);
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
			value.eE,
			A2(
				$elm$core$List$member,
				value.aa.bh,
				_List_fromArray(
					[2, 3, 4, 5, 6])) ? 2 : 1) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Operation protocol mismatch');
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
					case 7:
						return $elm$core$Maybe$Just(4);
					case 8:
						var desired = action.a;
						return $elm$core$Maybe$Just(
							desired ? 5 : 6);
					default:
						return $elm$core$Maybe$Nothing;
				}
			}();
			var eligible = A2(
				$elm$core$List$any,
				function (item) {
					return item.fd && _Utils_eq(item.e3, action);
				},
				$author$project$Provider$getItems(provider));
			return ((!_Utils_eq(
				binding,
				$author$project$Provider$getBinding(provider))) || ((!eligible) || ((!_Utils_eq(
				$elm$core$Maybe$Just(_native.aa.bh),
				expectedOperation)) || ((!_Utils_eq(
				_native.er,
				$author$project$Provider$nativeBinding(provider))) || ((!_Utils_eq(
				_native.aa.P,
				A2($author$project$Provider$actionContext, action, provider))) || ((!_Utils_eq(
				_native.eE,
				$author$project$Provider$actionProtocol(action))) || (!_Utils_eq(
				_native.aa.aq,
				$author$project$Provider$incarnation(provider))))))))) ? $elm$core$Result$Err('Native command does not match frozen menu action') : (A2(
				$elm$core$List$any,
				function (entry) {
					return _Utils_eq(entry.cq, local) || (_Utils_eq(entry.a_, _native) || (_Utils_eq(entry.a_.er, _native.er) && _Utils_eq(entry.a_.aa.c1, _native.aa.c1)));
				},
				entries) ? $elm$core$Result$Err('Native/local operation already registered') : ((_Utils_cmp(
				$elm$core$List$length(entries),
				$author$project$Menu$maxOutstanding) > -1) ? $elm$core$Result$Err('Receipt registry capacity') : $elm$core$Result$Ok(
				A2(
					$elm$core$List$cons,
					{dk: binding, a_: _native, cq: local},
					entries))));
		}
	});
var $author$project$ReceiptRouter$registerPrepared = F5(
	function (_v0, original, fresh, value, model) {
		var local = _v0.a;
		var originalBinding = _v0.b;
		var action = _v0.c;
		var ordered = $elm$core$List$sortWith(
			F2(
				function (a, b) {
					return A2($author$project$UInt64$compare, a.aq, b.aq);
				}));
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
						return _Utils_eq(
							ordered(before.a),
							ordered(after.a)) && ((!after.e6) && (_Utils_eq(before.P.y, after.P.y) && (_Utils_eq(before.dk, after.dk) && ((!(!A2($author$project$UInt64$compare, after.P.c2, before.P.c2))) && (!(!A2($author$project$UInt64$compare, after.bN, before.bN)))))));
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
			$author$project$Provider$presentationScope(fresh))) || ((!_Utils_eq(old.fp, _new.fp)) || ((!_Utils_eq(old.fe, _new.fe)) || ((!_Utils_eq(old.y, _new.y)) || ((!A2($author$project$UInt64$compare, _new.c2, old.c2)) || ((!geometrySame) || (!_Utils_eq(
			$author$project$Provider$getItems(original),
			$author$project$Provider$getItems(fresh)))))))))))) ? $elm$core$Result$Err('Prepared action authority changed') : A2(
			$elm$core$Result$map,
			function (_v1) {
				var entries = _v1;
				return A2(
					$elm$core$List$map,
					function (entry) {
						return _Utils_eq(entry.cq, local) ? _Utils_update(
							entry,
							{dk: originalBinding}) : entry;
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
					return $.dj;
				},
				A2(
					$author$project$ActionProjection$find,
					identity,
					$author$project$ActionProjection$windows(projection))));
	});
var $author$project$Effects$Context = F4(
	function (lifetime, epoch, output, revision) {
		return {fe: epoch, fp: lifetime, y: output, c2: revision};
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
var $author$project$ActionProjection$Window = F7(
	function (incarnation, label, minimized, owner, application, available, attention) {
		return {di: application, dS: attention, dj: available, aq: incarnation, el: label, b_: minimized, dD: owner};
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
var $author$project$ActionProjection$windowDecoder = $elm$json$Json$Decode$oneOf(
	_List_fromArray(
		[
			A2(
			$author$project$ActionProjection$strict,
			_List_fromArray(
				['incarnation', 'label', 'minimized', 'owner', 'application', 'available', 'attention']),
			A8(
				$elm$json$Json$Decode$map7,
				$author$project$ActionProjection$Window,
				A2($elm$json$Json$Decode$field, 'incarnation', $author$project$ActionProjection$nonzero),
				A2($elm$json$Json$Decode$field, 'label', $elm$json$Json$Decode$string),
				A2($elm$json$Json$Decode$field, 'minimized', $elm$json$Json$Decode$bool),
				A2(
					$elm$json$Json$Decode$field,
					'owner',
					$elm$json$Json$Decode$nullable($author$project$ActionProjection$nonzero)),
				A2($elm$json$Json$Decode$field, 'application', $elm$json$Json$Decode$string),
				A2($elm$json$Json$Decode$field, 'available', $elm$json$Json$Decode$bool),
				A2($elm$json$Json$Decode$field, 'attention', $elm$json$Json$Decode$bool))),
			A2(
			$author$project$ActionProjection$strict,
			_List_fromArray(
				['incarnation', 'label', 'minimized', 'owner', 'application', 'available']),
			A8(
				$elm$json$Json$Decode$map7,
				$author$project$ActionProjection$Window,
				A2($elm$json$Json$Decode$field, 'incarnation', $author$project$ActionProjection$nonzero),
				A2($elm$json$Json$Decode$field, 'label', $elm$json$Json$Decode$string),
				A2($elm$json$Json$Decode$field, 'minimized', $elm$json$Json$Decode$bool),
				A2(
					$elm$json$Json$Decode$field,
					'owner',
					$elm$json$Json$Decode$nullable($author$project$ActionProjection$nonzero)),
				A2($elm$json$Json$Decode$field, 'application', $elm$json$Json$Decode$string),
				A2($elm$json$Json$Decode$field, 'available', $elm$json$Json$Decode$bool),
				$elm$json$Json$Decode$succeed(false)))
		]));
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
				var _v0 = w.dD;
				if (_v0.$ === 1) {
					return $elm$core$Maybe$Just(w.aq);
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
									return !w.b_;
								},
								A2($author$project$ActionProjection$find, identity, rows)));
					},
					focus));
			var unique = A3(
				$elm$core$List$foldl,
				F2(
					function (w, seen) {
						return A2($elm$core$List$member, w.aq, seen) ? seen : A2($elm$core$List$cons, w.aq, seen);
					}),
				_List_Nil,
				rows);
			var table = $elm$core$Dict$fromList(
				A2(
					$elm$core$List$map,
					function (w) {
						return _Utils_Tuple2(
							$author$project$UInt64$string(w.aq),
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
										$author$project$UInt64$string(w.aq),
										root,
										cache);
								}),
							accumulated,
							A3($author$project$ActionProjection$rootIn, 256, w.aq, table));
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
							return _Utils_eq(root.b_, w.b_);
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
									$author$project$UInt64$string(w.aq)),
								roots))));
			};
			if ((!_Utils_eq(
				$elm$core$List$length(unique),
				$elm$core$List$length(rows))) || ((!validFocus) || A2(
				$elm$core$List$any,
				function (w) {
					return !($author$project$ActionProjection$validText(w.el) && ($author$project$ActionProjection$validText(w.di) && validFamily(w)));
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
		return {P: context, fh: generation, aq: incarnation, bh: operation, c1: request};
	});
var $author$project$Effects$SnapPlacement = function (a) {
	return {$: 6, a: a};
};
var $author$project$Effects$TransferWorkspace = function (a) {
	return {$: 7, a: a};
};
var $author$project$Transfer$Proposal = F3(
	function (source, sourceGeneration, destination) {
		return {bx: destination, cv: source, da: sourceGeneration};
	});
var $author$project$Transfer$decoder = A2(
	$elm$json$Json$Decode$andThen,
	function (pairs) {
		return (!_Utils_eq(
			$elm$core$List$sort(
				A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
			_List_fromArray(
				['destination', 'source', 'sourceGeneration']))) ? $elm$json$Json$Decode$fail('Transfer fields') : A2(
			$elm$json$Json$Decode$andThen,
			function (p) {
				return ($author$project$Transfer$ordinary(p.cv) && ($author$project$Transfer$ordinary(p.bx) && ((!_Utils_eq(p.cv, p.bx)) && (!_Utils_eq(p.da, $author$project$UInt64$zero))))) ? $elm$json$Json$Decode$succeed(p) : $elm$json$Json$Decode$fail('Transfer workspace identity');
			},
			A4(
				$elm$json$Json$Decode$map3,
				$author$project$Transfer$Proposal,
				A2($elm$json$Json$Decode$field, 'source', $elm$json$Json$Decode$string),
				A2($elm$json$Json$Decode$field, 'sourceGeneration', $author$project$UInt64$decoder),
				A2($elm$json$Json$Decode$field, 'destination', $elm$json$Json$Decode$string)));
	},
	$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
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
			case 'exit-fullscreen':
				return $elm$json$Json$Decode$succeed($author$project$Effects$ExitFullscreen);
			case 'pin':
				return $elm$json$Json$Decode$succeed($author$project$Effects$Pin);
			case 'unpin':
				return $elm$json$Json$Decode$succeed($author$project$Effects$Unpin);
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
						return {P: context, ap: geometry, b$: monitor, bi: output, cu: regionName, cE: area, ce: workspace};
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
				A2($elm$json$Json$Decode$field, 'context', $author$project$Effects$contextDecoder))) : ((name === 'transfer-workspace') ? A2(
			$author$project$Effects$strict,
			_List_fromArray(
				['request', 'generation', 'incarnation', 'operation', 'context', 'transfer']),
			A6(
				$elm$json$Json$Decode$map5,
				$author$project$Effects$Intent,
				A2($elm$json$Json$Decode$field, 'request', $author$project$Effects$identity),
				A2($elm$json$Json$Decode$field, 'generation', $author$project$Effects$identity),
				A2($elm$json$Json$Decode$field, 'incarnation', $author$project$Effects$identity),
				A2(
					$elm$json$Json$Decode$map,
					$author$project$Effects$TransferWorkspace,
					A2($elm$json$Json$Decode$field, 'transfer', $author$project$Transfer$decoder)),
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
				A2($elm$json$Json$Decode$field, 'context', $author$project$Effects$contextDecoder))));
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
		case 8:
			return 2;
		case 9:
			return 2;
		case 6:
			return 2;
		case 7:
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
		return _Utils_eq(a.fp, b.fp) && (_Utils_eq(a.fe, b.fe) && _Utils_eq(a.y, b.y));
	});
var $author$project$ActionProjection$sameState = F2(
	function (left, right) {
		var state = function (projection) {
			return A2(
				$elm$core$List$map,
				function (w) {
					return _Utils_Tuple3(
						w.aq,
						_Utils_Tuple2(w.b_, w.dD),
						_Utils_Tuple2(
							w.di,
							_Utils_Tuple2(w.dj, w.dS)));
				},
				A2(
					$elm$core$List$sortWith,
					F2(
						function (a, b) {
							return A2($author$project$UInt64$compare, a.aq, b.aq);
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
		return (!transaction.W) ? _Utils_update(
			transaction,
			{W: 4}) : transaction;
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
									context.c2)) {
									return refuse('Scene/context revision mismatch');
								} else {
									var _v3 = model.as;
									if (!_v3.$) {
										var old = _v3.a;
										return (A2($author$project$Effects$sameAuthority, old.P, context) && ((!A2($author$project$UInt64$compare, context.c2, old.P.c2)) || (_Utils_eq(context.c2, old.P.c2) && (!A2($author$project$ActionProjection$sameState, old.eN, scene))))) ? refuse('Nonincreasing snapshot') : _Utils_Tuple3(
											_Utils_update(
												model,
												{
													bb: true,
													as: $elm$core$Maybe$Just(
														{P: context, eN: scene}),
													fS: A2($author$project$Effects$sameAuthority, old.P, context) ? model.fS : $author$project$Effects$unknown(model.fS)
												}),
											$elm$core$Maybe$Nothing,
											$elm$core$Maybe$Nothing);
									} else {
										return _Utils_Tuple3(
											_Utils_update(
												model,
												{
													bb: true,
													as: $elm$core$Maybe$Just(
														{P: context, eN: scene})
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
								model.as,
								$author$project$UInt64$next(model.c1),
								$author$project$UInt64$next(model.fh));
							if (((!_v5.a.$) && (!_v5.b.$)) && (!_v5.c.$)) {
								var observed = _v5.a.a;
								var request = _v5.b.a;
								var generation = _v5.c.a;
								if (!model.bb) {
									return refuse('Disconnected');
								} else {
									if ($author$project$Effects$pending(model)) {
										return refuse('Operation already pending');
									} else {
										if ($elm$core$List$length(model.z) >= 64) {
											return refuse('Unresolved operation capacity');
										} else {
											if ($author$project$Effects$protocol(operation) === 2) {
												return refuse('Geometry observation required');
											} else {
												if (A3($author$project$Effects$blocked, observed.P.fp, incarnation, model)) {
													return refuse('Unresolved native operation');
												} else {
													if (!A2($author$project$ActionProjection$actionable, incarnation, observed.eN)) {
														return refuse('Locked or unmapped target');
													} else {
														var _v6 = A2($author$project$ActionProjection$minimized, incarnation, observed.eN);
														if (_v6.$ === 1) {
															return refuse('Unknown incarnation');
														} else {
															var minimized = _v6.a;
															if ((_Utils_eq(operation, $author$project$Effects$Minimize) && minimized) || ((_Utils_eq(operation, $author$project$Effects$Restore) && (!minimized)) || (_Utils_eq(operation, $author$project$Effects$Activate) && minimized))) {
																return refuse('Already in requested native state');
															} else {
																var intent = {P: observed.P, fh: generation, aq: incarnation, bh: operation, c1: request};
																return _Utils_Tuple3(
																	_Utils_update(
																		model,
																		{
																			fh: generation,
																			c1: request,
																			fS: $elm$core$Maybe$Just(
																				{ay: 1, aa: intent, W: 0}),
																			z: A2(
																				$elm$core$List$cons,
																				{ay: 1, aa: intent, W: 0},
																				model.z)
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
								return _Utils_eq(t.ay, protocolId) && _Utils_eq(t.aa, intent);
							};
							var found = A2($elm$core$List$any, exact, model.z);
							var settled = function (t) {
								return exact(t) ? _Utils_update(
									t,
									{W: status}) : t;
							};
							var unresolved = (status === 4) ? A2($elm$core$List$map, settled, model.z) : A2(
								$elm$core$List$filter,
								A2($elm$core$Basics$composeR, exact, $elm$core$Basics$not),
								model.z);
							return ((!found) || ((!A2(
								$elm$core$List$member,
								protocolId,
								_List_fromArray(
									[1, 2]))) || (!_Utils_eq(
								$author$project$Effects$protocol(intent.bh),
								protocolId)))) ? refuse('Stale, mismatched or terminal receipt') : _Utils_Tuple3(
								_Utils_update(
									model,
									{
										fS: A2(
											$elm$core$Maybe$map,
											function (t) {
												return A2(
													$elm$core$Maybe$withDefault,
													false,
													A2(
														$elm$core$Maybe$map,
														function (observed) {
															return A2($author$project$Effects$sameAuthority, observed.P, intent.P);
														},
														model.as)) ? settled(t) : t;
											},
											model.fS),
										z: unresolved
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
										fh: A2(maximum, model.fh, generation),
										c1: A2(maximum, model.c1, request)
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
								$author$project$Effects$protocol(intent.bh),
								protocolId))) {
								return refuse('Recovery operation protocol');
							} else {
								if (A2(
									$elm$core$List$any,
									function (t) {
										return _Utils_eq(t.aa, intent) && _Utils_eq(t.ay, protocolId);
									},
									model.z)) {
									return _Utils_Tuple3(model, $elm$core$Maybe$Nothing, $elm$core$Maybe$Nothing);
								} else {
									if ($elm$core$List$length(model.z) >= 64) {
										return refuse('Unresolved operation capacity');
									} else {
										var transaction = {ay: protocolId, aa: intent, W: 4};
										var maximum = F2(
											function (old, _new) {
												return (!A2($author$project$UInt64$compare, old, _new)) ? _new : old;
											});
										return _Utils_Tuple3(
											_Utils_update(
												model,
												{
													fh: A2(maximum, model.fh, intent.fh),
													c1: A2(maximum, model.c1, intent.c1),
													fS: $elm$core$Maybe$Just(transaction),
													z: A2($elm$core$List$cons, transaction, model.z)
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
										bb: false,
										fS: $author$project$Effects$unknown(model.fS),
										z: A2(
											$elm$core$List$map,
											function (t) {
												return (!t.W) ? _Utils_update(
													t,
													{W: 4}) : t;
											},
											model.z)
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
					$elm$core$Basics$eq(proposed.cu)),
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
									{fN: region})),
							$elm$core$Maybe$Just(proposed));
					},
					A2($author$project$Snap$open, snapshot, target)));
		}
	});
var $author$project$Transfer$matches = F3(
	function (snapshot, root, p) {
		return _Utils_eq(
			A3($author$project$Transfer$propose, snapshot, root, p.bx),
			$elm$core$Maybe$Just(p));
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
					return A2($author$project$ActionProjection$actionable, incarnation, legacy.eN) && _Utils_eq(
						A2($author$project$ActionProjection$rootOf, incarnation, legacy.eN),
						$elm$core$Maybe$Just(incarnation));
				},
				model.as));
		var _v0 = _Utils_Tuple3(
			A2($author$project$GeometryProjection$window, incarnation, observed),
			$author$project$UInt64$next(model.c1),
			$author$project$UInt64$next(model.fh));
		if (((!_v0.a.$) && (!_v0.b.$)) && (!_v0.c.$)) {
			var window = _v0.a.a;
			var request = _v0.b.a;
			var generation = _v0.c.a;
			if ((!model.bb) || ((!legacyReady) || ($author$project$Effects$pending(model) || A3($author$project$Effects$blocked, observed.P.fp, incarnation, model)))) {
				return refuse('Unresolved or disconnected native operation');
			} else {
				if ($elm$core$List$length(model.z) >= 64) {
					return refuse('Unresolved operation capacity');
				} else {
					if (($author$project$Effects$protocol(operation) !== 2) || ((!caps._) || (!A2(
						$elm$core$List$member,
						$author$project$Effects$operationName(operation),
						caps.ev)))) {
						return refuse('Geometry operation not negotiated');
					} else {
						if (observed.e6 || function () {
							switch (operation.$) {
								case 8:
									return !A2(
										$elm$core$Maybe$withDefault,
										false,
										A2(
											$elm$core$Maybe$map,
											function ($) {
												return $.dr;
											},
											window.dF));
								case 9:
									return !A2(
										$elm$core$Maybe$withDefault,
										false,
										A2(
											$elm$core$Maybe$map,
											function ($) {
												return $.dr;
											},
											window.dF));
								case 5:
									return !$author$project$GeometryProjection$canExitFullscreen(window);
								case 7:
									var p = operation.a;
									return !A3($author$project$Transfer$matches, observed, incarnation, p);
								default:
									return (!window.dr) || (window.b_ || window.fg);
							}
						}()) {
							return refuse('Geometry target ineligible');
						} else {
							if ((_Utils_eq(operation, $author$project$Effects$Pin) || _Utils_eq(operation, $author$project$Effects$Unpin)) && A2(
								$elm$core$Maybe$withDefault,
								true,
								A2(
									$elm$core$Maybe$map,
									function (pin) {
										return _Utils_eq(
											pin.fB,
											_Utils_eq(operation, $author$project$Effects$Pin));
									},
									window.dF))) {
								return refuse('Pin state already requested or unavailable');
							} else {
								if ((_Utils_eq(operation, $author$project$Effects$Maximize) && ((!window.fr) || (!(!window.es)))) || (_Utils_eq(operation, $author$project$Effects$RestoreGeometry) && ((!window.fI) || ((window.es !== 1) || (!window.fC))))) {
									return refuse('Geometry state/capability unavailable');
								} else {
									if (function () {
										if (operation.$ === 6) {
											var proposed = operation.a;
											return !A3($author$project$Snap$matches, observed, incarnation, proposed);
										} else {
											return false;
										}
									}()) {
										return refuse('Snap output/work-area placement changed');
									} else {
										var intent = {P: observed.P, fh: generation, aq: incarnation, bh: operation, c1: request};
										var transaction = {ay: 2, aa: intent, W: 0};
										return _Utils_Tuple3(
											_Utils_update(
												model,
												{
													fh: generation,
													c1: request,
													fS: $elm$core$Maybe$Just(transaction),
													z: A2($elm$core$List$cons, transaction, model.z)
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
			}
		} else {
			return refuse('Missing geometry target or exhausted identity');
		}
	});
var $author$project$Effects$canProveUnsent = F3(
	function (protocolId, intent, model) {
		var exact = function (entry) {
			return _Utils_eq(entry.ay, protocolId) && _Utils_eq(entry.aa, intent);
		};
		var currentSafe = function () {
			var _v0 = model.fS;
			if (!_v0.$) {
				var entry = _v0.a;
				return (!exact(entry)) || (!entry.W);
			} else {
				return true;
			}
		}();
		return _Utils_eq(
			$author$project$Effects$protocol(intent.bh),
			protocolId) && (currentSafe && A2(
			$elm$core$List$any,
			function (entry) {
				return exact(entry) && (!entry.W);
			},
			model.z));
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
				model.dk,
				$elm$core$Maybe$Just(key.dk)) && (A2(
				$elm$core$List$any,
				function (entry) {
					return _Utils_eq(entry.dk, key.dk) && (_Utils_eq(entry.eE, key.eE) && _Utils_eq(entry.aa, key.aa));
				},
				model.U) && A3($author$project$Effects$canProveUnsent, key.eE, key.aa, model._));
		};
		return (!$elm$core$List$isEmpty(operations)) && (($elm$core$List$length(operations) <= 16) && (_Utils_eq(
			$elm$core$List$length(unique),
			$elm$core$List$length(operations)) && ((!(!model.j)) && ((model.j !== 3) && A2($elm$core$List$all, known, operations)))));
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
		return (($elm$core$List$length(caps.ev) <= 7) && (A2(
			$elm$core$List$all,
			function (op) {
				return A2(
					$elm$core$List$member,
					op,
					_List_fromArray(
						['maximize', 'restore-geometry', 'snap', 'transfer-workspace', 'pin', 'unpin', 'exit-fullscreen']));
			},
			caps.ev) && (_Utils_eq(
			$elm$core$List$length(caps.ev),
			$elm$core$List$length(
				A3(
					$elm$core$List$foldl,
					F2(
						function (x, xs) {
							return A2($elm$core$List$member, x, xs) ? xs : A2($elm$core$List$cons, x, xs);
						}),
					_List_Nil,
					caps.ev))) && _Utils_eq(
			caps._,
			!$elm$core$List$isEmpty(caps.ev))))) ? $elm$json$Json$Decode$succeed(caps) : $elm$json$Json$Decode$fail('Geometry capabilities');
	},
	A2(
		$author$project$GeometryProjection$strict,
		_List_fromArray(
			['observe', 'effects', 'effectProtocol', 'operations', 'placementCapacity', 'canonicalScene']),
		A7(
			$elm$json$Json$Decode$map6,
			F6(
				function (_v0, effects, _v1, operations, _v2, _v3) {
					return {_: effects, ev: operations};
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
	var _v0 = inputs.b3;
	var ux = _v0.a;
	var uy = _v0.b;
	var _v1 = inputs.b4;
	var rx = _v1.a;
	var ry = _v1.b;
	var _v2 = inputs.bZ;
	var lx = _v2.a;
	var ly = _v2.b;
	var _v3 = inputs.bY;
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
			{aX: h, a5: w, a6: x, a7: y});
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$GeometrySizePolicy$roundNative = function (x) {
	return (x >= 0) ? ($elm$core$Basics$floor(x) + (((x - $elm$core$Basics$floor(x)) >= 0.5) ? 1 : 0)) : ($elm$core$Basics$ceiling(x) - ((($elm$core$Basics$ceiling(x) - x) >= 0.5) ? 1 : 0));
};
var $author$project$GeometrySizePolicy$rounded = function (value) {
	return {
		aX: $author$project$GeometrySizePolicy$roundNative(value.a7 + value.aX) - $author$project$GeometrySizePolicy$roundNative(value.a7),
		a5: $author$project$GeometrySizePolicy$roundNative(value.a6 + value.a5) - $author$project$GeometrySizePolicy$roundNative(value.a6),
		a6: $author$project$GeometrySizePolicy$roundNative(value.a6),
		a7: $author$project$GeometrySizePolicy$roundNative(value.a7)
	};
};
var $author$project$GeometrySizePolicy$within = F2(
	function (inputs, projection) {
		var axis = F6(
			function (configured, real, rawLo, rawHi, lo, hi) {
				return (configured >= 1) && ((configured <= 2147483647) && ((_Utils_cmp(configured, rawLo) > -1) && (((!rawHi) || (_Utils_cmp(configured, rawHi) < 1)) && ((_Utils_cmp(real, lo) > -1) && (_Utils_cmp(real, hi) < 1)))));
			});
		var _v0 = inputs.b3;
		var ux = _v0.a;
		var uy = _v0.b;
		var _v1 = inputs.b4;
		var rx = _v1.a;
		var ry = _v1.b;
		var _v2 = inputs.bZ;
		var lx = _v2.a;
		var ly = _v2.b;
		var _v3 = inputs.bY;
		var hx = _v3.a;
		var hy = _v3.b;
		var _v4 = projection.$7;
		var cx = _v4.a;
		var cy = _v4.b;
		return _Utils_eq(
			projection.$7,
			_Utils_Tuple2(
				$elm$core$Basics$floor(projection.b6.a5),
				$elm$core$Basics$floor(projection.b6.aX))) && (A6(axis, cx, projection.b6.a5, rx, ux, lx, hx) && A6(axis, cy, projection.b6.aX, ry, uy, ly, hy));
	});
var $author$project$GeometrySizePolicy$projectionValid = F4(
	function (maximize, workArea, inputs, projection) {
		var real = projection.b6;
		var logical = projection.en;
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
			projection.eX,
			$elm$core$Maybe$Just(real));
		var _v0 = inputs.dP;
		var tx = _v0.a;
		var ty = _v0.b;
		var _v1 = inputs.dl;
		var bx = _v1.a;
		var by = _v1.b;
		var converted = maximize ? {aX: logical.aX - (ty + by), a5: logical.a5 - (tx + bx), a6: logical.a6 + tx, a7: logical.a7 + ty} : logical;
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
				projection.eX)) && (_Utils_eq(real, converted) && (A2($author$project$GeometrySizePolicy$within, inputs, projection) && (source && ((!maximize) || _Utils_eq(projection.eX, $elm$core$Maybe$Nothing))))));
	});
var $author$project$GeometrySizePolicy$supported = function (policy) {
	var _v0 = policy.dt;
	if (_v0.$ === 1) {
		return false;
	} else {
		var inputs = _v0.a;
		return _Utils_eq(
			inputs.cY,
			_Utils_Tuple2(0, 0)) && (!$author$project$GeometrySizePolicy$fixed(inputs));
	}
};
var $author$project$GeometrySizePolicy$coherent = F4(
	function (policy, workArea, constrained, fixedSize) {
		var _v0 = policy.dt;
		if (_v0.$ === 1) {
			return _Utils_eq(policy.fr, $elm$core$Maybe$Nothing) && _Utils_eq(policy.fI, $elm$core$Maybe$Nothing);
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
					values(inputs.b4),
					values(inputs.bZ))) || (A2(
				$elm$core$List$any,
				$elm$core$Basics$lt(0),
				values(inputs.b3)) || A2(
				$elm$core$List$any,
				$elm$core$Basics$gt(1.7976931348623157e308),
				values(inputs.bY)));
			return _Utils_eq(constrained, expected) && (_Utils_eq(
				fixedSize,
				$author$project$GeometrySizePolicy$fixed(inputs)) && (A2(valid, true, policy.fr) && A2(valid, false, policy.fI)));
		}
	});
var $author$project$GeometrySizePolicy$permits = F2(
	function (maximize, policy) {
		return $author$project$GeometrySizePolicy$supported(policy) && (maximize ? (!_Utils_eq(policy.fr, $elm$core$Maybe$Nothing)) : (!_Utils_eq(policy.fI, $elm$core$Maybe$Nothing)));
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
									return _Utils_eq(row.aq, id);
								},
								rows));
						if (_v0.$ === 1) {
							return false;
						} else {
							var row = _v0.a;
							var _v1 = row.dD;
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
						return A4($author$project$GeometrySizePolicy$coherent, p, row.cd, row.cK, row.fg) && (((!row.dr) || $author$project$GeometrySizePolicy$supported(p)) && (((!row.fr) || A2($author$project$GeometrySizePolicy$permits, true, p)) && ((!row.fI) || A2($author$project$GeometrySizePolicy$permits, false, p))));
					},
					row.c9));
			var pinValid = A2(
				$elm$core$Maybe$withDefault,
				true,
				A2(
					$elm$core$Maybe$map,
					function (pin) {
						return (!pin.dr) || ((!blocked) && ((!_Utils_eq(row.e$, $elm$core$Maybe$Nothing)) && (row.bX && (_Utils_eq(row.dD, $elm$core$Maybe$Nothing) && ((!row.bB) && ((!row.b_) && (_Utils_eq(row.es, row.cg) && ((row.es !== 2) && (A2($elm$core$List$member, 'pin', caps.ev) && A2($elm$core$List$member, 'unpin', caps.ev))))))))));
					},
					row.dF));
			var ownership = function () {
				var _v2 = row.dD;
				if (_v2.$ === 1) {
					return true;
				} else {
					return A2(walk, _List_Nil, row.aq);
				}
			}();
			var known = A2(
				$elm$core$List$map,
				$elm$core$Basics$identity,
				_List_fromArray(
					[
						!_Utils_eq(row.e$, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.ce, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.b$, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.bi, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.cE, $elm$core$Maybe$Nothing),
						!_Utils_eq(row.cd, $elm$core$Maybe$Nothing)
					]));
			var paired = A2(
				$elm$core$List$all,
				$elm$core$Basics$eq(true),
				known) || A2(
				$elm$core$List$all,
				$elm$core$Basics$eq(false),
				known);
			var eligible = (!row.dr) || ((!_Utils_eq(row.e$, $elm$core$Maybe$Nothing)) && ((!blocked) && ((!row.b_) && ((!row.bB) && ((!row.fg) && (((!_Utils_eq(row.c9, $elm$core$Maybe$Nothing)) || (!row.cK)) && (row.bX && (_Utils_eq(row.dD, $elm$core$Maybe$Nothing) && (_Utils_eq(row.es, row.cg) && (row.es !== 2))))))))));
			var capabilityModes = ((!row.fr) || (row.dr && (!row.es))) && ((!row.fI) || (row.dr && ((row.es === 1) && row.fC)));
			return pinValid && (paired && (eligible && (ownership && (sizeValid && (capabilityModes && (((!row.fr) || A2($elm$core$List$member, 'maximize', caps.ev)) && ((!row.fI) || A2($elm$core$List$member, 'restore-geometry', caps.ev))))))));
		};
		var ids = A2(
			$elm$core$List$map,
			function ($) {
				return $.aq;
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
				return (_Utils_eq(a.bi, $elm$core$Maybe$Nothing) || ((!_Utils_eq(a.bi, b.bi)) || _Utils_eq(a.b$, b.b$))) && (_Utils_eq(a.ce, $elm$core$Maybe$Nothing) || ((!_Utils_eq(a.ce, b.ce)) || (_Utils_eq(a.e$, b.e$) && (_Utils_eq(a.bi, b.bi) && (_Utils_eq(a.cE, b.cE) && _Utils_eq(a.cd, b.cd))))));
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
		return {dt: inputs, fr: maximize, fI: restoreGeometry};
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
		return ($author$project$GeometrySizePolicy$finite(inputs.c4) && ((inputs.c4 > 0) && (A3($author$project$GeometrySizePolicy$interval, true, inputs.b4, inputs.b3) && A3($author$project$GeometrySizePolicy$interval, false, inputs.bZ, inputs.bY)))) ? $elm$json$Json$Decode$succeed(inputs) : $elm$json$Json$Decode$fail('Size intervals');
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
						return {dl: br, bY: layoutMax, bZ: layoutMin, cY: origin, b3: rawMax, b4: rawMin, c4: scale, dP: tl};
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
		return {$7: configure, en: logical, b6: real, eX: visual};
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
				{aX: h, a5: w, a6: x, a7: y}) : $elm$json$Json$Decode$fail('Prospective box');
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
				return {dY: client, d6: fixed, bX: floating, bB: grouped, en: logical, b_: minimized, er: _native, eX: visual};
			}),
		A2($elm$json$Json$Decode$field, 'logicalGeometry', $author$project$GeometryProjection$rect),
		A2($elm$json$Json$Decode$field, 'visualGeometry', $author$project$GeometryProjection$rect),
		A2($elm$json$Json$Decode$field, 'nativeMode', $author$project$GeometryProjection$modeDecoder),
		A2($elm$json$Json$Decode$field, 'clientMode', $author$project$GeometryProjection$modeDecoder),
		A2($elm$json$Json$Decode$field, 'minimized', $elm$json$Json$Decode$bool),
		A2($elm$json$Json$Decode$field, 'floating', $elm$json$Json$Decode$bool),
		A2($elm$json$Json$Decode$field, 'grouped', $elm$json$Json$Decode$bool),
		A2($elm$json$Json$Decode$field, 'fixedSize', $elm$json$Json$Decode$bool));
	var policy = A7(
		$elm$json$Json$Decode$map6,
		F6(
			function (constrained, eligible, known, caps, size, pin) {
				return {dn: caps, dZ: constrained, dr: eligible, ek: known, dF: pin, eQ: size};
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
		(protocol >= 2) ? A2(
			$elm$json$Json$Decode$map,
			$elm$core$Maybe$Just,
			A2($elm$json$Json$Decode$field, 'sizePolicy', $author$project$GeometrySizePolicy$decoder)) : $elm$json$Json$Decode$succeed($elm$core$Maybe$Nothing),
		(protocol === 3) ? A2(
			$elm$json$Json$Decode$map,
			$elm$core$Maybe$Just,
			A2(
				$elm$json$Json$Decode$field,
				'pin',
				A2(
					$author$project$GeometryProjection$strict,
					_List_fromArray(
						['pinned', 'eligible']),
					A3(
						$elm$json$Json$Decode$map2,
						F2(
							function (pinned, eligible) {
								return {dr: eligible, fB: pinned};
							}),
						A2($elm$json$Json$Decode$field, 'pinned', $elm$json$Json$Decode$bool),
						A2($elm$json$Json$Decode$field, 'eligible', $elm$json$Json$Decode$bool))))) : $elm$json$Json$Decode$succeed($elm$core$Maybe$Nothing));
	var identities = A9(
		$elm$json$Json$Decode$map8,
		F8(
			function (inc, owner, ws, wg, mon, og, wr, wa) {
				return {ee: inc, ep: mon, eu: og, dD: owner, eZ: wa, e_: wg, e0: wr, e1: ws};
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
			_Utils_ap(
				(protocol >= 2) ? _List_fromArray(
					['sizePolicy']) : _List_Nil,
				(protocol === 3) ? _List_fromArray(
					['pin']) : _List_Nil)),
		A4(
			$elm$json$Json$Decode$map3,
			F3(
				function (i, s, p) {
					return {cg: s.dY, cK: p.dZ, dr: p.dr, fg: s.d6, bX: s.bX, bB: s.bB, aq: i.ee, eo: s.en, fr: p.dn.a, b_: s.b_, b$: i.ep, es: s.er, bi: i.eu, dD: i.dD, dF: p.dF, fC: p.ek, fI: p.dn.b, c9: p.eQ, eY: s.eX, cd: i.eZ, cE: i.e0, e$: i.e1, ce: i.e_};
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
				return (A3($author$project$GeometryProjection$validRows, caps, snapshot.e6, snapshot.a) && A2(
					$elm$core$Maybe$withDefault,
					true,
					A2(
						$elm$core$Maybe$map,
						function (id) {
							return A2(
								$elm$core$List$any,
								function (row) {
									return _Utils_eq(row.aq, id);
								},
								snapshot.a);
						},
						snapshot.ci))) ? $elm$json$Json$Decode$succeed(snapshot) : $elm$json$Json$Decode$fail('Geometry facts coherence');
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
									return {fe: epoch, fp: life, y: output, c2: revision};
								} else {
									return {fe: $author$project$UInt64$zero, fp: $author$project$UInt64$zero, y: output, c2: revision};
								}
							}();
							return {dk: binding, e6: facts.e6, P: context, ci: facts.ci, c1: request, bN: sequence, a: facts.a};
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
											return {e6: blocked, ci: focus, a: rows};
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
				A2(
					$elm$json$Json$Decode$andThen,
					function (version) {
						return A2(
							$elm$core$List$member,
							version,
							_List_fromArray(
								[2, 3])) ? A2($author$project$GeometryProjection$decoder, version, caps) : $elm$json$Json$Decode$fail('Geometry protocol');
					},
					A2($elm$json$Json$Decode$field, 'geometryProtocol', $elm$json$Json$Decode$int)),
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
		model._);
	var effects = _v0.a;
	return _Utils_update(
		model,
		{
			am: false,
			d$: false,
			_: effects,
			A: $elm$core$Maybe$Nothing,
			ap: $elm$core$Maybe$Nothing,
			ea: $elm$core$Maybe$Nothing,
			ds: $elm$core$Maybe$Nothing,
			eb: $elm$core$Maybe$Nothing,
			ft: A2(
				$elm$core$Maybe$withDefault,
				'Connection lost. Reconnect to continue.',
				A2($elm$core$Maybe$map, $author$project$Shell$recoveryNotice, model.b7)),
			aA: false,
			j: 0,
			a2: false,
			bm: false,
			X: false
		});
};
var $author$project$Effects$locallyRefuseUnsent = F3(
	function (protocolId, intent, model) {
		var exact = function (entry) {
			return _Utils_eq(entry.ay, protocolId) && _Utils_eq(entry.aa, intent);
		};
		return (!A3($author$project$Effects$canProveUnsent, protocolId, intent, model)) ? model : _Utils_update(
			model,
			{
				fS: A2(
					$elm$core$Maybe$map,
					function (entry) {
						return exact(entry) ? _Utils_update(
							entry,
							{W: 2}) : entry;
					},
					model.fS),
				z: A2(
					$elm$core$List$filter,
					A2($elm$core$Basics$composeR, exact, $elm$core$Basics$not),
					model.z)
			});
	});
var $author$project$Shell$matchesUnsent = F2(
	function (observations, model) {
		var slot = function (kind) {
			switch (kind) {
				case 'projection-request':
					return model.A;
				case 'geometry-facts-request':
					return model.eb;
				case 'geometry-attach':
					return model.ea;
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
	return ((!model.j) || ((model.j === 3) || model.X)) ? _Utils_Tuple2(model, _List_Nil) : ((model.d$ || ($author$project$Effects$pending(model._) || ((!_Utils_eq(model.A, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(model.eb, $elm$core$Maybe$Nothing)) || (!_Utils_eq(model.ea, $elm$core$Maybe$Nothing)))))) ? _Utils_Tuple2(
		_Utils_update(
			model,
			{aA: true}),
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
			return (_Utils_eq(transaction.aa, intent) && (_Utils_eq(transaction.ay, protocolId) && (!transaction.W))) ? _Utils_update(
				transaction,
				{W: 4}) : transaction;
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
						fS: A2($elm$core$Maybe$map, observe, recovered.fS),
						z: A2($elm$core$List$map, observe, recovered.z)
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
				z: A2(
					$elm$core$List$filter,
					function (t) {
						return !((t.W === 4) && (_Utils_eq(t.ay, protocolId) && _Utils_eq(t.aa, intent)));
					},
					model.z)
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
				$author$project$Effects$protocol(original.bh),
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
						{ct: true, X: true}),
					_List_Nil);
			case 1:
				var protocolId = msg.a;
				var intent = msg.b;
				var _v1 = A3($author$project$Effects$recoverUnknown, protocolId, intent, model._);
				if (_v1.$ === 1) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var effects = _v1.a;
					return _Utils_Tuple2(
						_Utils_update(
							model,
							{_: effects, ft: 'The previous window change could not be confirmed.'}),
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
							_: preserveShared ? model._ : A3($author$project$Effects$releaseUnknown, protocolId, intent, model._),
							U: A2(
								$elm$core$List$filter,
								function (entry) {
									return !(_Utils_eq(entry.dk, oldBinding) && (_Utils_eq(entry.eE, protocolId) && _Utils_eq(entry.aa, intent)));
								},
								model.U),
							ft: 'Previous request remains unconfirmed. Choose a new window action.'
						}),
					_List_Nil);
			case 4:
				return ((!model.j) || $author$project$Effects$pending(model._)) ? _Utils_Tuple2(model, _List_Nil) : ($author$project$Shell$geometrySupported(model) ? $author$project$Shell$notificationRefresh(model) : $author$project$Shell$refresh(model));
			case 5:
				return ((!model.j) && (!model.bm)) ? _Utils_Tuple2(
					_Utils_update(
						model,
						{ft: 'Reconnecting…', bm: true}),
					_List_fromArray(
						[$author$project$Shell$RestartBackend])) : _Utils_Tuple2(model, _List_Nil);
			case 11:
				var reissue = msg.a;
				if ((!model.j) || ((model.j === 3) || _Utils_eq(model.dk, $elm$core$Maybe$Nothing))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var retired = _Utils_update(
						model,
						{d$: false, A: $elm$core$Maybe$Nothing, ea: $elm$core$Maybe$Nothing, eb: $elm$core$Maybe$Nothing, aA: true, j: 1, a2: false});
					var attach = model.am || (!_Utils_eq(model.ea, $elm$core$Maybe$Nothing));
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
						return _Utils_eq(entry.dk, key.dk) && (_Utils_eq(entry.eE, key.eE) && _Utils_eq(entry.aa, key.aa));
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
							return A3($author$project$Effects$locallyRefuseUnsent, key.eE, key.aa, state);
						}),
					model._,
					proven);
				var retired = _Utils_update(
					model,
					{
						am: model.am || A2(has, 'geometry-attach', model.ea),
						d$: false,
						_: effects,
						A: A2(has, 'projection-request', model.A) ? $elm$core$Maybe$Nothing : model.A,
						ea: A2(has, 'geometry-attach', model.ea) ? $elm$core$Maybe$Nothing : model.ea,
						eb: A2(has, 'geometry-facts-request', model.eb) ? $elm$core$Maybe$Nothing : model.eb,
						U: A2(
							$elm$core$List$filter,
							function (entry) {
								return !A2(
									$elm$core$List$any,
									function (key) {
										return A2(matches, key, entry);
									},
									proven);
							},
							model.U),
						ft: 'The request was not sent. Waiting for window transport recovery.',
						aA: true,
						j: ((!model.j) || (model.j === 3)) ? model.j : 1,
						X: true
					});
				return _Utils_Tuple2(retired, _List_Nil);
			case 14:
				var reissue = msg.a;
				if (!model.X) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var recovered = _Utils_update(
						model,
						{X: false});
					return ((!reissue) || ((!recovered.j) || ((recovered.j === 3) || ($author$project$Effects$pending(recovered._) || ((!_Utils_eq(recovered.A, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(recovered.eb, $elm$core$Maybe$Nothing)) || (!_Utils_eq(recovered.ea, $elm$core$Maybe$Nothing)))))))) ? _Utils_Tuple2(recovered, _List_Nil) : $author$project$Shell$refreshObservations(recovered);
				}
			case 12:
				var operations = msg.a;
				if (!A2($author$project$Shell$canProveUnsent, operations, model)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var matches = F2(
						function (key, entry) {
							return _Utils_eq(entry.dk, key.dk) && (_Utils_eq(entry.eE, key.eE) && _Utils_eq(entry.aa, key.aa));
						});
					var effects = A3(
						$elm$core$List$foldl,
						F2(
							function (key, state) {
								return A3($author$project$Effects$locallyRefuseUnsent, key.eE, key.aa, state);
							}),
						model._,
						operations);
					var updated = _Utils_update(
						model,
						{
							_: effects,
							U: A2(
								$elm$core$List$filter,
								function (entry) {
									return !A2(
										$elm$core$List$any,
										function (key) {
											return A2(matches, key, entry);
										},
										operations);
								},
								model.U),
							ft: 'The request was not sent. Choose again.'
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
						A: contains('projection-request') ? $elm$core$Maybe$Nothing : model.A,
						ea: contains('geometry-attach') ? $elm$core$Maybe$Nothing : model.ea,
						eb: contains('geometry-facts-request') ? $elm$core$Maybe$Nothing : model.eb,
						aA: true
					});
				if ((!valid) || ((!model.j) || (model.j === 3))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					if ($author$project$Effects$pending(model._) || (model.d$ || ((!_Utils_eq(cleared.A, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(cleared.eb, $elm$core$Maybe$Nothing)) || (!_Utils_eq(cleared.ea, $elm$core$Maybe$Nothing)))))) {
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
								{ft: 'Window list changed. Choose again.'}),
							_List_Nil);
					} else {
						var _v8 = function () {
							if ($author$project$Effects$protocol(operation) === 2) {
								var _v9 = _Utils_Tuple2(model.ds, model.ap);
								if ((!_v9.a.$) && (!_v9.b.$)) {
									var caps = _v9.a.a;
									var observed = _v9.b.a;
									return ((!_Utils_eq(model.eb, $elm$core$Maybe$Nothing)) || (!_Utils_eq(model.ea, $elm$core$Maybe$Nothing))) ? _Utils_Tuple3(
										model._,
										$elm$core$Maybe$Nothing,
										$elm$core$Maybe$Just('Geometry refresh pending')) : A5($author$project$Effects$beginGeometry, caps, observed, operation, incarnation, model._);
								} else {
									return _Utils_Tuple3(
										model._,
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
									model._);
							}
						}();
						var effects = _v8.a;
						var command = _v8.b;
						var error = _v8.c;
						var commands = function () {
							var _v11 = _Utils_Tuple2(command, model.dk);
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
									_: effects,
									U: function () {
										var _v10 = _Utils_Tuple3(command, model.dk, effects.fS);
										if (((!_v10.a.$) && (!_v10.b.$)) && (!_v10.c.$)) {
											var binding = _v10.b.a;
											var transaction = _v10.c.a;
											return A2(
												$elm$core$List$cons,
												{dk: binding, aa: transaction.aa, eE: transaction.ay},
												model.U);
										} else {
											return model.U;
										}
									}(),
									ft: A2($elm$core$Maybe$withDefault, model.ft, error)
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
												ft: $author$project$Shell$recoveryNotice(reason),
												b7: $elm$core$Maybe$Just(reason)
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
									if ((!(!model.j)) || ((!model.bm) || A2(
										$elm$core$Maybe$withDefault,
										false,
										A2(
											$elm$core$Maybe$map,
											A2(
												$elm$core$Basics$composeR,
												$author$project$Binding$replaces(binding),
												$elm$core$Basics$not),
											model.dk)))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var detached = $author$project$Shell$disconnect(model);
										return $author$project$Shell$refresh(
											_Utils_update(
												detached,
												{
													dk: $elm$core$Maybe$Just(binding),
													ft: 'Updating window information…',
													j: 1,
													bm: false,
													b7: $elm$core$Maybe$Nothing
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
									return ((!model.j) || ((model.j === 3) || ((!_Utils_eq(
										model.dk,
										$elm$core$Maybe$Just(binding))) || (!_Utils_eq(
										model.A,
										$elm$core$Maybe$Just(request)))))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$drainNotifications(
										_Utils_update(
											model,
											{A: $elm$core$Maybe$Nothing, aA: true, j: 1, a2: true}));
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
									if ((!model.j) || ((!_Utils_eq(
										model.dk,
										$elm$core$Maybe$Just(binding))) || ((!_Utils_eq(
										model.A,
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
											var _v27 = A2($author$project$Effects$apply, snapshot, model._);
											var effects = _v27.a;
											var error = _v27.c;
											return $author$project$Shell$drainNotifications(
												_Utils_update(
													model,
													{
														_: effects,
														A: _Utils_eq(error, $elm$core$Maybe$Nothing) ? $elm$core$Maybe$Nothing : model.A,
														ft: _Utils_eq(error, $elm$core$Maybe$Nothing) ? 'Connected' : 'Window information could not be verified.',
														j: _Utils_eq(error, $elm$core$Maybe$Nothing) ? 2 : 1
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
									return ((!_Utils_eq(model.ds, $elm$core$Maybe$Nothing)) || (!_Utils_eq(model.ea, $elm$core$Maybe$Nothing))) ? _Utils_Tuple2(model, _List_Nil) : A2($author$project$Shell$geometryRequest, true, model);
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
												return {dk: binding, eH: reason, c1: request};
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
										model.dk,
										$elm$core$Maybe$Just(refusal.dk))) || (!_Utils_eq(
										model.ea,
										$elm$core$Maybe$Just(refusal.c1)))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$drainNotifications(
										_Utils_update(
											model,
											{
												am: false,
												ap: $elm$core$Maybe$Nothing,
												ea: $elm$core$Maybe$Nothing,
												ds: $elm$core$Maybe$Just(
													{_: false, ev: _List_Nil}),
												eb: $elm$core$Maybe$Nothing
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
												return {dk: binding, dn: caps, c1: request};
											}),
										$author$project$Shell$version,
										A2(
											$elm$json$Json$Decode$andThen,
											function (v) {
												return (v === 3) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Geometry protocol');
											},
											A2($elm$json$Json$Decode$field, 'geometryProtocol', $elm$json$Json$Decode$int)),
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$Shell$positive),
										A2($elm$json$Json$Decode$field, 'capabilities', $author$project$GeometryProjection$capabilitiesDecoder)));
								var _v32 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v32.$) {
									var value = _v32.a;
									return ((!_Utils_eq(
										model.dk,
										$elm$core$Maybe$Just(value.dk))) || ((!_Utils_eq(
										model.ea,
										$elm$core$Maybe$Just(value.c1))) || (!model.j))) ? _Utils_Tuple2(model, _List_Nil) : A2(
										$author$project$Shell$geometryRequest,
										false,
										_Utils_update(
											model,
											{
												am: false,
												ap: $elm$core$Maybe$Nothing,
												ea: $elm$core$Maybe$Nothing,
												ds: $elm$core$Maybe$Just(value.dn)
											}));
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'geometry-facts':
								var _v35 = model.ds;
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
											var _v37 = model.ap;
											if (_v37.$ === 1) {
												return true;
											} else {
												var old = _v37.a;
												return (_Utils_eq(old.P.fp, observed.P.fp) && _Utils_eq(old.P.fe, observed.P.fe)) ? ((!(!A2($author$project$UInt64$compare, observed.P.y, old.P.y))) && ((!(!A2($author$project$UInt64$compare, observed.bN, old.bN))) && ((!(!A2($author$project$UInt64$compare, observed.P.c2, old.P.c2))) && ((!_Utils_eq(observed.P.c2, old.P.c2)) || _Utils_eq(
													observed,
													_Utils_update(
														old,
														{c1: observed.c1, bN: observed.bN})))))) : true;
											}
										}();
										return ((!_Utils_eq(
											model.dk,
											$elm$core$Maybe$Just(observed.dk))) || ((!_Utils_eq(
											model.eb,
											$elm$core$Maybe$Just(observed.c1))) || ((!model.j) || (!newer)))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Shell$drainNotifications(
											_Utils_update(
												model,
												{
													ap: $elm$core$Maybe$Just(observed),
													eb: $elm$core$Maybe$Nothing
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
									if ((model.j !== 1) || (!_Utils_eq(
										model.dk,
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
											model._);
										var effects = _v40.a;
										return _Utils_Tuple2(
											_Utils_update(
												model,
												{_: effects}),
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
										model.dk,
										$elm$core$Maybe$Just(binding))) || ((model.j !== 1) || (!_Utils_eq(
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
											model._);
										var effects = _v44.a;
										var error = _v44.c;
										return (!_Utils_eq(error, $elm$core$Maybe$Nothing)) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
											_Utils_update(
												model,
												{_: effects, ft: 'The previous window change could not be confirmed.'}),
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
											return _Utils_eq(entry.dk, binding) && (_Utils_eq(entry.eE, protocolId) && _Utils_eq(
												$elm$core$Maybe$Just(entry.aa),
												receivedIntent));
										};
										var known = A2($elm$core$List$any, exact, model.U);
										if (!known) {
											return _Utils_Tuple2(model, _List_Nil);
										} else {
											var retained = _Utils_eq(
												A2(
													$elm$json$Json$Decode$decodeValue,
													A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string),
													raw),
												$elm$core$Result$Ok('Unknown')) ? model.U : A2(
												$elm$core$List$filter,
												A2($elm$core$Basics$composeR, exact, $elm$core$Basics$not),
												model.U);
											var _v50 = A2($author$project$Effects$apply, receipt, model._);
											var effects = _v50.a;
											var error = _v50.c;
											if (!_Utils_eq(error, $elm$core$Maybe$Nothing)) {
												return _Utils_Tuple2(model, _List_Nil);
											} else {
												var current = function () {
													var _v51 = model._.fS;
													if (_v51.$ === 1) {
														return false;
													} else {
														var transaction = _v51.a;
														return _Utils_eq(transaction.ay, protocolId) && _Utils_eq(
															$elm$core$Maybe$Just(transaction.aa),
															receivedIntent);
													}
												}();
												return ((!current) || ((!model.j) || (!_Utils_eq(
													model.dk,
													$elm$core$Maybe$Just(binding))))) ? _Utils_Tuple2(
													_Utils_update(
														model,
														{_: effects, U: retained}),
													_List_Nil) : $author$project$Shell$refreshObservations(
													_Utils_update(
														model,
														{_: effects, U: retained}));
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
		var _v0 = state.O;
		if (_v0.$ === 1) {
			return A4($author$project$MenuBridge$answer, model, shell, _List_Nil, $elm$core$Maybe$Nothing);
		} else {
			var slot = _v0.a;
			if ((!shell.j) || ((shell.j === 3) || (!_Utils_eq(
				shell.dk,
				$elm$core$Maybe$Just(
					$author$project$Provider$nativeBinding(slot.ax.c)))))) {
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
				var legacyReady = slot.bD || (_Utils_eq(
					response,
					$elm$core$Maybe$Just(
						_Utils_Tuple3(
							'action-projection',
							$author$project$Provider$nativeBinding(slot.ax.c),
							slot.bg))) && (_Utils_eq(
					previous.A,
					$elm$core$Maybe$Just(slot.bg)) && _Utils_eq(shell.A, $elm$core$Maybe$Nothing)));
				var geometryReady = slot.bA || function () {
					var _v7 = slot.bd;
					if (_v7.$ === 1) {
						return true;
					} else {
						var request = _v7.a;
						return _Utils_eq(
							response,
							$elm$core$Maybe$Just(
								_Utils_Tuple3(
									'geometry-facts',
									$author$project$Provider$nativeBinding(slot.ax.c),
									request))) && (_Utils_eq(
							previous.eb,
							$elm$core$Maybe$Just(request)) && _Utils_eq(shell.eb, $elm$core$Maybe$Nothing));
					}
				}();
				var lostCorrelation = ((!legacyReady) && (!_Utils_eq(
					shell.A,
					$elm$core$Maybe$Just(slot.bg)))) || ((!geometryReady) && (!_Utils_eq(shell.eb, slot.bd)));
				var updatedSlot = _Utils_update(
					slot,
					{bA: geometryReady, bD: legacyReady});
				var updated = _Utils_update(
					state,
					{
						O: $elm$core$Maybe$Just(updatedSlot)
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
							var scope = $author$project$Provider$presentationScope(slot.ax.c);
							var generation = A2(
								$elm$core$Maybe$withDefault,
								$author$project$UInt64$zero,
								A2(
									$elm$core$Maybe$map,
									A2(
										$elm$core$Basics$composeR,
										function ($) {
											return $.P;
										},
										function ($) {
											return $.c2;
										}),
									shell._.as));
							var _v1 = A3(
								$author$project$NativeProvider$fromShell,
								{e7: generation, dC: scope.dC, dI: scope.dI},
								$author$project$Provider$incarnation(slot.ax.c),
								shell);
							if (_v1.$ === 1) {
								var reason = _v1.a;
								return A3($author$project$MenuBridge$cancelPrepared, reason, shell, updated);
							} else {
								var fresh = _v1.a;
								var _v2 = $author$project$MenuBridge$operation(slot.e3);
								if (_v2.$ === 1) {
									return A3($author$project$MenuBridge$cancelPrepared, 'Selected operation unavailable', shell, updated);
								} else {
									var nativeOperation = _v2.a;
									var stamp = ($author$project$Provider$actionProtocol(slot.e3) === 2) ? $author$project$Shell$captureGeometry(shell) : $author$project$Shell$capture(shell);
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
											var _v6 = A5($author$project$ReceiptRouter$registerPrepared, slot.dq, slot.ax.c, fresh, command, state.au);
											if (_v6.$ === 1) {
												var reason = _v6.a;
												return A3($author$project$MenuBridge$cancelPrepared, reason, shell, updated);
											} else {
												var router = _v6.a;
												return A4(
													$author$project$MenuBridge$answer,
													_Utils_update(
														state,
														{O: $elm$core$Maybe$Nothing, au: router}),
													_Utils_update(
														issued,
														{d$: false}),
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
			aI: A2(
				$elm$core$Maybe$map,
				function (menu) {
					var _v1 = menu.W;
					if (_v1.$ === 1) {
						var intent = _v1.a;
						return _Utils_update(
							menu,
							{
								W: $author$project$Menu$Unknown(intent)
							});
					} else {
						return menu;
					}
				},
				state.aI),
			fx: A2(
				$elm$core$List$map,
				function (entry) {
					return _Utils_update(
						entry,
						{bq: true});
				},
				state.fx)
		});
};
var $author$project$MenuBridge$connectionLost = function (_v0) {
	var state = _v0;
	var canceled = function () {
		var _v2 = state.O;
		if (_v2.$ === 1) {
			return state.aI;
		} else {
			var slot = _v2.a;
			return A2(
				$author$project$Menu$update,
				A3(
					$author$project$Menu$ReceiveFor,
					slot.cq,
					slot.b0,
					$author$project$Menu$Refusal('Connection lost before dispatch')),
				state.aI).a;
		}
	}();
	var uncertain = $author$project$Menu$markDisconnected(canceled);
	var closed = function () {
		var _v1 = $author$project$Menu$snapshot(uncertain).aI;
		if (_v1.$ === 1) {
			return uncertain;
		} else {
			var view = _v1.a;
			return A2(
				$author$project$Menu$update,
				$author$project$Menu$Dismiss(view.cl),
				uncertain).a;
		}
	}();
	return _Utils_update(
		state,
		{aI: closed, O: $elm$core$Maybe$Nothing});
};
var $author$project$MenuBridge$preparedSnapshot = function (_v0) {
	var state = _v0;
	return A2(
		$elm$core$Maybe$map,
		function (slot) {
			return {bA: slot.bA, bd: slot.bd, bD: slot.bD, bg: slot.bg, bp: slot.bp};
		},
		state.O);
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
				$elm$json$Json$Encode$int(key.eE)),
				_Utils_Tuple2(
				'binding',
				$author$project$Binding$encode(key.dk)),
				_Utils_Tuple2(
				'intent',
				$author$project$Effects$encodeIntent(key.aa))
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
						return _Utils_eq(entry.a_, _native);
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
							return !_Utils_eq(item.a_, _native);
						},
						entries),
					$elm$core$Maybe$Just(
						A3(
							$author$project$Menu$ReceiveFor,
							entry.cq,
							entry.dk,
							$author$project$Menu$Refusal('The request was not sent. Choose again.'))));
			}
		}
	});
var $author$project$MenuBridge$locallyRefuseUnsent = F2(
	function (proved, model) {
		var state = model;
		var _v0 = A2($author$project$ReceiptRouter$locallyRefuseUnsent, proved, state.au);
		var router = _v0.a;
		var message = _v0.b;
		if (message.$ === 1) {
			return model;
		} else {
			var receipt = message.a;
			var _v2 = A2($author$project$Menu$update, receipt, state.aI);
			var menu = _v2.a;
			return _Utils_update(
				state,
				{aI: menu, au: router});
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
							return _Utils_eq(entry.a_, _native);
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
							return !_Utils_eq(item.cq, entry.cq);
						},
						entries);
					return _Utils_Tuple3(
						next,
						$elm$core$Maybe$Just(
							A3($author$project$Menu$ReceiveFor, entry.cq, entry.dk, outcome)),
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
					var _v1 = A2($author$project$ReceiptRouter$accept, raw, state.au);
					var router = _v1.a;
					var receipt = _v1.b;
					var error = _v1.c;
					if (receipt.$ === 1) {
						return _Utils_Tuple2(model, error);
					} else {
						var message = receipt.a;
						var _v3 = A2($author$project$Menu$update, message, state.aI);
						var menu = _v3.a;
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{aI: menu, au: router}),
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
							$author$project$UInt64$string(context.y))),
						_Utils_Tuple2(
						'revision',
						$elm$json$Json$Encode$string(
							$author$project$UInt64$string(context.c2)))
					]))));
};
var $author$project$Menu$rebindReady = F5(
	function (id, previous, fresh, items, model) {
		var state = model;
		var _v0 = state.aI;
		if (!_v0.$) {
			var current = _v0.a;
			return (state.az || ((!_Utils_eq(current.cl, id)) || ((!_Utils_eq(current.dk, previous)) || ((!_Utils_eq(current.W, $author$project$Menu$Ready)) || ((!_Utils_eq(current.fo, items)) || ((!$author$project$Menu$validItems(items)) || ((!A2($author$project$Menu$sameTarget, previous, fresh)) || ((!_Utils_eq(
				$author$project$Menu$outputTuple(previous),
				$author$project$Menu$outputTuple(fresh))) || (A2($elm$core$List$member, fresh, state.aY) || (A2(
				$elm$core$List$member,
				$author$project$Menu$outputTuple(fresh),
				state.a3) || A2(
				$elm$core$List$any,
				function (entry) {
					return A2($author$project$Menu$sameTarget, entry.dk, fresh);
				},
				state.fx))))))))))) ? model : _Utils_update(
				state,
				{
					aI: $elm$core$Maybe$Just(
						_Utils_update(
							current,
							{dk: fresh}))
				});
		} else {
			return model;
		}
	});
var $author$project$MenuBridge$reconcileWithShell = F2(
	function (shell, model) {
		var state = model;
		if (!shell.j) {
			return $author$project$MenuBridge$connectionLost(model);
		} else {
			if (!_Utils_eq(state.O, $elm$core$Maybe$Nothing)) {
				return model;
			} else {
				var _v0 = state.bJ;
				if (_v0.$ === 1) {
					return model;
				} else {
					var captured = _v0.a;
					var _v1 = shell._.as;
					if (_v1.$ === 1) {
						return model;
					} else {
						var observed = _v1.a;
						var retired = function () {
							var _v8 = A2(
								$author$project$Menu$update,
								$author$project$Menu$Invalidate(
									$author$project$Provider$getBinding(captured.c)),
								state.aI);
							var menu = _v8.a;
							return _Utils_update(
								state,
								{aI: menu});
						}();
						var previous = $author$project$Provider$nativeContext(captured.c);
						var sameAuthority = _Utils_eq(
							shell.dk,
							$elm$core$Maybe$Just(
								$author$project$Provider$nativeBinding(captured.c))) && (_Utils_eq(observed.P.fp, previous.fp) && (_Utils_eq(observed.P.fe, previous.fe) && _Utils_eq(observed.P.y, previous.y)));
						var liveRoot = _Utils_eq(
							A2(
								$author$project$ActionProjection$rootOf,
								$author$project$Provider$incarnation(captured.c),
								observed.eN),
							$elm$core$Maybe$Just(
								$author$project$Provider$incarnation(captured.c)));
						var changed = (!_Utils_eq(observed.P, previous)) || ((!sameAuthority) || ((!liveRoot) || (!_Utils_eq(
							A2(
								$elm$core$Maybe$map,
								function ($) {
									return $.P;
								},
								$author$project$Provider$geometryObservation(captured.c)),
							_Utils_eq(
								$author$project$Provider$geometryObservation(captured.c),
								$elm$core$Maybe$Nothing) ? $elm$core$Maybe$Nothing : A2(
								$elm$core$Maybe$map,
								function ($) {
									return $.P;
								},
								shell.ap)))));
						if (!changed) {
							return model;
						} else {
							var _v2 = $author$project$Menu$snapshot(state.aI).aI;
							if (!_v2.$) {
								var view = _v2.a;
								if ((!_Utils_eq(view.W, $author$project$Menu$Ready)) || ((!sameAuthority) || (!liveRoot))) {
									return retired;
								} else {
									if ((!_Utils_eq(shell.A, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(shell.eb, $elm$core$Maybe$Nothing)) || (!_Utils_eq(shell.ea, $elm$core$Maybe$Nothing)))) {
										return model;
									} else {
										if (!$author$project$Shell$available(shell)) {
											return retired;
										} else {
											var scope = $author$project$Provider$presentationScope(captured.c);
											var sameGeometry = function (fresh) {
												var _v5 = _Utils_Tuple2(
													$author$project$Provider$geometryObservation(captured.c),
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
															return A2($author$project$MenuBridge$sameWindowFacts, previousFacts.a, currentFacts.a) && (_Utils_eq(previousFacts.dk, currentFacts.dk) && (_Utils_eq(previousFacts.P.fp, currentFacts.P.fp) && (_Utils_eq(previousFacts.P.fe, currentFacts.P.fe) && _Utils_eq(previousFacts.P.y, currentFacts.P.y))));
														} else {
															break _v5$2;
														}
													}
												}
												return false;
											};
											var _v3 = A3(
												$author$project$NativeProvider$fromShell,
												{e7: observed.P.c2, dC: scope.dC, dI: scope.dI},
												$author$project$Provider$incarnation(captured.c),
												shell);
											if (_v3.$ === 1) {
												return retired;
											} else {
												var fresh = _v3.a;
												if ((!_Utils_eq(
													$author$project$Provider$getItems(fresh),
													$author$project$Provider$getItems(captured.c))) || ((!_Utils_eq(
													$author$project$Provider$title(fresh),
													$author$project$Provider$title(captured.c))) || (!sameGeometry(fresh)))) {
													return retired;
												} else {
													var _v4 = $author$project$MenuBridge$providerStamp(fresh);
													if (_v4.$ === 1) {
														return retired;
													} else {
														var stamp = _v4.a;
														var refreshed = A5(
															$author$project$Menu$rebindReady,
															view.cl,
															view.dk,
															$author$project$Provider$getBinding(fresh),
															$author$project$Provider$getItems(fresh),
															state.aI);
														return (!_Utils_eq(
															A2(
																$elm$core$Maybe$map,
																function ($) {
																	return $.dk;
																},
																$author$project$Menu$snapshot(refreshed).aI),
															$elm$core$Maybe$Just(
																$author$project$Provider$getBinding(fresh)))) ? retired : _Utils_update(
															state,
															{
																aI: refreshed,
																bJ: $elm$core$Maybe$Just(
																	{c: fresh, db: stamp})
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
										model.h).a : model.h;
								case 'host-disconnected':
									return $author$project$MenuBridge$connectionLost(model.h);
								default:
									break _v4$2;
							}
						} else {
							break _v4$2;
						}
					}
					return model.h;
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
						model.h,
						operations);
				case 12:
					var operations = message.a;
					return A2($author$project$Shell$canProveUnsent, operations, model.b) ? A3($elm$core$List$foldl, $author$project$MenuBridge$locallyRefuseUnsent, model.h, operations) : model.h;
				default:
					return model.h;
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
								ft: A2($elm$core$Maybe$withDefault, next.ft, error)
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
		var settledMenus = A2($author$project$MenuBridge$reconcileWithShell, advanced.b, advanced.dW);
		var picker = A2(
			$elm$core$Maybe$andThen,
			function (current) {
				return (_Utils_eq(
					$author$project$Shell$capture(shell),
					$elm$core$Maybe$Just(current.c5)) && $author$project$Shell$available(shell)) ? $elm$core$Maybe$Just(current) : $elm$core$Maybe$Nothing;
			},
			model.J);
		return _Utils_Tuple2(
			_Utils_update(
				model,
				{
					h: settledMenus,
					J: picker,
					b: _Utils_update(
						finalShell,
						{
							ft: A2($elm$core$Maybe$withDefault, finalShell.ft, advanced.d3)
						})
				}),
			_Utils_ap(effects, advanced._));
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
		var _v0 = state.O;
		if (!_v0.$) {
			var slot = _v0.a;
			return _Utils_eq(slot.bp, token) ? A3($author$project$MenuBridge$cancelPrepared, 'Selection canceled before dispatch', shell, model) : A4($author$project$MenuBridge$answer, model, shell, _List_Nil, $elm$core$Maybe$Nothing);
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
			shell.dk,
			$elm$core$Maybe$Just(
				$author$project$Provider$nativeBinding(captured.c))) && (_Utils_eq(
			$author$project$Shell$capture(shell),
			$elm$core$Maybe$Just(captured.db)) && (_Utils_eq(
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.P;
				},
				$author$project$Provider$geometryObservation(captured.c)),
			_Utils_eq(
				$author$project$Provider$geometryObservation(captured.c),
				$elm$core$Maybe$Nothing) ? $elm$core$Maybe$Nothing : A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.P;
				},
				shell.ap)) && (_Utils_eq(
			A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.P;
				},
				shell._.as),
			$elm$core$Maybe$Just(
				$author$project$Provider$nativeContext(captured.c))) && _Utils_eq(
			A2(
				$elm$core$Maybe$andThen,
				function (observed) {
					return A2(
						$author$project$ActionProjection$rootOf,
						$author$project$Provider$incarnation(captured.c),
						observed.eN);
				},
				shell._.as),
			$elm$core$Maybe$Just(
				$author$project$Provider$incarnation(captured.c))))));
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
				var _v1 = state.O;
				if (!_v1.$) {
					var slot = _v1.a;
					return _Utils_eq(slot.dx, id) ? A3($author$project$MenuBridge$cancelPrepared, 'Selection canceled before dispatch', shell, model) : A4($author$project$MenuBridge$answer, model, shell, _List_Nil, $elm$core$Maybe$Nothing);
				} else {
					return A4(
						$author$project$MenuBridge$answer,
						_Utils_update(
							state,
							{
								aI: A2($author$project$Menu$update, message, state.aI).a
							}),
						shell,
						_List_Nil,
						$elm$core$Maybe$Nothing);
				}
			case 6:
				var binding = message.a;
				var _v2 = state.O;
				if (!_v2.$) {
					var slot = _v2.a;
					return _Utils_eq(slot.b0, binding) ? A3($author$project$MenuBridge$cancelPrepared, 'Selection authority retired', shell, model) : A4(
						$author$project$MenuBridge$answer,
						_Utils_update(
							state,
							{
								aI: A2($author$project$Menu$update, message, state.aI).a
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
								aI: A2($author$project$Menu$update, message, state.aI).a
							}),
						shell,
						_List_Nil,
						$elm$core$Maybe$Nothing);
				}
			case 7:
				var output = message.a;
				var generation = message.b;
				var _v3 = state.O;
				if (!_v3.$) {
					var slot = _v3.a;
					return (_Utils_eq(
						$author$project$Menu$outputId(
							$author$project$UInt64$string(
								$author$project$Provider$presentationScope(slot.ax.c).dC)),
						output) && _Utils_eq(
						$author$project$UInt64$string(
							$author$project$Provider$nativeContext(slot.ax.c).y),
						generation)) ? A3($author$project$MenuBridge$cancelPrepared, 'Selection output retired', shell, model) : A4(
						$author$project$MenuBridge$answer,
						_Utils_update(
							state,
							{
								aI: A2($author$project$Menu$update, message, state.aI).a
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
								aI: A2($author$project$Menu$update, message, state.aI).a
							}),
						shell,
						_List_Nil,
						$elm$core$Maybe$Nothing);
				}
			default:
				var preblocked = function () {
					var _v12 = _Utils_Tuple2(message, state.bJ);
					if ((_v12.a.$ === 3) && (!_v12.b.$)) {
						var _v13 = _v12.a;
						var captured = _v12.b.a;
						return A3(
							$author$project$MenuBridge$blockedFor,
							$author$project$Provider$incarnation(captured.c),
							shell,
							model);
					} else {
						return false;
					}
				}();
				var _v4 = A2($author$project$Menu$update, message, state.aI);
				var menu = _v4.a;
				var effects = _v4.b;
				var updated = _Utils_update(
					state,
					{aI: menu});
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
								state.bJ,
								$author$project$MenuBridge$operation(action));
							if ((!_v6.a.$) && (!_v6.b.$)) {
								var captured = _v6.a.a;
								if ((!_Utils_eq(
									$author$project$Provider$getBinding(captured.c),
									binding)) || ((!A2($author$project$MenuBridge$providerMatches, captured, shell)) || (($author$project$Provider$actionProtocol(action) === 2) && ((!_Utils_eq(shell.eb, $elm$core$Maybe$Nothing)) || (!_Utils_eq(shell.ea, $elm$core$Maybe$Nothing)))))) {
									return rejected('Native window information changed; choose again');
								} else {
									var _v7 = _Utils_Tuple3(
										state.O,
										$author$project$UInt64$next(state.dG),
										_Utils_Tuple2(
											$author$project$Menu$snapshot(state.aI).aI,
											shell._.as));
									if ((((_v7.a.$ === 1) && (!_v7.b.$)) && (!_v7.c.a.$)) && (!_v7.c.b.$)) {
										var _v8 = _v7.a;
										var token = _v7.b.a;
										var _v9 = _v7.c;
										var view = _v9.a.a;
										var observed = _v9.b.a;
										var needsGeometry = !_Utils_eq(
											$author$project$Provider$geometryObservation(captured.c),
											$elm$core$Maybe$Nothing);
										var closed = A2(
											$author$project$Menu$update,
											$author$project$Menu$Dismiss(view.cl),
											menu).a;
										var _v10 = A2($author$project$Shell$update, $author$project$Shell$Refresh, shell);
										var refreshing = _v10.a;
										var requests = _v10.b;
										var _v11 = refreshing.A;
										if (_v11.$ === 1) {
											return rejected('Post-close window observation unavailable');
										} else {
											var legacyRequest = _v11.a;
											if ($elm$core$List$isEmpty(requests) || (needsGeometry && _Utils_eq(refreshing.eb, $elm$core$Maybe$Nothing))) {
												return rejected('Post-close geometry observation unavailable');
											} else {
												var slot = {
													e3: action,
													ax: captured,
													dq: dispatch,
													ds: shell.ds,
													bA: !needsGeometry,
													bd: refreshing.eb,
													bD: false,
													bg: legacyRequest,
													dw: $author$project$ActionProjection$windows(observed.eN),
													cq: local,
													dx: view.cl,
													b0: binding,
													bp: token
												};
												return A4(
													$author$project$MenuBridge$answer,
													_Utils_update(
														state,
														{
															aI: closed,
															O: $elm$core$Maybe$Just(slot),
															dG: token
														}),
													_Utils_update(
														refreshing,
														{d$: true}),
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
	var _v0 = $author$project$MenuBridge$menuSnapshot(model.h).aI;
	if (_v0.$ === 1) {
		return model;
	} else {
		var view = _v0.a;
		var result = A3(
			$author$project$MenuBridge$menuEvent,
			$author$project$Menu$Dismiss(view.cl),
			model.b,
			model.h);
		return _Utils_update(
			model,
			{h: result.dW});
	}
};
var $author$project$MenuBridge$expirePrepared = F3(
	function (token, shell, model) {
		var state = model;
		var _v0 = state.O;
		if (!_v0.$) {
			var slot = _v0.a;
			return _Utils_eq(slot.bp, token) ? A3($author$project$MenuBridge$cancelPrepared, 'Window information took too long. Choose again.', shell, model) : A4($author$project$MenuBridge$answer, model, shell, _List_Nil, $elm$core$Maybe$Nothing);
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
	return A2($author$project$Menu$Open, value.dk, value.fo);
};
var $author$project$MenuBridge$open = F2(
	function (provider, model) {
		var state = model;
		if (!_Utils_eq(state.O, $elm$core$Maybe$Nothing)) {
			return model;
		} else {
			var _v0 = $author$project$MenuBridge$providerStamp(provider);
			if (_v0.$ === 1) {
				return model;
			} else {
				var stamp = _v0.a;
				var before = $author$project$Menu$snapshot(state.aI);
				var _v1 = A2(
					$author$project$Menu$update,
					$author$project$Provider$toOpen(provider),
					state.aI);
				var menu = _v1.a;
				return _Utils_eq(
					$author$project$Menu$snapshot(menu).aI,
					before.aI) ? model : _Utils_update(
					state,
					{
						aI: menu,
						bJ: $elm$core$Maybe$Just(
							{c: provider, db: stamp})
					});
			}
		}
	});
var $author$project$Taskbar$selection = function (entry) {
	return (!entry.dj) ? $author$project$Taskbar$Unavailable : A2(
		$author$project$Taskbar$Apply,
		entry.b_ ? $author$project$Effects$Restore : $author$project$Effects$Activate,
		entry.r);
};
var $author$project$TaskbarShell$valid = F2(
	function (scope, model) {
		return _Utils_eq(
			$author$project$MenuBridge$preparedSnapshot(model.h),
			$elm$core$Maybe$Nothing) && (_Utils_eq(
			$author$project$Shell$capture(model.b),
			$elm$core$Maybe$Just(scope)) && $author$project$Shell$available(model.b));
	});
var $author$project$TaskbarShell$update = F2(
	function (message, model) {
		switch (message.$) {
			case 4:
				var provider = message.a;
				var menus = A2($author$project$MenuBridge$open, provider, model.h);
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							h: menus,
							J: _Utils_eq(menus, model.h) ? model.J : $elm$core$Maybe$Nothing
						}),
					_List_Nil);
			case 5:
				var event = message.a;
				var result = A3($author$project$MenuBridge$menuEvent, event, model.b, model.h);
				var shell = result.b;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							h: result.dW,
							J: $elm$core$List$isEmpty(result._) ? model.J : $elm$core$Maybe$Nothing,
							b: _Utils_update(
								shell,
								{
									ft: A2($elm$core$Maybe$withDefault, shell.ft, result.d3)
								})
						}),
					result._);
			case 7:
				var token = message.a;
				var result = A3($author$project$MenuBridge$cancelSelection, token, model.b, model.h);
				var shell = result.b;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							h: result.dW,
							b: _Utils_update(
								shell,
								{
									ft: A2($elm$core$Maybe$withDefault, shell.ft, result.d3)
								})
						}),
					result._);
			case 6:
				var token = message.a;
				var result = A3($author$project$MenuBridge$expirePrepared, token, model.b, model.h);
				var shell = result.b;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							h: result.dW,
							b: _Utils_update(
								shell,
								{
									ft: A2($elm$core$Maybe$withDefault, shell.ft, result.d3)
								})
						}),
					result._);
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
								return _Utils_eq(group.a_, key);
							},
							$author$project$TaskbarShell$groups(model)));
					if (_v1.$ === 1) {
						return _Utils_Tuple2(model, _List_Nil);
					} else {
						var group = _v1.a;
						var base = $author$project$TaskbarShell$dismissMenus(model);
						var _v2 = A2($author$project$Taskbar$primary, false, group.aG);
						if (_v2.$ === 1) {
							var _v3 = $author$project$UInt64$next(model.fh);
							if (!_v3.$) {
								var generation = _v3.a;
								return _Utils_Tuple2(
									_Utils_update(
										base,
										{
											fh: generation,
											J: $elm$core$Maybe$Just(
												{fh: generation, a_: key, c5: scope})
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
					return ((!A2($author$project$TaskbarShell$valid, scope, model)) || ((!_Utils_eq(picker.c5, scope)) || (!_Utils_eq(picker.fh, generation)))) ? _Utils_Tuple2(model, _List_Nil) : A2(
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
										return _Utils_eq(family.r, root);
									},
									A2(
										$elm$core$List$concatMap,
										function ($) {
											return $.aG;
										},
										A2(
											$elm$core$List$filter,
											function (group) {
												return _Utils_eq(group.a_, picker.a_);
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
					return (_Utils_eq(picker.c5, scope) && _Utils_eq(picker.fh, generation)) ? _Utils_Tuple2(
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
		return _Utils_eq(current.dk, choice.c.dk) && (_Utils_eq(current.P.fp, choice.c.P.fp) && (_Utils_eq(current.P.fe, choice.c.P.fe) && (_Utils_eq(current.P.y, choice.c.P.y) && A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (window) {
					return (current.e6 || window.dr) && ((!window.b_) && (window.bX && ((!window.bB) && ((!window.fg) && (_Utils_eq(window.dD, $elm$core$Maybe$Nothing) && ((!window.es) && ((!window.cg) && (_Utils_eq(
						A2(
							$elm$core$Maybe$map,
							function ($) {
								return $.c9;
							},
							A2($author$project$GeometryProjection$window, choice.fR, choice.c)),
						$elm$core$Maybe$Just(window.c9)) && _Utils_eq(
						$author$project$Snap$proposal(
							_Utils_update(
								choice,
								{c: current})),
						A2(
							$elm$core$Maybe$map,
							function (prior) {
								return _Utils_update(
									prior,
									{P: current.P});
							},
							$author$project$Snap$proposal(choice)))))))))));
				},
				A2($author$project$GeometryProjection$window, choice.fR, current))))));
	});
var $author$project$Desktop$windowBase = F2(
	function (message, model) {
		var _v0 = A2($author$project$TaskbarShell$update, message, model.a);
		var windows = _v0.a;
		var effects = _v0.b;
		var changed = !_Utils_eq(windows.b.dk, model.a.b.dk);
		var disconnected = !windows.b.j;
		var pins = (disconnected || changed) ? $author$project$Pins$initial : model.R;
		var launch = disconnected ? $author$project$Launch$disconnect(model.M) : (changed ? A2(
			$elm$core$Maybe$withDefault,
			$author$project$Launch$disconnect(model.M),
			A2(
				$elm$core$Maybe$map,
				function (binding) {
					return A2(
						$author$project$Launch$bind,
						$author$project$Desktop$host(binding),
						model.M);
				},
				windows.b.dk)) : model.M);
		var read = (changed && (!disconnected)) ? A2(
			$elm$core$Maybe$andThen,
			function (binding) {
				return A2(
					$elm$core$Maybe$map,
					function (request) {
						return _Utils_Tuple2(binding, request);
					},
					$author$project$UInt64$next(model.c1));
			},
			windows.b.dk) : $elm$core$Maybe$Nothing;
		var settingsRead = A2(
			$elm$core$Maybe$andThen,
			function (_v11) {
				var binding = _v11.a;
				var request = _v11.b;
				return A2(
					$elm$core$Maybe$map,
					function (next) {
						return _Utils_Tuple2(binding, next);
					},
					$author$project$UInt64$next(request));
			},
			read);
		var motionRead = A2(
			$elm$core$Maybe$andThen,
			function (_v10) {
				var binding = _v10.a;
				var request = _v10.b;
				return A2(
					$elm$core$Maybe$map,
					function (next) {
						return _Utils_Tuple2(binding, next);
					},
					$author$project$UInt64$next(request));
			},
			settingsRead);
		var shortcutsRead = A2(
			$elm$core$Maybe$andThen,
			function (_v9) {
				var binding = _v9.a;
				var request = _v9.b;
				return A2(
					$elm$core$Maybe$map,
					function (next) {
						return _Utils_Tuple2(binding, next);
					},
					$author$project$UInt64$next(request));
			},
			motionRead);
		return _Utils_Tuple2(
			((disconnected || changed) ? $author$project$Desktop$advance : $elm$core$Basics$identity)(
				_Utils_update(
					model,
					{
						F: (disconnected && (!(!model.a.b.j))) ? A2(
							$elm$core$Maybe$map,
							function (binding) {
								return A2($author$project$AdapterNotice$connectionLost, binding, model.a.b.c1);
							},
							model.a.b.dk) : (changed ? $elm$core$Maybe$Nothing : model.F),
						aD: (disconnected || changed) ? $elm$core$Maybe$Nothing : model.aD,
						bu: (disconnected || changed) ? $elm$core$Maybe$Nothing : model.bu,
						k: (disconnected || (changed || (windows.b.j === 3))) ? $elm$core$Maybe$Nothing : model.k,
						G: (disconnected || changed) ? '' : model.G,
						A: (disconnected || changed) ? A2($elm$core$Maybe$map, $elm$core$Tuple$second, read) : model.A,
						T: (disconnected || changed) ? $author$project$Files$disconnect(model.T) : model.T,
						aW: (disconnected || changed) ? $elm$core$Maybe$Nothing : model.aW,
						p: (disconnected || (changed || (windows.b.j === 3))) ? false : model.p,
						B: (disconnected || (changed || (windows.b.j === 3))) ? false : model.B,
						o: (disconnected || (changed || (windows.b.j === 3))) ? $elm$core$Maybe$Nothing : model.o,
						aZ: (disconnected || changed) ? $elm$core$Maybe$Nothing : model.aZ,
						ar: (disconnected || changed) ? $author$project$JumpList$disconnect(model.ar) : model.ar,
						w: (disconnected || (changed || (windows.b.j === 3))) ? false : model.w,
						M: launch,
						H: (disconnected || (changed || _Utils_eq(
							$author$project$MenuBridge$menuSnapshot(windows.h).aI,
							$elm$core$Maybe$Nothing))) ? $elm$core$Maybe$Nothing : model.H,
						I: (disconnected || changed) ? $author$project$Motion$rebind(model.I) : model.I,
						aK: (disconnected || changed) ? A2($elm$core$Maybe$map, $elm$core$Tuple$second, motionRead) : model.aK,
						ah: (disconnected || (changed || (windows.b.j === 3))) ? $elm$core$Maybe$Nothing : model.ah,
						C: (disconnected || changed) ? $author$project$Notifications$initial : model.C,
						a0: (disconnected || changed) ? $elm$core$Maybe$Nothing : model.a0,
						t: (disconnected || (changed || (windows.b.j === 3))) ? false : model.t,
						D: (disconnected || (changed || (windows.b.j === 3))) ? false : model.D,
						m: (disconnected || (changed || (windows.b.j === 3))) ? false : model.m,
						aB: (disconnected || (changed || (!model.m))) ? $elm$core$Maybe$Nothing : model.aB,
						at: (disconnected || changed) ? $elm$core$Maybe$Nothing : model.at,
						R: pins,
						c1: A2(
							$elm$core$Maybe$withDefault,
							A2(
								$elm$core$Maybe$withDefault,
								A2(
									$elm$core$Maybe$withDefault,
									A2(
										$elm$core$Maybe$withDefault,
										model.c1,
										A2($elm$core$Maybe$map, $elm$core$Tuple$second, read)),
									A2($elm$core$Maybe$map, $elm$core$Tuple$second, settingsRead)),
								A2($elm$core$Maybe$map, $elm$core$Tuple$second, motionRead)),
							A2($elm$core$Maybe$map, $elm$core$Tuple$second, shortcutsRead)),
						u: (disconnected || changed) ? $elm$core$Maybe$Nothing : model.u,
						aj: (disconnected || changed) ? $author$project$Settings$initial : model.aj,
						bo: (disconnected || changed) ? A2($elm$core$Maybe$map, $elm$core$Tuple$second, settingsRead) : model.bo,
						n: (disconnected || (changed || (windows.b.j === 3))) ? false : model.n,
						L: (disconnected || (changed || (windows.b.j === 3))) ? false : model.L,
						aQ: (disconnected || changed) ? A2($elm$core$Maybe$map, $elm$core$Tuple$second, shortcutsRead) : model.aQ,
						ac: (disconnected || changed) ? $author$project$ShortcutPreferences$initial : model.ac,
						b8: (disconnected || changed) ? $author$project$Shortcuts$initial : model.b8,
						x: (disconnected || (changed || (windows.b.j === 3))) ? $elm$core$Maybe$Nothing : A2(
							$elm$core$Maybe$andThen,
							function (choice) {
								var _v1 = windows.b.ap;
								if (_v1.$ === 1) {
									return $elm$core$Maybe$Just(choice);
								} else {
									var geometry = _v1.a;
									return A2($author$project$Snap$valid, geometry, choice) ? $elm$core$Maybe$Just(
										_Utils_update(
											choice,
											{c: geometry})) : $elm$core$Maybe$Nothing;
								}
							},
							model.x),
						i: (disconnected || (changed || (windows.b.j === 3))) ? A2(
							$author$project$Switcher$cancel,
							$author$project$Switcher$generation(model.i),
							model.i) : model.i,
						aR: (disconnected || (changed || (windows.b.j === 3))) ? $elm$core$Maybe$Nothing : model.aR,
						aS: (disconnected || (changed || (windows.b.j === 3))) ? $elm$core$Maybe$Nothing : model.aS,
						ak: (disconnected || changed) ? $author$project$SystemMenu$initial : model.ak,
						s: (disconnected || (changed || (windows.b.j === 3))) ? $elm$core$Maybe$Nothing : model.s,
						aT: (disconnected || changed) ? $elm$core$Maybe$Nothing : model.aT,
						v: (disconnected || (changed || (windows.b.j === 3))) ? false : model.v,
						E: (disconnected || (changed || (windows.b.j === 3))) ? false : model.E,
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
					A2(
						$elm$core$Maybe$withDefault,
						_List_Nil,
						A2(
							$elm$core$Maybe$map,
							function (_v3) {
								var binding = _v3.a;
								var request = _v3.b;
								return _List_fromArray(
									[
										A2($author$project$Desktop$settingsRequest, binding, request)
									]);
							},
							settingsRead)),
					_Utils_ap(
						A2(
							$elm$core$Maybe$withDefault,
							_List_Nil,
							A2(
								$elm$core$Maybe$map,
								function (_v4) {
									var binding = _v4.a;
									var request = _v4.b;
									return _List_fromArray(
										[
											A2($author$project$Desktop$motionPreferencesRequest, binding, request)
										]);
								},
								motionRead)),
						_Utils_ap(
							A2(
								$elm$core$Maybe$withDefault,
								_List_Nil,
								A2(
									$elm$core$Maybe$map,
									function (_v5) {
										var binding = _v5.a;
										var request = _v5.b;
										return _List_fromArray(
											[
												A2($author$project$Desktop$shortcutPreferencesRequest, binding, request)
											]);
									},
									shortcutsRead)),
							_Utils_ap(
								A2($elm$core$List$map, $author$project$Desktop$WindowEffect, effects),
								function () {
									var _v6 = _Utils_Tuple3(model.a.J, windows.J, message);
									if (!_v6.b.$) {
										var prior = _v6.a;
										var picker = _v6.b.a;
										return _Utils_eq(
											A2(
												$elm$core$Maybe$map,
												function ($) {
													return $.fh;
												},
												prior),
											$elm$core$Maybe$Just(picker.fh)) ? _List_Nil : A2(
											$elm$core$Maybe$withDefault,
											_List_Nil,
											A2(
												$elm$core$Maybe$map,
												function (family) {
													return _List_fromArray(
														[
															$author$project$Desktop$Focus(
															'picker:' + ($author$project$Shell$stampKey(picker.c5) + (':' + ($author$project$UInt64$string(picker.fh) + (':' + $author$project$UInt64$string(family.r))))))
														]);
												},
												$elm$core$List$head(
													A2(
														$elm$core$List$filter,
														function ($) {
															return $.dj;
														},
														A2(
															$elm$core$List$concatMap,
															function ($) {
																return $.aG;
															},
															A2(
																$elm$core$List$filter,
																function (group) {
																	return _Utils_eq(group.a_, picker.a_);
																},
																$author$project$TaskbarShell$groups(windows)))))));
									} else {
										if ((!_v6.a.$) && (_v6.c.$ === 3)) {
											var picker = _v6.a.a;
											var _v7 = _v6.b;
											var _v8 = _v6.c;
											var scope = _v8.a;
											var generation = _v8.b;
											return (_Utils_eq(picker.c5, scope) && (_Utils_eq(picker.fh, generation) && _Utils_eq(
												$author$project$Shell$capture(windows.b),
												$elm$core$Maybe$Just(scope)))) ? _List_fromArray(
												[
													$author$project$Desktop$Focus(
													'group:' + ($author$project$Shell$stampKey(scope) + (':' + picker.a_)))
												]) : _List_Nil;
										} else {
											return _List_Nil;
										}
									}
								}()))))));
	});
var $author$project$Desktop$chooseFamily = F2(
	function (family, model) {
		var _v0 = _Utils_Tuple2(model.a.b.dk, model.a.b._.as);
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var binding = _v0.a.a;
			var observed = _v0.b.a;
			if ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) || A3($author$project$MenuBridge$blockedFor, family.r, model.a.b, model.a.h)) {
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
							{G: '', m: false, aN: $author$project$OverviewRecovery$initial})));
				var next = _v1.a;
				var effects = _v1.b;
				var _v2 = next.a.b.A;
				if (!_v2.$) {
					var request = _v2.a;
					var token = A2($author$project$Desktop$ChoiceToken, binding, request);
					return _Utils_Tuple2(
						_Utils_update(
							next,
							{
								k: $elm$core$Maybe$Just(
									{
										di: family.di,
										dk: binding,
										aV: A2(
											$elm$core$Maybe$map,
											function ($) {
												return $.fh;
											},
											model.ah),
										y: observed.P.y,
										bk: $elm$core$Maybe$Nothing,
										r: family.r,
										bp: token,
										a4: $elm$core$Maybe$Nothing
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
		{fh: token, j: 1});
};
var $author$project$Switcher$prepare = F2(
	function (token, model) {
		var _v0 = A2($author$project$UInt64$compare, token, model.fh);
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
				return A2($elm$core$Dict$member, ordinal, model.bO);
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
			model.c0));
	if ((!model.b5) || (!complete)) {
		return _Utils_Tuple2(
			_Utils_update(
				model,
				{j: 1}),
			$elm$core$Maybe$Nothing);
	} else {
		if ($elm$core$List$isEmpty(model.af)) {
			return _Utils_Tuple2(
				_Utils_update(
					model,
					{j: 3}),
				$elm$core$Maybe$Nothing);
		} else {
			if (!_Utils_eq(model.c0, $elm$core$Maybe$Nothing)) {
				var current = _Utils_update(
					model,
					{j: 3});
				return _Utils_Tuple2(
					current,
					$author$project$Switcher$selected(current));
			} else {
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{j: 2}),
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
					var _v1 = model.c0;
					if (!_v1.$) {
						return _Utils_Tuple2(original, $elm$core$Maybe$Nothing);
					} else {
						return $author$project$Switcher$settle(
							_Utils_update(
								model,
								{
									c0: $elm$core$Maybe$Just(ordinal)
								}));
					}
				}
			}
		}
	});
var $author$project$Switcher$commit = F2(
	function (token, original) {
		var model = original;
		return ((!_Utils_eq(token, model.fh)) || (model.j !== 2)) ? _Utils_Tuple2(original, $elm$core$Maybe$Nothing) : A3(
			$author$project$Switcher$release,
			token,
			$author$project$Switcher$lastOrdinal(model),
			original);
	});
var $author$project$Notifications$configure = F2(
	function (policy, model) {
		return _Utils_update(
			model,
			{fD: policy});
	});
var $author$project$SystemMenu$confirmed = function (value) {
	return A2(
		$elm$core$List$member,
		value.bh,
		_List_fromArray(
			[4, 5, 7])) || ((value.bh === 2) && (!value.Y));
};
var $author$project$Files$Peer = F5(
	function (pid, start, instance, target, visible) {
		return {du: instance, dE: pid, dN: start, fR: target, eW: visible};
	});
var $author$project$Files$Snapshot = F5(
	function (service, revision, available, reason, peer) {
		return {dj: available, b2: peer, eH: reason, c2: revision, c7: service};
	});
var $author$project$Files$bounded = function (limit) {
	return A2(
		$elm$json$Json$Decode$andThen,
		function (value) {
			return ((_Utils_cmp(
				$elm$core$String$length(value),
				limit) < 1) && $author$project$Files$textValid(value)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Files text');
		},
		$elm$json$Json$Decode$string);
};
var $author$project$Files$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return _Utils_eq(value, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Files identity') : $elm$json$Json$Decode$succeed(value);
	},
	$author$project$UInt64$decoder);
var $author$project$Files$strict = F2(
	function (fields, child) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? child : $elm$json$Json$Decode$fail('Files fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$Files$decoder = A2(
	$elm$json$Json$Decode$andThen,
	function (snapshot) {
		return ((!snapshot.dj) && (!_Utils_eq(snapshot.b2, $elm$core$Maybe$Nothing))) ? $elm$json$Json$Decode$fail('Unavailable Files peer') : $elm$json$Json$Decode$succeed(snapshot);
	},
	A2(
		$author$project$Files$strict,
		_List_fromArray(
			['service', 'revision', 'available', 'reason', 'peer']),
		A6(
			$elm$json$Json$Decode$map5,
			$author$project$Files$Snapshot,
			A2($elm$json$Json$Decode$field, 'service', $author$project$Files$positive),
			A2($elm$json$Json$Decode$field, 'revision', $author$project$Files$positive),
			A2($elm$json$Json$Decode$field, 'available', $elm$json$Json$Decode$bool),
			A2(
				$elm$json$Json$Decode$field,
				'reason',
				$author$project$Files$bounded(128)),
			A2(
				$elm$json$Json$Decode$field,
				'peer',
				$elm$json$Json$Decode$nullable(
					A2(
						$author$project$Files$strict,
						_List_fromArray(
							['pid', 'start', 'instance', 'target', 'visible']),
						A6(
							$elm$json$Json$Decode$map5,
							$author$project$Files$Peer,
							A2($elm$json$Json$Decode$field, 'pid', $author$project$Files$positive),
							A2($elm$json$Json$Decode$field, 'start', $author$project$Files$positive),
							A2(
								$elm$json$Json$Decode$field,
								'instance',
								A2(
									$elm$json$Json$Decode$andThen,
									function (value) {
										return ((!$elm$core$String$isEmpty(value)) && A2(
											$elm$core$String$all,
											function (c) {
												return $elm$core$Char$isAlphaNum(c) || ((c === '_') || (c === '-'));
											},
											value)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Files instance');
									},
									$author$project$Files$bounded(128))),
							A2(
								$elm$json$Json$Decode$field,
								'target',
								A2(
									$elm$json$Json$Decode$andThen,
									function (value) {
										return ($author$project$Files$validTarget(value) && (!A2($elm$core$String$startsWith, '~', value))) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Files observed target');
									},
									$author$project$Files$bounded(512))),
							A2($elm$json$Json$Decode$field, 'visible', $elm$json$Json$Decode$bool))))))));
var $author$project$JumpList$Snapshot = F7(
	function (service, revision, entry, name, available, reason, actions) {
		return {cG: actions, dj: available, d2: entry, dA: name, eH: reason, c2: revision, c7: service};
	});
var $author$project$JumpList$Action = F3(
	function (id, label, kind) {
		return {cl: id, ej: kind, el: label};
	});
var $author$project$JumpList$bounded = F2(
	function (limit, nonempty) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (value) {
				return ((_Utils_cmp(
					$elm$core$String$length(value),
					limit) < 1) && (((!nonempty) || (!$elm$core$String$isEmpty(value))) && (!A2(
					$elm$core$String$any,
					function (c) {
						return ($elm$core$Char$toCode(c) < 32) || ($elm$core$Char$toCode(c) === 127);
					},
					value)))) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Jump list text');
			},
			$elm$json$Json$Decode$string);
	});
var $author$project$JumpList$strict = F2(
	function (fields, child) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? child : $elm$json$Json$Decode$fail('Jump list fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$JumpList$actionDecoder = A2(
	$author$project$JumpList$strict,
	_List_fromArray(
		['id', 'label', 'kind']),
	A4(
		$elm$json$Json$Decode$map3,
		$author$project$JumpList$Action,
		A2(
			$elm$json$Json$Decode$field,
			'id',
			A2($author$project$JumpList$bounded, 256, true)),
		A2(
			$elm$json$Json$Decode$field,
			'label',
			A2($author$project$JumpList$bounded, 512, true)),
		A2(
			$elm$json$Json$Decode$field,
			'kind',
			A2(
				$elm$json$Json$Decode$andThen,
				function (value) {
					return A2(
						$elm$core$List$member,
						value,
						_List_fromArray(
							['desktop', 'recent'])) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Unsupported action kind');
				},
				$elm$json$Json$Decode$string))));
var $author$project$JumpList$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return _Utils_eq(value, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Jump list identity') : $elm$json$Json$Decode$succeed(value);
	},
	$author$project$UInt64$decoder);
var $author$project$JumpList$decoder = A2(
	$elm$json$Json$Decode$andThen,
	function (snapshot) {
		var keys = A2(
			$elm$core$List$map,
			function ($) {
				return $.cl;
			},
			snapshot.cG);
		var unique = A3(
			$elm$core$List$foldl,
			F2(
				function (key, seen) {
					return A2($elm$core$List$member, key, seen) ? seen : A2($elm$core$List$cons, key, seen);
				}),
			_List_Nil,
			keys);
		return (($elm$core$List$length(keys) > 44) || ((!_Utils_eq(
			$elm$core$List$length(keys),
			$elm$core$List$length(unique))) || (((!snapshot.dj) && (!$elm$core$List$isEmpty(keys))) || A2(
			$elm$core$List$any,
			function (row) {
				return !A2($elm$core$String$startsWith, row.ej + ':', row.cl);
			},
			snapshot.cG)))) ? $elm$json$Json$Decode$fail('Jump list actions') : $elm$json$Json$Decode$succeed(snapshot);
	},
	A2(
		$author$project$JumpList$strict,
		_List_fromArray(
			['service', 'revision', 'entry', 'name', 'available', 'reason', 'actions']),
		A8(
			$elm$json$Json$Decode$map7,
			$author$project$JumpList$Snapshot,
			A2($elm$json$Json$Decode$field, 'service', $author$project$JumpList$positive),
			A2($elm$json$Json$Decode$field, 'revision', $author$project$JumpList$positive),
			A2(
				$elm$json$Json$Decode$field,
				'entry',
				A2($author$project$JumpList$bounded, 256, true)),
			A2(
				$elm$json$Json$Decode$field,
				'name',
				A2($author$project$JumpList$bounded, 512, false)),
			A2($elm$json$Json$Decode$field, 'available', $elm$json$Json$Decode$bool),
			A2(
				$elm$json$Json$Decode$field,
				'reason',
				A2($author$project$JumpList$bounded, 128, false)),
			A2(
				$elm$json$Json$Decode$field,
				'actions',
				$elm$json$Json$Decode$list($author$project$JumpList$actionDecoder)))));
var $author$project$Motion$kind = function (expected) {
	return A2(
		$elm$json$Json$Decode$andThen,
		function (v) {
			return _Utils_eq(v, expected) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Motion kind');
		},
		A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string));
};
var $author$project$Motion$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (v) {
		return (!_Utils_eq(v, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(v) : $elm$json$Json$Decode$fail('Motion counter');
	},
	$author$project$UInt64$decoder);
var $author$project$Motion$profileDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (v) {
		switch (v) {
			case 'reduced':
				return $elm$json$Json$Decode$succeed(0);
			case 'full':
				return $elm$json$Json$Decode$succeed(1);
			default:
				return $elm$json$Json$Decode$fail('Motion profile');
		}
	},
	$elm$json$Json$Decode$string);
var $author$project$Motion$strict = F2(
	function (fields, decoder_) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? decoder_ : $elm$json$Json$Decode$fail('Motion fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$Motion$version = A2(
	$elm$json$Json$Decode$andThen,
	function (v) {
		return (v === 3) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Motion version');
	},
	A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int));
var $author$project$Motion$decoder = A2(
	$author$project$Motion$strict,
	_List_fromArray(
		['protocolVersion', 'kind', 'serial', 'profile', 'source']),
	A6(
		$elm$json$Json$Decode$map5,
		F5(
			function (_v0, _v1, serial, profile, source) {
				return {aC: profile, c6: serial, cv: source};
			}),
		$author$project$Motion$version,
		$author$project$Motion$kind('host-motion-preference'),
		A2($elm$json$Json$Decode$field, 'serial', $author$project$Motion$positive),
		A2($elm$json$Json$Decode$field, 'profile', $author$project$Motion$profileDecoder),
		A2(
			$elm$json$Json$Decode$andThen,
			function (v) {
				return A2(
					$elm$core$List$member,
					v,
					_List_fromArray(
						['portal', 'gtk'])) ? $elm$json$Json$Decode$succeed(v) : $elm$json$Json$Decode$fail('Motion source');
			},
			A2($elm$json$Json$Decode$field, 'source', $elm$json$Json$Decode$string))));
var $author$project$MotionPreferences$overrideDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		if (value.$ === 1) {
			return $elm$json$Json$Decode$succeed(0);
		} else {
			switch (value.a) {
				case 'reduced':
					return $elm$json$Json$Decode$succeed(1);
				case 'full':
					return $elm$json$Json$Decode$succeed(2);
				default:
					return $elm$json$Json$Decode$fail('Motion override');
			}
		}
	},
	$elm$json$Json$Decode$nullable($elm$json$Json$Decode$string));
var $author$project$MotionPreferences$strict = F2(
	function (fields, child) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? child : $elm$json$Json$Decode$fail('Motion preference fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$MotionPreferences$decoder = A2(
	$author$project$MotionPreferences$strict,
	_List_fromArray(
		['schema', 'revision', 'override']),
	A4(
		$elm$json$Json$Decode$map3,
		F3(
			function (_v0, revision, override) {
				return {fy: override, c2: revision};
			}),
		A2(
			$elm$json$Json$Decode$andThen,
			function (v) {
				return (v === 1) ? $elm$json$Json$Decode$succeed(0) : $elm$json$Json$Decode$fail('Motion preference version');
			},
			A2($elm$json$Json$Decode$field, 'schema', $elm$json$Json$Decode$int)),
		A2(
			$elm$json$Json$Decode$andThen,
			function (v) {
				return (!_Utils_eq(v, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(v) : $elm$json$Json$Decode$fail('Motion preference revision');
			},
			A2($elm$json$Json$Decode$field, 'revision', $author$project$UInt64$decoder)),
		A2($elm$json$Json$Decode$field, 'override', $author$project$MotionPreferences$overrideDecoder)));
var $author$project$Notifications$Snapshot = F5(
	function (service, revision, available, reason, entries) {
		return {dj: available, af: entries, eH: reason, c2: revision, c7: service};
	});
var $author$project$Notifications$bounded = function (limit) {
	return A2(
		$elm$json$Json$Decode$andThen,
		function (value) {
			return ((_Utils_cmp(
				$elm$core$String$length(value),
				limit) < 1) && (!A2(
				$elm$core$String$any,
				function (c) {
					return ($elm$core$Char$toCode(c) < 32) && ((c !== '\n') && (c !== '\t'));
				},
				value))) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Notification text');
		},
		$elm$json$Json$Decode$string);
};
var $author$project$Notifications$Low = 0;
var $author$project$Notifications$Normal = 1;
var $author$project$Notifications$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (!_Utils_eq(value, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Notification identity');
	},
	$author$project$UInt64$decoder);
var $author$project$Notifications$strict = F2(
	function (fields, child) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? child : $elm$json$Json$Decode$fail('Notification fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$Notifications$unique = function (values) {
	return _Utils_eq(
		$elm$core$List$length(values),
		$elm$core$Set$size(
			$elm$core$Set$fromList(values)));
};
var $author$project$Notifications$entryDecoder = function () {
	var urgency = A2(
		$elm$json$Json$Decode$andThen,
		function (value) {
			switch (value) {
				case 0:
					return $elm$json$Json$Decode$succeed(0);
				case 1:
					return $elm$json$Json$Decode$succeed(1);
				case 2:
					return $elm$json$Json$Decode$succeed(2);
				default:
					return $elm$json$Json$Decode$fail('Notification urgency');
			}
		},
		$elm$json$Json$Decode$int);
	var base = A9(
		$elm$json$Json$Decode$map8,
		F8(
			function (id, incarnation, producer, app, summary, body, state, actions) {
				return {cG: actions, dR: app, dU: body, cl: id, aq: incarnation, ab: producer, dc: state, eS: summary, dg: 1};
			}),
		A2($elm$json$Json$Decode$field, 'id', $author$project$Notifications$positive),
		A2($elm$json$Json$Decode$field, 'incarnation', $author$project$Notifications$positive),
		A2(
			$elm$json$Json$Decode$field,
			'producer',
			A2(
				$elm$json$Json$Decode$andThen,
				function (value) {
					return A2($elm$core$String$startsWith, ':', value) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Notification producer');
				},
				$author$project$Notifications$bounded(128))),
		A2(
			$elm$json$Json$Decode$field,
			'app',
			$author$project$Notifications$bounded(128)),
		A2(
			$elm$json$Json$Decode$field,
			'summary',
			$author$project$Notifications$bounded(256)),
		A2(
			$elm$json$Json$Decode$field,
			'body',
			$author$project$Notifications$bounded(1024)),
		A2(
			$elm$json$Json$Decode$field,
			'state',
			A2(
				$elm$json$Json$Decode$andThen,
				function (value) {
					return A2(
						$elm$core$List$member,
						value,
						_List_fromArray(
							['live', 'expired', 'invoked', 'dismissed', 'closed', 'disconnected', 'unknown', 'unavailable'])) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Notification state');
				},
				$elm$json$Json$Decode$string)),
		A2(
			$elm$json$Json$Decode$field,
			'actions',
			$elm$json$Json$Decode$list(
				A2(
					$author$project$Notifications$strict,
					_List_fromArray(
						['key', 'label']),
					A3(
						$elm$json$Json$Decode$map2,
						F2(
							function (key, label) {
								return {a_: key, el: label};
							}),
						A2(
							$elm$json$Json$Decode$field,
							'key',
							$author$project$Notifications$bounded(64)),
						A2(
							$elm$json$Json$Decode$field,
							'label',
							$author$project$Notifications$bounded(128)))))));
	return A2(
		$elm$json$Json$Decode$andThen,
		function (entry) {
			return (($elm$core$List$length(entry.cG) <= 8) && ($author$project$Notifications$unique(
				A2(
					$elm$core$List$map,
					function ($) {
						return $.a_;
					},
					entry.cG)) && (A2(
				$elm$core$List$all,
				function (a) {
					return (!$elm$core$String$isEmpty(a.a_)) && (!$elm$core$String$isEmpty(a.el));
				},
				entry.cG) && ((entry.dc === 'live') || $elm$core$List$isEmpty(entry.cG))))) ? $elm$json$Json$Decode$succeed(entry) : $elm$json$Json$Decode$fail('Notification action lifecycle');
		},
		$elm$json$Json$Decode$oneOf(
			_List_fromArray(
				[
					A2(
					$author$project$Notifications$strict,
					_List_fromArray(
						['id', 'incarnation', 'producer', 'app', 'summary', 'body', 'state', 'actions', 'urgency']),
					A3(
						$elm$json$Json$Decode$map2,
						F2(
							function (entry, level) {
								return _Utils_update(
									entry,
									{dg: level});
							}),
						base,
						A2($elm$json$Json$Decode$field, 'urgency', urgency))),
					A2(
					$author$project$Notifications$strict,
					_List_fromArray(
						['id', 'incarnation', 'producer', 'app', 'summary', 'body', 'state', 'actions']),
					base)
				])));
}();
var $author$project$Notifications$decoder = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (($elm$core$List$length(value.af) <= 32) && ($author$project$Notifications$unique(
			A2(
				$elm$core$List$map,
				A2(
					$elm$core$Basics$composeR,
					function ($) {
						return $.cl;
					},
					$author$project$UInt64$string),
				value.af)) && $author$project$Notifications$unique(
			A2(
				$elm$core$List$map,
				A2(
					$elm$core$Basics$composeR,
					function ($) {
						return $.aq;
					},
					$author$project$UInt64$string),
				value.af)))) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Notification capacity/identity');
	},
	A2(
		$author$project$Notifications$strict,
		_List_fromArray(
			['service', 'revision', 'available', 'reason', 'entries']),
		A6(
			$elm$json$Json$Decode$map5,
			$author$project$Notifications$Snapshot,
			A2($elm$json$Json$Decode$field, 'service', $author$project$Notifications$positive),
			A2($elm$json$Json$Decode$field, 'revision', $author$project$Notifications$positive),
			A2($elm$json$Json$Decode$field, 'available', $elm$json$Json$Decode$bool),
			A2(
				$elm$json$Json$Decode$field,
				'reason',
				$author$project$Notifications$bounded(256)),
			A2(
				$elm$json$Json$Decode$field,
				'entries',
				$elm$json$Json$Decode$list($author$project$Notifications$entryDecoder)))));
var $author$project$Pins$Snapshot = F2(
	function (revision, identities) {
		return {fl: identities, c2: revision};
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
var $author$project$PointerOwnership$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (v) {
		return _Utils_eq(v, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Pointer counter') : $elm$json$Json$Decode$succeed(v);
	},
	$author$project$UInt64$decoder);
var $author$project$PointerOwnership$Moving = 1;
var $author$project$PointerOwnership$Resizing = 2;
var $author$project$PointerOwnership$stateDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (v) {
		switch (v) {
			case 'idle':
				return $elm$json$Json$Decode$succeed(0);
			case 'move':
				return $elm$json$Json$Decode$succeed(1);
			case 'resize':
				return $elm$json$Json$Decode$succeed(2);
			default:
				return $elm$json$Json$Decode$fail('Pointer state');
		}
	},
	$elm$json$Json$Decode$string);
var $author$project$PointerOwnership$strict = F2(
	function (fields, child) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? child : $elm$json$Json$Decode$fail('Pointer fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$PointerOwnership$decoder = A2(
	$elm$json$Json$Decode$andThen,
	function (r) {
		return ((r.eU !== 3) || ((r.ej !== 'pointer-ownership') || ((r.eE !== 1) || ((!r.c.dc) && (!_Utils_eq(r.c.dD, $elm$core$Maybe$Nothing)))))) ? $elm$json$Json$Decode$fail('Pointer protocol/owner') : $elm$json$Json$Decode$succeed(r.c);
	},
	A2(
		$author$project$PointerOwnership$strict,
		_List_fromArray(
			['protocolVersion', 'kind', 'ownershipProtocol', 'binding', 'requestId', 'serial', 'state', 'owner']),
		A9(
			$elm$json$Json$Decode$map8,
			F8(
				function (version, kind, protocol, binding, request, serial, state, owner) {
					return {
						ej: kind,
						eE: protocol,
						c: {dk: binding, dD: owner, c6: serial, dc: state},
						eU: version
					};
				}),
			A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int),
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			A2($elm$json$Json$Decode$field, 'ownershipProtocol', $elm$json$Json$Decode$int),
			A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
			A2($elm$json$Json$Decode$field, 'requestId', $author$project$PointerOwnership$positive),
			A2($elm$json$Json$Decode$field, 'serial', $author$project$PointerOwnership$positive),
			A2($elm$json$Json$Decode$field, 'state', $author$project$PointerOwnership$stateDecoder),
			A2(
				$elm$json$Json$Decode$field,
				'owner',
				$elm$json$Json$Decode$nullable($author$project$PointerOwnership$positive)))));
var $author$project$Settings$Snapshot = F3(
	function (schema, revision, values) {
		return {c2: revision, fM: schema, bs: values};
	});
var $author$project$Settings$Values = F4(
	function (theme, textScale, effectsOff, reducedTransparency) {
		return {cQ: effectsOff, c$: reducedTransparency, cy: textScale, de: theme};
	});
var $author$project$Settings$scaleDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (scale) {
		return A2(
			$elm$core$List$member,
			scale,
			_List_fromArray(
				[100, 125, 150, 200])) ? $elm$json$Json$Decode$succeed(scale) : $elm$json$Json$Decode$fail('Text scale unavailable');
	},
	$elm$json$Json$Decode$int);
var $author$project$Settings$strict = F2(
	function (fields, child) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? child : $elm$json$Json$Decode$fail('Settings fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$Settings$themeDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		switch (value) {
			case 'night':
				return $elm$json$Json$Decode$succeed(0);
			case 'dawn':
				return $elm$json$Json$Decode$succeed(1);
			case 'high-contrast':
				return $elm$json$Json$Decode$succeed(2);
			default:
				return $elm$json$Json$Decode$fail('Theme unavailable');
		}
	},
	$elm$json$Json$Decode$string);
var $author$project$Settings$currentValues = A2(
	$author$project$Settings$strict,
	_List_fromArray(
		['theme', 'textScale', 'effectsOff', 'reducedTransparency']),
	A5(
		$elm$json$Json$Decode$map4,
		$author$project$Settings$Values,
		A2($elm$json$Json$Decode$field, 'theme', $author$project$Settings$themeDecoder),
		A2($elm$json$Json$Decode$field, 'textScale', $author$project$Settings$scaleDecoder),
		A2($elm$json$Json$Decode$field, 'effectsOff', $elm$json$Json$Decode$bool),
		A2($elm$json$Json$Decode$field, 'reducedTransparency', $elm$json$Json$Decode$bool)));
var $author$project$Settings$legacyValues = A2(
	$author$project$Settings$strict,
	_List_fromArray(
		['theme', 'textScale']),
	A3(
		$elm$json$Json$Decode$map2,
		F2(
			function (theme, scale) {
				return {cQ: false, c$: false, cy: scale, de: theme};
			}),
		A2($elm$json$Json$Decode$field, 'theme', $author$project$Settings$themeDecoder),
		A2($elm$json$Json$Decode$field, 'textScale', $author$project$Settings$scaleDecoder)));
var $author$project$Settings$decoder = A2(
	$author$project$Settings$strict,
	_List_fromArray(
		['schema', 'revision', 'values']),
	A2(
		$elm$json$Json$Decode$andThen,
		function (version) {
			return (!A2(
				$elm$core$List$member,
				version,
				_List_fromArray(
					[1, 2]))) ? $elm$json$Json$Decode$fail('Settings schema unavailable') : A3(
				$elm$json$Json$Decode$map2,
				$author$project$Settings$Snapshot(2),
				A2(
					$elm$json$Json$Decode$field,
					'revision',
					A2(
						$elm$json$Json$Decode$andThen,
						function (revision) {
							return (!_Utils_eq(revision, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(revision) : $elm$json$Json$Decode$fail('Settings revision');
						},
						$author$project$UInt64$decoder)),
				A2(
					$elm$json$Json$Decode$field,
					'values',
					(version === 1) ? $author$project$Settings$legacyValues : $author$project$Settings$currentValues));
		},
		A2($elm$json$Json$Decode$field, 'schema', $elm$json$Json$Decode$int)));
var $author$project$ShortcutPreferences$Snapshot = F3(
	function (schema, revision, choices) {
		return {ae: choices, c2: revision, fM: schema};
	});
var $author$project$ShortcutPreferences$Choices = F3(
	function (applications, system, notifications) {
		return {aD: applications, C: notifications, bP: system};
	});
var $author$project$ShortcutPreferences$choiceDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		switch (value) {
			case 'undecided':
				return $elm$json$Json$Decode$succeed(0);
			case 'keep':
				return $elm$json$Json$Decode$succeed(1);
			case 'default':
				return $elm$json$Json$Decode$succeed(2);
			case 'alternate':
				return $elm$json$Json$Decode$succeed(3);
			default:
				return $elm$json$Json$Decode$fail('Shortcut decision');
		}
	},
	$elm$json$Json$Decode$string);
var $author$project$ShortcutPreferences$strict = F2(
	function (fields, child) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? child : $elm$json$Json$Decode$fail('Shortcut fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$ShortcutPreferences$choicesDecoder = A2(
	$author$project$ShortcutPreferences$strict,
	_List_fromArray(
		['applications', 'system', 'notifications']),
	A4(
		$elm$json$Json$Decode$map3,
		$author$project$ShortcutPreferences$Choices,
		A2($elm$json$Json$Decode$field, 'applications', $author$project$ShortcutPreferences$choiceDecoder),
		A2($elm$json$Json$Decode$field, 'system', $author$project$ShortcutPreferences$choiceDecoder),
		A2($elm$json$Json$Decode$field, 'notifications', $author$project$ShortcutPreferences$choiceDecoder)));
var $author$project$ShortcutPreferences$decoder = A2(
	$author$project$ShortcutPreferences$strict,
	_List_fromArray(
		['schema', 'revision', 'choices']),
	A4(
		$elm$json$Json$Decode$map3,
		$author$project$ShortcutPreferences$Snapshot,
		A2(
			$elm$json$Json$Decode$field,
			'schema',
			A2(
				$elm$json$Json$Decode$andThen,
				function (v) {
					return (v === 1) ? $elm$json$Json$Decode$succeed(v) : $elm$json$Json$Decode$fail('Shortcut schema');
				},
				$elm$json$Json$Decode$int)),
		A2(
			$elm$json$Json$Decode$field,
			'revision',
			A2(
				$elm$json$Json$Decode$andThen,
				function (v) {
					return (!_Utils_eq(v, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(v) : $elm$json$Json$Decode$fail('Shortcut revision');
				},
				$author$project$UInt64$decoder)),
		A2($elm$json$Json$Decode$field, 'choices', $author$project$ShortcutPreferences$choicesDecoder)));
var $author$project$Shortcuts$Event = F3(
	function (serial, route, outputGeneration) {
		return {fw: outputGeneration, eM: route, c6: serial};
	});
var $author$project$Shortcuts$boxDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (box) {
		if ((((box.b && box.b.b) && box.b.b.b) && box.b.b.b.b) && (!box.b.b.b.b.b)) {
			var x = box.a;
			var _v1 = box.b;
			var y = _v1.a;
			var _v2 = _v1.b;
			var width = _v2.a;
			var _v3 = _v2.b;
			var height = _v3.a;
			return ((width > 0) && ((height > 0) && A2(
				$elm$core$List$all,
				function (v) {
					return (_Utils_cmp(v, -2147483648) > -1) && (v <= 2147483647);
				},
				box))) ? $elm$json$Json$Decode$succeed(box) : $elm$json$Json$Decode$fail('Shortcut output bounds');
		} else {
			return $elm$json$Json$Decode$fail('Shortcut output shape');
		}
	},
	$elm$json$Json$Decode$list($elm$json$Json$Decode$int));
var $author$project$Shortcuts$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (v) {
		return _Utils_eq(v, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Shortcut serial') : $elm$json$Json$Decode$succeed(v);
	},
	$author$project$UInt64$decoder);
var $author$project$Shortcuts$Applications = 0;
var $author$project$Shortcuts$Notifications = 2;
var $author$project$Shortcuts$System = 1;
var $author$project$Shortcuts$routeDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (v) {
		switch (v) {
			case 'applications':
				return $elm$json$Json$Decode$succeed(0);
			case 'system':
				return $elm$json$Json$Decode$succeed(1);
			case 'notifications':
				return $elm$json$Json$Decode$succeed(2);
			default:
				return $elm$json$Json$Decode$fail('Unsupported shell shortcut');
		}
	},
	$elm$json$Json$Decode$string);
var $author$project$Shortcuts$strict = F2(
	function (fields, child) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? child : $elm$json$Json$Decode$fail('Shortcut fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$Shortcuts$eventDecoder = function (protocol) {
	return (protocol === 1) ? A2(
		$author$project$Shortcuts$strict,
		_List_fromArray(
			['serial', 'route']),
		A3(
			$elm$json$Json$Decode$map2,
			F2(
				function (serial, route) {
					return A3($author$project$Shortcuts$Event, serial, route, $elm$core$Maybe$Nothing);
				}),
			A2($elm$json$Json$Decode$field, 'serial', $author$project$Shortcuts$positive),
			A2($elm$json$Json$Decode$field, 'route', $author$project$Shortcuts$routeDecoder))) : ((protocol === 2) ? A2(
		$author$project$Shortcuts$strict,
		_List_fromArray(
			['serial', 'route', 'output']),
		A4(
			$elm$json$Json$Decode$map3,
			F3(
				function (serial, route, _v0) {
					return A3($author$project$Shortcuts$Event, serial, route, $elm$core$Maybe$Nothing);
				}),
			A2($elm$json$Json$Decode$field, 'serial', $author$project$Shortcuts$positive),
			A2($elm$json$Json$Decode$field, 'route', $author$project$Shortcuts$routeDecoder),
			A2(
				$elm$json$Json$Decode$field,
				'output',
				$elm$json$Json$Decode$nullable($author$project$Shortcuts$boxDecoder)))) : A2(
		$author$project$Shortcuts$strict,
		_List_fromArray(
			['serial', 'route', 'output', 'outputGeneration']),
		A5(
			$elm$json$Json$Decode$map4,
			F4(
				function (serial, route, _v1, generation) {
					return A3(
						$author$project$Shortcuts$Event,
						serial,
						route,
						$elm$core$Maybe$Just(generation));
				}),
			A2($elm$json$Json$Decode$field, 'serial', $author$project$Shortcuts$positive),
			A2($elm$json$Json$Decode$field, 'route', $author$project$Shortcuts$routeDecoder),
			A2(
				$elm$json$Json$Decode$field,
				'output',
				$elm$json$Json$Decode$nullable($author$project$Shortcuts$boxDecoder)),
			A2($elm$json$Json$Decode$field, 'outputGeneration', $author$project$Shortcuts$positive))));
};
var $author$project$Shortcuts$decoder = A2(
	$elm$json$Json$Decode$andThen,
	function (eventProtocol) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (receipt) {
				var snapshot = receipt.c;
				var ordered = function (rows) {
					if (!rows.b) {
						return true;
					} else {
						if (!rows.b.b) {
							return true;
						} else {
							var a = rows.a;
							var _v1 = rows.b;
							var b = _v1.a;
							var rest = _v1.b;
							return _Utils_eq(
								$author$project$UInt64$next(a.c6),
								$elm$core$Maybe$Just(b.c6)) && ordered(
								A2($elm$core$List$cons, b, rest));
						}
					}
				};
				var last = A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.c6;
					},
					$elm$core$List$head(
						$elm$core$List$reverse(snapshot.by)));
				return ((receipt.eU !== 3) || ((receipt.ej !== 'shell-shortcuts') || ((!A2(
					$elm$core$List$member,
					receipt.eE,
					_List_fromArray(
						[1, 2, 3]))) || (($elm$core$List$length(snapshot.by) > 64) || ((!ordered(snapshot.by)) || ((!_Utils_eq(last, $elm$core$Maybe$Nothing)) && (!_Utils_eq(
					last,
					$elm$core$Maybe$Just(snapshot.c6))))))))) ? $elm$json$Json$Decode$fail('Shortcut protocol/order') : $elm$json$Json$Decode$succeed(snapshot);
			},
			A2(
				$author$project$Shortcuts$strict,
				_List_fromArray(
					['protocolVersion', 'kind', 'shortcutProtocol', 'binding', 'requestId', 'serial', 'blocked', 'events']),
				A9(
					$elm$json$Json$Decode$map8,
					F8(
						function (version, kind, protocol, binding, request, serial, blocked, events) {
							return {
								ej: kind,
								eE: protocol,
								c: {dk: binding, e6: blocked, by: events, c6: serial},
								eU: version
							};
						}),
					A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int),
					A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
					A2($elm$json$Json$Decode$field, 'shortcutProtocol', $elm$json$Json$Decode$int),
					A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
					A2($elm$json$Json$Decode$field, 'requestId', $author$project$Shortcuts$positive),
					A2($elm$json$Json$Decode$field, 'serial', $author$project$UInt64$decoder),
					A2($elm$json$Json$Decode$field, 'blocked', $elm$json$Json$Decode$bool),
					A2(
						$elm$json$Json$Decode$field,
						'events',
						$elm$json$Json$Decode$list(
							$author$project$Shortcuts$eventDecoder(eventProtocol))))));
	},
	A2($elm$json$Json$Decode$field, 'shortcutProtocol', $elm$json$Json$Decode$int));
var $author$project$SystemMenu$Snapshot = F6(
	function (service, revision, volume, network, power, session) {
		return {fs: network, fE: power, c2: revision, c7: service, fO: session, fV: volume};
	});
var $author$project$SystemMenu$bounded = function (limit) {
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
				value))) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('System text');
		},
		$elm$json$Json$Decode$string);
};
var $author$project$SystemMenu$option = function (values) {
	return A2(
		$elm$json$Json$Decode$andThen,
		function (value) {
			return A2($elm$core$List$member, value, values) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Native capability');
		},
		$elm$json$Json$Decode$string);
};
var $author$project$SystemMenu$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return _Utils_eq(value, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('System identity') : $elm$json$Json$Decode$succeed(value);
	},
	$author$project$UInt64$decoder);
var $author$project$SystemMenu$strict = F2(
	function (fields, child) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? child : $elm$json$Json$Decode$fail('System fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$SystemMenu$decoder = A2(
	$author$project$SystemMenu$strict,
	_List_fromArray(
		['service', 'revision', 'volume', 'network', 'power', 'session']),
	A7(
		$elm$json$Json$Decode$map6,
		$author$project$SystemMenu$Snapshot,
		A2($elm$json$Json$Decode$field, 'service', $author$project$SystemMenu$positive),
		A2($elm$json$Json$Decode$field, 'revision', $author$project$SystemMenu$positive),
		A2(
			$elm$json$Json$Decode$field,
			'volume',
			$elm$json$Json$Decode$nullable(
				A2(
					$author$project$SystemMenu$strict,
					_List_fromArray(
						['percent', 'muted', 'label']),
					A4(
						$elm$json$Json$Decode$map3,
						F3(
							function (percent, muted, label) {
								return {el: label, dz: muted, fz: percent};
							}),
						A2(
							$elm$json$Json$Decode$field,
							'percent',
							A2(
								$elm$json$Json$Decode$andThen,
								function (value) {
									return ((value >= 0) && (value <= 1600)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Native volume');
								},
								$elm$json$Json$Decode$int)),
						A2($elm$json$Json$Decode$field, 'muted', $elm$json$Json$Decode$bool),
						A2(
							$elm$json$Json$Decode$field,
							'label',
							$author$project$SystemMenu$bounded(128)))))),
		A2(
			$elm$json$Json$Decode$field,
			'network',
			$elm$json$Json$Decode$nullable(
				A2(
					$author$project$SystemMenu$strict,
					_List_fromArray(
						['enabled', 'state', 'permission']),
					A4(
						$elm$json$Json$Decode$map3,
						F3(
							function (enabled, state, permission) {
								return {fd: enabled, fA: permission, dc: state};
							}),
						A2($elm$json$Json$Decode$field, 'enabled', $elm$json$Json$Decode$bool),
						A2(
							$elm$json$Json$Decode$field,
							'state',
							$author$project$SystemMenu$bounded(32)),
						A2(
							$elm$json$Json$Decode$field,
							'permission',
							$author$project$SystemMenu$option(
								_List_fromArray(
									['yes', 'no', 'auth']))))))),
		A2(
			$elm$json$Json$Decode$field,
			'power',
			$elm$json$Json$Decode$nullable(
				A2(
					$author$project$SystemMenu$strict,
					_List_fromArray(
						['suspend', 'reboot', 'poweroff']),
					A4(
						$elm$json$Json$Decode$map3,
						F3(
							function (suspend, reboot, poweroff) {
								return {fF: poweroff, fH: reboot, fQ: suspend};
							}),
						A2(
							$elm$json$Json$Decode$field,
							'suspend',
							$author$project$SystemMenu$option(
								_List_fromArray(
									['yes', 'no', 'na', 'challenge']))),
						A2(
							$elm$json$Json$Decode$field,
							'reboot',
							$author$project$SystemMenu$option(
								_List_fromArray(
									['yes', 'no', 'na', 'challenge']))),
						A2(
							$elm$json$Json$Decode$field,
							'poweroff',
							$author$project$SystemMenu$option(
								_List_fromArray(
									['yes', 'no', 'na', 'challenge']))))))),
		A2(
			$elm$json$Json$Decode$field,
			'session',
			$elm$json$Json$Decode$nullable(
				A2(
					$author$project$SystemMenu$strict,
					_List_fromArray(
						['name', 'state', 'locked']),
					A4(
						$elm$json$Json$Decode$map3,
						F3(
							function (ownerName, state, locked) {
								return {fq: locked, dA: ownerName, dc: state};
							}),
						A2(
							$elm$json$Json$Decode$field,
							'name',
							$author$project$SystemMenu$bounded(128)),
						A2(
							$elm$json$Json$Decode$field,
							'state',
							$author$project$SystemMenu$bounded(32)),
						A2($elm$json$Json$Decode$field, 'locked', $elm$json$Json$Decode$bool)))))));
var $author$project$Files$edit = F2(
	function (value, model) {
		return $author$project$Files$textValid(value) ? _Utils_update(
			model,
			{fb: value}) : model;
	});
var $author$project$MotionPreferences$edit = F2(
	function (override, model) {
		return $author$project$MotionPreferences$writable(model) ? _Utils_update(
			model,
			{fb: override, ft: 'Unsaved motion preference. Save to apply.'}) : model;
	});
var $author$project$Settings$edit = F2(
	function (values, model) {
		return ((!$author$project$Settings$writable(model)) || (!A2(
			$elm$core$List$member,
			values.cy,
			_List_fromArray(
				[100, 125, 150, 200])))) ? model : _Utils_update(
			model,
			{fb: values, ft: 'Unsaved changes. Save to apply.'});
	});
var $author$project$ShortcutPreferences$edit = F3(
	function (route, selected, model) {
		if ((!$author$project$ShortcutPreferences$writable(model)) || ((!A2(
			$elm$core$List$member,
			route,
			_List_fromArray(
				['applications', 'system', 'notifications']))) || (!A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				A2(
					$elm$core$Basics$composeR,
					$author$project$ShortcutPreferences$row(route),
					$author$project$ShortcutPreferences$allowed(selected)),
				model.cV))))) {
			return model;
		} else {
			var draft = model.fb;
			var next = function () {
				switch (route) {
					case 'applications':
						return _Utils_update(
							draft,
							{aD: selected});
					case 'system':
						return _Utils_update(
							draft,
							{bP: selected});
					default:
						return _Utils_update(
							draft,
							{C: selected});
				}
			}();
			return _Utils_update(
				model,
				{fb: next, ft: 'Unsaved shortcut choices. Existing bindings remain unchanged until you save.'});
		}
	});
var $author$project$AdapterNotice$failedRead = F7(
	function (source, binding, request, service, revision, unavailable, prior) {
		return unavailable ? $elm$core$Maybe$Just(
			{dk: binding, c1: request, c2: revision, c7: service, cv: source}) : prior;
	});
var $author$project$Notifications$focus = F2(
	function (selected, model) {
		if (_Utils_eq(
			$author$project$Notifications$focusedIdentity(model),
			$elm$core$Maybe$Just(selected))) {
			return model;
		} else {
			var chosen = A2(
				$elm$core$Maybe$andThen,
				function (snapshot) {
					return $elm$core$List$head(
						A2(
							$elm$core$List$filter,
							function (row) {
								return _Utils_eq(
									$author$project$Notifications$identity(row.fR),
									selected);
							},
							A2(
								$elm$core$List$concatMap,
								function (entry) {
									return _Utils_ap(
										A2(
											$elm$core$List$map,
											function (action) {
												return {
													el: action.el,
													fR: A4($author$project$Notifications$target, snapshot, entry, 'invoke', action.a_)
												};
											},
											entry.cG),
										_List_fromArray(
											[
												{
												el: 'Dismiss notification',
												fR: A4($author$project$Notifications$target, snapshot, entry, 'dismiss', '')
											}
											]));
								},
								A2(
									$elm$core$List$filter,
									function (entry) {
										return entry.dc === 'live';
									},
									snapshot.af))));
				},
				model.c);
			return _Utils_update(
				model,
				{ci: chosen});
		}
	});
var $author$project$Desktop$gestureAction = function (message) {
	_v0$11:
	while (true) {
		switch (message.$) {
			case 11:
				return false;
			case 9:
				return false;
			case 8:
				return false;
			case 10:
				return false;
			case 7:
				return false;
			case 66:
				return false;
			case 67:
				return false;
			case 32:
				return false;
			case 64:
				return false;
			case 69:
				return false;
			case 1:
				if (!message.a.$) {
					return false;
				} else {
					break _v0$11;
				}
			default:
				break _v0$11;
		}
	}
	return true;
};
var $author$project$ShortcutPreferences$Inventory = F4(
	function (fingerprint, applications, system, notifications) {
		return {aD: applications, d5: fingerprint, C: notifications, bP: system};
	});
var $author$project$ShortcutPreferences$Row = F5(
	function (defaultChord, alternateChord, defaultAvailable, alternateAvailable, active) {
		return {bt: active, dh: alternateAvailable, e4: alternateChord, dp: defaultAvailable, e9: defaultChord};
	});
var $author$project$ShortcutPreferences$rowDecoder = F2(
	function (defaultChord, alternateChord) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (value) {
				return (((value.bt === 2) && (!value.dp)) || ((value.bt === 3) && (!value.dh))) ? $elm$json$Json$Decode$fail('Active shortcut conflicts') : $elm$json$Json$Decode$succeed(value);
			},
			A2(
				$author$project$ShortcutPreferences$strict,
				_List_fromArray(
					['defaultChord', 'alternateChord', 'defaultAvailable', 'alternateAvailable', 'active']),
				A6(
					$elm$json$Json$Decode$map5,
					$author$project$ShortcutPreferences$Row,
					A2(
						$elm$json$Json$Decode$field,
						'defaultChord',
						A2(
							$elm$json$Json$Decode$andThen,
							function (v) {
								return _Utils_eq(v, defaultChord) ? $elm$json$Json$Decode$succeed(v) : $elm$json$Json$Decode$fail('Default chord');
							},
							$elm$json$Json$Decode$string)),
					A2(
						$elm$json$Json$Decode$field,
						'alternateChord',
						A2(
							$elm$json$Json$Decode$andThen,
							function (v) {
								return _Utils_eq(v, alternateChord) ? $elm$json$Json$Decode$succeed(v) : $elm$json$Json$Decode$fail('Alternate chord');
							},
							$elm$json$Json$Decode$string)),
					A2($elm$json$Json$Decode$field, 'defaultAvailable', $elm$json$Json$Decode$bool),
					A2($elm$json$Json$Decode$field, 'alternateAvailable', $elm$json$Json$Decode$bool),
					A2(
						$elm$json$Json$Decode$field,
						'active',
						A2(
							$elm$json$Json$Decode$andThen,
							function (v) {
								return A2(
									$elm$core$List$member,
									v,
									_List_fromArray(
										[1, 2, 3])) ? $elm$json$Json$Decode$succeed(v) : $elm$json$Json$Decode$fail('Observed shortcut');
							},
							$author$project$ShortcutPreferences$choiceDecoder)))));
	});
var $author$project$ShortcutPreferences$inventoryDecoder = A2(
	$author$project$ShortcutPreferences$strict,
	_List_fromArray(
		['fingerprint', 'applications', 'system', 'notifications']),
	A5(
		$elm$json$Json$Decode$map4,
		$author$project$ShortcutPreferences$Inventory,
		A2(
			$elm$json$Json$Decode$field,
			'fingerprint',
			A2(
				$elm$json$Json$Decode$andThen,
				function (v) {
					return (($elm$core$String$length(v) === 64) && A2(
						$elm$core$String$all,
						function (c) {
							return A2(
								$elm$core$String$contains,
								$elm$core$String$fromChar(c),
								'0123456789abcdef');
						},
						v)) ? $elm$json$Json$Decode$succeed(v) : $elm$json$Json$Decode$fail('Binding fingerprint');
				},
				$elm$json$Json$Decode$string)),
		A2(
			$elm$json$Json$Decode$field,
			'applications',
			A2($author$project$ShortcutPreferences$rowDecoder, 'SUPER + ALT + SPACE', 'SUPER + CTRL + ALT + SPACE')),
		A2(
			$elm$json$Json$Decode$field,
			'system',
			A2($author$project$ShortcutPreferences$rowDecoder, 'SUPER + ESCAPE', 'SUPER + CTRL + ESCAPE')),
		A2(
			$elm$json$Json$Decode$field,
			'notifications',
			A2($author$project$ShortcutPreferences$rowDecoder, 'SUPER + SHIFT + ALT + comma', 'SUPER + CTRL + ALT + comma'))));
var $author$project$Switcher$lastStep = function (_v0) {
	var model = _v0;
	return $author$project$Switcher$lastOrdinal(model);
};
var $author$project$Desktop$motionGesture = function (message) {
	switch (message.$) {
		case 36:
			return false;
		case 37:
			return false;
		case 42:
			return false;
		case 43:
			return false;
		case 47:
			return false;
		case 44:
			return false;
		case 45:
			return false;
		case 46:
			return false;
		default:
			return $author$project$Desktop$gestureAction(message);
	}
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
		return {cH: cancelled, cL: consumed, fh: generation, ck: history, cY: origin, c0: released, aP: roots, bO: steps};
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
				_Utils_eq(chord.fh, $author$project$UInt64$zero),
				$elm$core$List$isEmpty(chord.bO)) && A2(
				$elm$core$List$all,
				function (root) {
					return A2($elm$core$List$member, root, chord.aP);
				},
				chord.ck)) ? $elm$json$Json$Decode$succeed(chord) : $elm$json$Json$Decode$fail('Chord entry/history');
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
		if ((model.j !== 2) || ((!_Utils_eq(model.c0, $elm$core$Maybe$Nothing)) || $elm$core$List$isEmpty(model.af))) {
			return original;
		} else {
			var position = A2(
				$elm$core$Basics$modBy,
				$elm$core$List$length(model.af),
				model.fN + $author$project$Switcher$delta(direction));
			var root = A2(
				$elm$core$Maybe$withDefault,
				$author$project$UInt64$zero,
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.r;
					},
					$elm$core$List$head(
						A2($elm$core$List$drop, position, model.af))));
			return _Utils_update(
				model,
				{
					ba: $elm$core$Maybe$Just(
						{
							r: root,
							df: $author$project$Switcher$lastOrdinal(model)
						}),
					fN: position
				});
		}
	});
var $author$project$Motion$observe = F2(
	function (observation, model) {
		return A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (old) {
					return A2($author$project$UInt64$compare, observation.c6, old.c6) !== 2;
				},
				model.bF)) ? model : _Utils_update(
			model,
			{
				bF: $elm$core$Maybe$Just(observation)
			});
	});
var $author$project$MotionPreferences$observe = F2(
	function (snapshot, model) {
		if (snapshot.$ === 1) {
			return _Utils_update(
				model,
				{ft: 'Stored motion preference unavailable. Refresh to read it again; the stored copy is preserved.', c: $elm$core$Maybe$Nothing});
		} else {
			var current = snapshot.a;
			return A2(
				$elm$core$Maybe$withDefault,
				false,
				A2(
					$elm$core$Maybe$map,
					function (old) {
						return (!A2($author$project$UInt64$compare, current.c2, old.c2)) || (_Utils_eq(current.c2, old.c2) && (!_Utils_eq(current.fy, old.fy)));
					},
					model.c)) ? model : _Utils_update(
				model,
				{
					fb: current.fy,
					ft: 'Motion preference loaded.',
					ex: $elm$core$Maybe$Nothing,
					c: $elm$core$Maybe$Just(current)
				});
		}
	});
var $author$project$Notifications$observe = F2(
	function (current, model) {
		var pending = A2(
			$elm$core$Maybe$map,
			function (waiting) {
				return _Utils_update(
					waiting,
					{
						bV: waiting.bV || A2(
							$elm$core$List$any,
							function (entry) {
								return A3($author$project$Notifications$same, waiting.fR, current.c7, entry) && (entry.dc === 'expired');
							},
							current.af)
					});
			},
			model.ex);
		var entries = A2(
			$elm$core$List$filter,
			function (row) {
				return row.dc === 'live';
			},
			current.af);
		var count = $elm$core$List$length(entries);
		var notice = (!current.dj) ? current.eH : ((!count) ? 'No live notifications. Previous notifications remain in history.' : ($elm$core$String$fromInt(count) + ' live notifications. Actions apply only to the current notification.'));
		var admitted = function () {
			var _v0 = model.c;
			if (_v0.$ === 1) {
				return true;
			} else {
				var old = _v0.a;
				return _Utils_eq(current.c7, old.c7) && ((A2($author$project$UInt64$compare, current.c2, old.c2) === 2) || _Utils_eq(current, old));
			}
		}();
		return (!admitted) ? model : _Utils_update(
			model,
			{
				ft: (!_Utils_eq(model.ex, $elm$core$Maybe$Nothing)) ? model.ft : notice,
				ex: pending,
				c: $elm$core$Maybe$Just(current)
			});
	});
var $author$project$Pins$observe = F2(
	function (snapshot, model) {
		if (snapshot.$ === 1) {
			return _Utils_update(
				model,
				{ft: 'Pin storage unavailable. Refresh applications to try again.', ex: $elm$core$Maybe$Nothing, c: $elm$core$Maybe$Nothing});
		} else {
			var value = snapshot.a;
			return A2(
				$elm$core$Maybe$withDefault,
				false,
				A2(
					$elm$core$Maybe$map,
					function (old) {
						return !A2($author$project$UInt64$compare, value.c2, old.c2);
					},
					model.c)) ? model : _Utils_update(
				model,
				{
					ft: '',
					ex: $elm$core$Maybe$Nothing,
					c: $elm$core$Maybe$Just(value)
				});
		}
	});
var $author$project$Settings$observe = F2(
	function (snapshot, model) {
		if (snapshot.$ === 1) {
			return _Utils_update(
				model,
				{ft: 'Settings unavailable or from an unsupported version. Refresh to read them again; the stored copy is preserved.', ex: $elm$core$Maybe$Nothing, c: $elm$core$Maybe$Nothing});
		} else {
			var current = snapshot.a;
			return A2(
				$elm$core$Maybe$withDefault,
				false,
				A2(
					$elm$core$Maybe$map,
					function (old) {
						return !A2($author$project$UInt64$compare, current.c2, old.c2);
					},
					model.c)) ? model : _Utils_update(
				model,
				{
					fb: current.bs,
					ft: 'Settings loaded.',
					ex: $elm$core$Maybe$Nothing,
					c: $elm$core$Maybe$Just(current)
				});
		}
	});
var $author$project$ShortcutPreferences$observe = F3(
	function (snapshot, inventory, model) {
		var _v0 = _Utils_Tuple2(snapshot, inventory);
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var current = _v0.a.a;
			var _native = _v0.b.a;
			return A2(
				$elm$core$Maybe$withDefault,
				false,
				A2(
					$elm$core$Maybe$map,
					function (old) {
						return !A2($author$project$UInt64$compare, current.c2, old.c2);
					},
					model.c)) ? model : _Utils_update(
				model,
				{
					fb: current.ae,
					cV: $elm$core$Maybe$Just(_native),
					ft: 'Shortcut choices loaded. Conflicting bindings are preserved; choose a free chord or keep the existing shortcut.',
					ex: $elm$core$Maybe$Nothing,
					c: $elm$core$Maybe$Just(current)
				});
		} else {
			return _Utils_update(
				model,
				{cV: $elm$core$Maybe$Nothing, ft: 'Shortcut choices unavailable. Stored choices are preserved. Refresh to read again.', ex: $elm$core$Maybe$Nothing, c: $elm$core$Maybe$Nothing});
		}
	});
var $author$project$JumpList$propose = F3(
	function (request, value, model) {
		return (_Utils_eq(request, $author$project$UInt64$zero) || (!A2($author$project$JumpList$supported, value, model))) ? _Utils_Tuple2(model, $elm$core$Maybe$Nothing) : _Utils_Tuple2(
			_Utils_update(
				model,
				{
					ft: 'Application action: waiting for native submission…',
					ex: $elm$core$Maybe$Just(
						{aa: value, c1: request}),
					ca: A2(
						$elm$core$List$take,
						128,
						A2($elm$core$List$cons, value, model.ca))
				}),
			$elm$core$Maybe$Just(
				$elm$json$Json$Encode$object(
					_List_fromArray(
						[
							_Utils_Tuple2(
							'service',
							$elm$json$Json$Encode$string(
								$author$project$UInt64$string(value.c7))),
							_Utils_Tuple2(
							'revision',
							$elm$json$Json$Encode$string(
								$author$project$UInt64$string(value.c2))),
							_Utils_Tuple2(
							'entry',
							$elm$json$Json$Encode$string(value.d2)),
							_Utils_Tuple2(
							'action',
							$elm$json$Json$Encode$string(value.e3))
						]))));
	});
var $author$project$MotionPreferences$encode = function (snapshot) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'schema',
				$elm$json$Json$Encode$int(1)),
				_Utils_Tuple2(
				'revision',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(snapshot.c2))),
				_Utils_Tuple2(
				'override',
				function () {
					var _v0 = snapshot.fy;
					switch (_v0) {
						case 0:
							return $elm$json$Json$Encode$null;
						case 1:
							return $elm$json$Json$Encode$string('reduced');
						default:
							return $elm$json$Json$Encode$string('full');
					}
				}())
			]));
};
var $author$project$MotionPreferences$propose = F2(
	function (request, model) {
		var _v0 = model.c;
		if (_v0.$ === 1) {
			return _Utils_Tuple2(model, $elm$core$Maybe$Nothing);
		} else {
			var current = _v0.a;
			return (_Utils_eq(request, $author$project$UInt64$zero) || ((!$author$project$MotionPreferences$writable(model)) || _Utils_eq(current.fy, model.fb))) ? _Utils_Tuple2(model, $elm$core$Maybe$Nothing) : _Utils_Tuple2(
				_Utils_update(
					model,
					{
						ft: 'Saving motion preference…',
						ex: $elm$core$Maybe$Just(
							{fy: model.fb, c1: request, c2: current.c2})
					}),
				$elm$core$Maybe$Just(
					$author$project$MotionPreferences$encode(
						_Utils_update(
							current,
							{fy: model.fb}))));
		}
	});
var $author$project$Notifications$propose = F3(
	function (request, choice, model) {
		return ((!_Utils_eq(model.ex, $elm$core$Maybe$Nothing)) || (!A2($author$project$Notifications$live, choice, model))) ? _Utils_Tuple2(model, $elm$core$Maybe$Nothing) : _Utils_Tuple2(
			_Utils_update(
				model,
				{
					ft: 'Sending notification action…',
					ex: $elm$core$Maybe$Just(
						{bV: false, c1: request, fR: choice}),
					ca: A2(
						$elm$core$List$take,
						64,
						A2($elm$core$List$cons, choice, model.ca))
				}),
			$elm$core$Maybe$Just(
				$author$project$Notifications$encodeIntent(choice)));
	});
var $author$project$Settings$encode = function (snapshot) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'schema',
				$elm$json$Json$Encode$int(snapshot.fM)),
				_Utils_Tuple2(
				'revision',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(snapshot.c2))),
				_Utils_Tuple2(
				'values',
				$author$project$Settings$encodeValues(snapshot.bs))
			]));
};
var $author$project$Settings$propose = F2(
	function (request, model) {
		var _v0 = model.c;
		if (!_v0.$) {
			var current = _v0.a;
			return ((!$author$project$Settings$writable(model)) || _Utils_eq(current.bs, model.fb)) ? _Utils_Tuple2(model, $elm$core$Maybe$Nothing) : _Utils_Tuple2(
				_Utils_update(
					model,
					{
						ft: 'Saving settings…',
						cZ: $elm$core$Maybe$Nothing,
						ex: $elm$core$Maybe$Just(
							{c1: request, bs: model.fb})
					}),
				$elm$core$Maybe$Just(
					$author$project$Settings$encode(
						_Utils_update(
							current,
							{bs: model.fb}))));
		} else {
			return _Utils_Tuple2(model, $elm$core$Maybe$Nothing);
		}
	});
var $author$project$ShortcutPreferences$encode = function (snapshot) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'schema',
				$elm$json$Json$Encode$int(1)),
				_Utils_Tuple2(
				'revision',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(snapshot.c2))),
				_Utils_Tuple2(
				'choices',
				$elm$json$Json$Encode$object(
					_List_fromArray(
						[
							_Utils_Tuple2(
							'applications',
							$elm$json$Json$Encode$string(
								$author$project$ShortcutPreferences$name(snapshot.ae.aD))),
							_Utils_Tuple2(
							'system',
							$elm$json$Json$Encode$string(
								$author$project$ShortcutPreferences$name(snapshot.ae.bP))),
							_Utils_Tuple2(
							'notifications',
							$elm$json$Json$Encode$string(
								$author$project$ShortcutPreferences$name(snapshot.ae.C)))
						])))
			]));
};
var $author$project$ShortcutPreferences$propose = F2(
	function (request, model) {
		var _v0 = _Utils_Tuple2(model.c, model.cV);
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var current = _v0.a.a;
			var _native = _v0.b.a;
			return (!($author$project$ShortcutPreferences$ready(model) && $author$project$ShortcutPreferences$changed(model))) ? _Utils_Tuple2(model, $elm$core$Maybe$Nothing) : _Utils_Tuple2(
				_Utils_update(
					model,
					{
						ft: 'Saving and applying shortcut choices…',
						ex: $elm$core$Maybe$Just(
							{ae: model.fb, c1: request})
					}),
				$elm$core$Maybe$Just(
					$elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'preferences',
								$author$project$ShortcutPreferences$encode(
									_Utils_update(
										current,
										{ae: model.fb}))),
								_Utils_Tuple2(
								'fingerprint',
								$elm$json$Json$Encode$string(_native.d5))
							]))));
		} else {
			return _Utils_Tuple2(model, $elm$core$Maybe$Nothing);
		}
	});
var $author$project$Desktop$readFiles = function (model) {
	if (!_Utils_eq(model.aW, $elm$core$Maybe$Nothing)) {
		return _Utils_Tuple2(model, _List_Nil);
	} else {
		var _v0 = _Utils_Tuple2(
			model.a.b.dk,
			$author$project$UInt64$next(model.c1));
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var binding = _v0.a.a;
			var request = _v0.b.a;
			return _Utils_Tuple2(
				$author$project$Desktop$advance(
					_Utils_update(
						model,
						{
							aW: $elm$core$Maybe$Just(request),
							c1: request
						})),
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
									$elm$json$Json$Encode$string('files-request')),
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
			return _Utils_Tuple2(model, _List_Nil);
		}
	}
};
var $author$project$Desktop$readJumpList = function (model) {
	if (!_Utils_eq(model.aZ, $elm$core$Maybe$Nothing)) {
		return _Utils_Tuple2(model, _List_Nil);
	} else {
		var _v0 = _Utils_Tuple3(
			model.a.b.dk,
			$author$project$UInt64$next(model.c1),
			model.o);
		if (((!_v0.a.$) && (!_v0.b.$)) && (!_v0.c.$)) {
			var binding = _v0.a.a;
			var request = _v0.b.a;
			var entry = _v0.c.a;
			return _Utils_Tuple2(
				$author$project$Desktop$advance(
					_Utils_update(
						model,
						{
							aZ: $elm$core$Maybe$Just(request),
							c1: request
						})),
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
									$elm$json$Json$Encode$string('jump-list-request')),
									_Utils_Tuple2(
									'binding',
									$author$project$Binding$encode(binding)),
									_Utils_Tuple2(
									'requestId',
									$elm$json$Json$Encode$string(
										$author$project$UInt64$string(request))),
									_Utils_Tuple2(
									'entry',
									$elm$json$Json$Encode$string(entry))
								])))
					]));
		} else {
			return _Utils_Tuple2(model, _List_Nil);
		}
	}
};
var $author$project$Desktop$readMotionPreferences = function (model) {
	var _v0 = _Utils_Tuple2(
		model.a.b.dk,
		$author$project$UInt64$next(model.c1));
	if ((!_v0.a.$) && (!_v0.b.$)) {
		var binding = _v0.a.a;
		var request = _v0.b.a;
		return _Utils_Tuple2(
			$author$project$Desktop$advance(
				_Utils_update(
					model,
					{
						aK: $elm$core$Maybe$Just(request),
						c1: request
					})),
			_List_fromArray(
				[
					A2($author$project$Desktop$motionPreferencesRequest, binding, request)
				]));
	} else {
		return _Utils_Tuple2(model, _List_Nil);
	}
};
var $author$project$Desktop$readNotifications = function (model) {
	if (!_Utils_eq(model.a0, $elm$core$Maybe$Nothing)) {
		return _Utils_Tuple2(model, _List_Nil);
	} else {
		var _v0 = _Utils_Tuple2(
			model.a.b.dk,
			$author$project$UInt64$next(model.c1));
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var binding = _v0.a.a;
			var request = _v0.b.a;
			return _Utils_Tuple2(
				$author$project$Desktop$advance(
					_Utils_update(
						model,
						{
							a0: $elm$core$Maybe$Just(request),
							c1: request
						})),
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
									$elm$json$Json$Encode$string('notification-request')),
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
			return _Utils_Tuple2(model, _List_Nil);
		}
	}
};
var $author$project$Desktop$readSettings = function (model) {
	var _v0 = _Utils_Tuple2(
		model.a.b.dk,
		$author$project$UInt64$next(model.c1));
	if ((!_v0.a.$) && (!_v0.b.$)) {
		var binding = _v0.a.a;
		var request = _v0.b.a;
		return _Utils_Tuple2(
			$author$project$Desktop$advance(
				_Utils_update(
					model,
					{
						c1: request,
						bo: $elm$core$Maybe$Just(request)
					})),
			_List_fromArray(
				[
					A2($author$project$Desktop$settingsRequest, binding, request)
				]));
	} else {
		return _Utils_Tuple2(model, _List_Nil);
	}
};
var $author$project$Desktop$readShortcutPreferences = function (model) {
	var _v0 = _Utils_Tuple2(
		model.a.b.dk,
		$author$project$UInt64$next(model.c1));
	if ((!_v0.a.$) && (!_v0.b.$)) {
		var binding = _v0.a.a;
		var request = _v0.b.a;
		return _Utils_Tuple2(
			$author$project$Desktop$advance(
				_Utils_update(
					model,
					{
						c1: request,
						aQ: $elm$core$Maybe$Just(request)
					})),
			_List_fromArray(
				[
					A2($author$project$Desktop$shortcutPreferencesRequest, binding, request)
				]));
	} else {
		return _Utils_Tuple2(model, _List_Nil);
	}
};
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
		model.a.b.dk,
		$author$project$UInt64$next(model.c1));
	if ((!_v0.a.$) && (!_v0.b.$)) {
		var binding = _v0.a.a;
		var request = _v0.b.a;
		return _Utils_Tuple2(
			_Utils_update(
				model,
				{
					c1: request,
					aR: $elm$core$Maybe$Just(request),
					aS: $elm$core$Maybe$Nothing
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
var $author$project$Desktop$readSystemMenu = function (model) {
	var _v0 = _Utils_Tuple2(
		model.a.b.dk,
		$author$project$UInt64$next(model.c1));
	if ((!_v0.a.$) && (!_v0.b.$)) {
		var binding = _v0.a.a;
		var request = _v0.b.a;
		return _Utils_Tuple2(
			$author$project$Desktop$advance(
				_Utils_update(
					model,
					{
						c1: request,
						aT: $elm$core$Maybe$Just(request)
					})),
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
								$elm$json$Json$Encode$string('system-menu-request')),
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
		return _Utils_Tuple2(model, _List_Nil);
	}
};
var $author$project$Motion$ready = F2(
	function (binding, model) {
		return (_Utils_eq(model.bF, $elm$core$Maybe$Nothing) && ((!$author$project$MotionPreferences$selected(model.a1)) && _Utils_eq(model.ex, $elm$core$Maybe$Nothing))) || ((!_Utils_eq(model.a1.c, $elm$core$Maybe$Nothing)) && (_Utils_eq(model.ex, $elm$core$Maybe$Nothing) && A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (a) {
					return _Utils_eq(
						binding,
						$elm$core$Maybe$Just(a.dk)) && _Utils_eq(
						a.aC,
						$author$project$Motion$desired(model));
				},
				model.bT))));
	});
var $author$project$Motion$receiptDecoder = A2(
	$author$project$Motion$strict,
	_List_fromArray(
		['protocolVersion', 'kind', 'binding', 'requestId', 'profile']),
	A6(
		$elm$json$Json$Decode$map5,
		F5(
			function (_v0, _v1, binding, request_, profile) {
				return {dk: binding, aC: profile, c1: request_};
			}),
		$author$project$Motion$version,
		$author$project$Motion$kind('motion-profile'),
		A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
		A2($elm$json$Json$Decode$field, 'requestId', $author$project$Motion$positive),
		A2($elm$json$Json$Decode$field, 'profile', $author$project$Motion$profileDecoder)));
var $author$project$Files$normalize = function (value) {
	return (!A2(
		$elm$core$String$startsWith,
		'/',
		$elm$core$String$trim(value))) ? value : ('/' + A2(
		$elm$core$String$join,
		'/',
		$elm$core$List$reverse(
			A3(
				$elm$core$List$foldl,
				F2(
					function (part, parts) {
						return ((part === '') || (part === '.')) ? parts : ((part === '..') ? A2($elm$core$List$drop, 1, parts) : A2($elm$core$List$cons, part, parts));
					}),
				_List_Nil,
				A2(
					$elm$core$String$split,
					'/',
					$elm$core$String$trim(value))))));
};
var $author$project$Files$observe = F2(
	function (snapshot, model) {
		var admitted = A2(
			$elm$core$Maybe$withDefault,
			true,
			A2(
				$elm$core$Maybe$map,
				function (old) {
					return _Utils_eq(snapshot.c7, old.c7) && ((A2($author$project$UInt64$compare, snapshot.c2, old.c2) === 2) || _Utils_eq(snapshot, old));
				},
				model.c));
		return (!admitted) ? model : _Utils_update(
			model,
			{
				ft: (!_Utils_eq(model.ex, $elm$core$Maybe$Nothing)) ? model.ft : (snapshot.dj ? 'Choose a collection or folder.' : snapshot.eH),
				c: $elm$core$Maybe$Just(snapshot)
			});
	});
var $author$project$Files$receive = F4(
	function (request, status, snapshot, model) {
		var _v0 = model.ex;
		if (_v0.$ === 1) {
			return model;
		} else {
			var pending = _v0.a;
			if ((!_Utils_eq(request, pending.c1)) || ((!_Utils_eq(snapshot.c7, pending.aa.c7)) || (!A2(
				$elm$core$List$member,
				status,
				_List_fromArray(
					['Opened', 'Refused', 'Unknown']))))) {
				return model;
			} else {
				var samePeer = function () {
					var _v1 = _Utils_Tuple2(
						A2(
							$elm$core$Maybe$andThen,
							function ($) {
								return $.b2;
							},
							model.c),
						snapshot.b2);
					_v1$2:
					while (true) {
						if (!_v1.a.$) {
							if (!_v1.b.$) {
								var old = _v1.a.a;
								var current = _v1.b.a;
								return _Utils_eq(old.dE, current.dE) && (_Utils_eq(old.dN, current.dN) && _Utils_eq(old.du, current.du));
							} else {
								break _v1$2;
							}
						} else {
							if (!_v1.b.$) {
								var _v2 = _v1.a;
								return true;
							} else {
								break _v1$2;
							}
						}
					}
					return false;
				}();
				var next = A2($author$project$Files$observe, snapshot, model);
				var locationMatches = A2(
					$elm$core$Maybe$withDefault,
					false,
					A2(
						$elm$core$Maybe$map,
						function (peer) {
							return A2(
								$elm$core$String$startsWith,
								'~',
								$elm$core$String$trim(pending.aa.fR)) ? A2($elm$core$String$startsWith, '/', peer.fR) : _Utils_eq(
								peer.fR,
								$author$project$Files$normalize(pending.aa.fR));
						},
						snapshot.b2));
				var opened = snapshot.dj && (samePeer && (locationMatches && ((A2($author$project$UInt64$compare, snapshot.c2, pending.aa.c2) === 2) && A2(
					$elm$core$Maybe$withDefault,
					false,
					A2(
						$elm$core$Maybe$map,
						function ($) {
							return $.eW;
						},
						snapshot.b2)))));
				var notice = ((status === 'Opened') && opened) ? 'Files: requested location opened.' : ((status === 'Refused') ? 'Files: request refused. Refresh before choosing again.' : 'Files: opening not confirmed. Refresh only reads state; this request will not be repeated.');
				return (!_Utils_eq(
					next.c,
					$elm$core$Maybe$Just(snapshot))) ? model : _Utils_update(
					next,
					{
						ft: notice,
						ex: ((status === 'Refused') || ((status === 'Opened') && opened)) ? $elm$core$Maybe$Nothing : model.ex
					});
			}
		}
	});
var $author$project$JumpList$observe = F2(
	function (snapshot, model) {
		var admitted = A2(
			$elm$core$Maybe$withDefault,
			true,
			A2(
				$elm$core$Maybe$map,
				function (old) {
					return _Utils_eq(snapshot.c7, old.c7) && ((A2($author$project$UInt64$compare, snapshot.c2, old.c2) === 2) || _Utils_eq(snapshot, old));
				},
				model.c));
		return (!admitted) ? model : _Utils_update(
			model,
			{
				ft: (!_Utils_eq(model.ex, $elm$core$Maybe$Nothing)) ? model.ft : (snapshot.dj ? ($elm$core$String$isEmpty(snapshot.eH) ? 'Choose an application action or recent file.' : snapshot.eH) : snapshot.eH),
				c: $elm$core$Maybe$Just(snapshot)
			});
	});
var $author$project$JumpList$receive = F4(
	function (request, status, snapshot, model) {
		var _v0 = model.ex;
		if (_v0.$ === 1) {
			return model;
		} else {
			var pending = _v0.a;
			if ((!_Utils_eq(request, pending.c1)) || ((!_Utils_eq(snapshot.c7, pending.aa.c7)) || ((!_Utils_eq(snapshot.d2, pending.aa.d2)) || (!A2(
				$elm$core$List$member,
				status,
				_List_fromArray(
					['Submitted', 'Refused', 'Unknown'])))))) {
				return model;
			} else {
				var next = A2($author$project$JumpList$observe, snapshot, model);
				return (!_Utils_eq(
					next.c,
					$elm$core$Maybe$Just(snapshot))) ? model : _Utils_update(
					next,
					{
						ft: (status === 'Submitted') ? 'Application action: submitted to the native launcher.' : ((status === 'Refused') ? 'Application action: refused or no longer available. Refresh before choosing again.' : 'Application action: not confirmed. Refresh only reads actions; this request will not be repeated.'),
						ex: (status === 'Unknown') ? model.ex : $elm$core$Maybe$Nothing
					});
			}
		}
	});
var $author$project$Launch$Refused = 1;
var $author$project$Launch$Submitted = 0;
var $author$project$Launch$Intent = F4(
	function (request, lifetime, generation, entry) {
		return {d2: entry, fh: generation, fp: lifetime, c1: request};
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
		return ((receipt.eU !== 1) || (receipt.ej !== 'launch-outcome')) ? $elm$json$Json$Decode$fail('Launch receipt version/kind') : (((receipt.dc === 'Submitted') && (receipt.eH === 'native-submission-accepted')) ? $elm$json$Json$Decode$succeed(
			_Utils_Tuple2(receipt.aa, 0)) : (((receipt.dc === 'Unknown') && (receipt.eH === 'submission-not-confirmed')) ? $elm$json$Json$Decode$succeed(
			_Utils_Tuple2(receipt.aa, 2)) : (((receipt.dc === 'Refused') && A2(
			$elm$core$List$member,
			receipt.eH,
			_List_fromArray(
				['retired-authority', 'request-reuse', 'retired-request', 'catalog-unavailable', 'stale-catalog', 'removed-entry', 'native-entry-unavailable', 'desktop-entry-raced']))) ? $elm$json$Json$Decode$succeed(
			_Utils_Tuple2(receipt.aa, 1)) : $elm$json$Json$Decode$fail('Launch receipt outcome'))));
	},
	A2(
		$author$project$Launch$strict,
		_List_fromArray(
			['catalogProtocol', 'kind', 'intent', 'status', 'reason']),
		A6(
			$elm$json$Json$Decode$map5,
			F5(
				function (version, kind, intent, state, reason) {
					return {aa: intent, ej: kind, eH: reason, dc: state, eU: version};
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
			model.j,
			A2($elm$json$Json$Decode$decodeValue, $author$project$Launch$receiptDecoder, raw));
		if ((_v0.a.$ === 1) && (!_v0.b.$)) {
			var _v1 = _v0.a;
			var owner = _v1.a;
			var intent = _v1.b;
			var _v2 = _v0.b.a;
			var received = _v2.a;
			var result = _v2.b;
			return (_Utils_eq(host, owner) && (_Utils_eq(
				model.be,
				$elm$core$Maybe$Just(owner)) && _Utils_eq(received, intent))) ? $author$project$Launch$advance(
				_Utils_update(
					model,
					{
						j: A2($author$project$Launch$Settled, intent, result)
					})) : current;
		} else {
			return current;
		}
	});
var $author$project$Motion$receive = F3(
	function (binding, receipt, model) {
		return ((!_Utils_eq(
			binding,
			$elm$core$Maybe$Just(receipt.dk))) || (!_Utils_eq(
			model.ex,
			$elm$core$Maybe$Just(receipt)))) ? model : _Utils_update(
			model,
			{
				bT: $elm$core$Maybe$Just(
					{dk: receipt.dk, aC: receipt.aC}),
				ex: $elm$core$Maybe$Nothing
			});
	});
var $author$project$MotionPreferences$receive = F4(
	function (request, status, snapshot, model) {
		var _v0 = model.ex;
		if (_v0.$ === 1) {
			return model;
		} else {
			var pending = _v0.a;
			return (!_Utils_eq(request, pending.c1)) ? model : (((status === 'Saved') && A2(
				$elm$core$Maybe$withDefault,
				false,
				A2(
					$elm$core$Maybe$map,
					function (s) {
						return _Utils_eq(s.fy, pending.fy) && (A2($author$project$UInt64$compare, s.c2, pending.c2) === 2);
					},
					snapshot))) ? _Utils_update(
				model,
				{ft: 'Motion preference saved.', ex: $elm$core$Maybe$Nothing, c: snapshot}) : ((status === 'Refused') ? _Utils_update(
				model,
				{ft: 'Motion preference refused. Refresh, then choose again.', ex: $elm$core$Maybe$Nothing}) : _Utils_update(
				model,
				{ft: 'Motion preference save not confirmed. Refresh to read stored values; this write will not be repeated.'})));
		}
	});
var $author$project$Pins$receive = F4(
	function (request, status, snapshot, model) {
		var _v0 = model.ex;
		if (!_v0.$) {
			var pending = _v0.a;
			return (!_Utils_eq(pending.c1, request)) ? model : (((status === 'Saved') && A2(
				$elm$core$Maybe$withDefault,
				false,
				A2(
					$elm$core$Maybe$map,
					function (s) {
						return _Utils_eq(s.fl, pending.fl) && A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (old) {
									return A2($author$project$UInt64$compare, s.c2, old.c2) === 2;
								},
								model.c));
					},
					snapshot))) ? _Utils_update(
				model,
				{ft: 'Pin order saved.', ex: $elm$core$Maybe$Nothing, c: snapshot}) : ((status === 'Refused') ? _Utils_update(
				model,
				{ft: 'Pin change refused. Refresh applications and choose again.', ex: $elm$core$Maybe$Nothing}) : _Utils_update(
				model,
				{ft: 'Pin save not confirmed. Refresh applications to read the order; the change will not be repeated.'})));
		} else {
			return model;
		}
	});
var $author$project$PointerOwnership$receive = F3(
	function (expected, snapshot, model) {
		if (!_Utils_eq(
			expected,
			$elm$core$Maybe$Just(snapshot.dk))) {
			return model;
		} else {
			var _v0 = model.bF;
			if (!_v0.$) {
				var prior = _v0.a;
				return (_Utils_eq(prior.dk, snapshot.dk) && (A2($author$project$UInt64$compare, snapshot.c6, prior.c6) !== 2)) ? model : {
					bF: $elm$core$Maybe$Just(snapshot)
				};
			} else {
				return {
					bF: $elm$core$Maybe$Just(snapshot)
				};
			}
		}
	});
var $author$project$Settings$Saved = 0;
var $author$project$Settings$Unconfirmed = 2;
var $author$project$Settings$receive = F4(
	function (request, status, snapshot, model) {
		var _v0 = model.ex;
		if (_v0.$ === 1) {
			return model;
		} else {
			var pending = _v0.a;
			return (!_Utils_eq(request, pending.c1)) ? model : (((status === 'Saved') && A2(
				$elm$core$Maybe$withDefault,
				false,
				A2(
					$elm$core$Maybe$map,
					function (current) {
						return _Utils_eq(current.bs, pending.bs) && A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (old) {
									return A2($author$project$UInt64$compare, current.c2, old.c2) === 2;
								},
								model.c));
					},
					snapshot))) ? _Utils_update(
				model,
				{
					ft: 'Settings saved.',
					cZ: $elm$core$Maybe$Just(
						{c1: request, fJ: 0}),
					ex: $elm$core$Maybe$Nothing,
					c: snapshot
				}) : ((status === 'Refused') ? _Utils_update(
				model,
				{
					ft: 'Settings change refused. Refresh, then choose again.',
					cZ: $elm$core$Maybe$Just(
						{c1: request, fJ: 1}),
					ex: $elm$core$Maybe$Nothing
				}) : _Utils_update(
				model,
				{
					ft: 'Settings save not confirmed. Refresh to read the stored values; this write will not be repeated.',
					cZ: $elm$core$Maybe$Just(
						{c1: request, fJ: 2})
				})));
		}
	});
var $author$project$ShortcutPreferences$receive = F5(
	function (request, status, snapshot, inventory, model) {
		var _v0 = model.ex;
		if (_v0.$ === 1) {
			return model;
		} else {
			var pending = _v0.a;
			return (!_Utils_eq(pending.c1, request)) ? model : (((status === 'Saved') && (A2(
				$elm$core$Maybe$withDefault,
				false,
				A2(
					$elm$core$Maybe$map,
					function (current) {
						return _Utils_eq(current.ae, pending.ae) && A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (old) {
									return !(!A2($author$project$UInt64$compare, current.c2, old.c2));
								},
								model.c));
					},
					snapshot)) && A2(
				$elm$core$Maybe$withDefault,
				false,
				A2(
					$elm$core$Maybe$map,
					function (_native) {
						return A2(
							$elm$core$List$all,
							function (route) {
								return _Utils_eq(
									A2($author$project$ShortcutPreferences$choices, route, pending.ae),
									A2($author$project$ShortcutPreferences$row, route, _native).bt);
							},
							_List_fromArray(
								['applications', 'system', 'notifications']));
					},
					inventory)))) ? _Utils_update(
				model,
				{cV: inventory, ft: 'Shortcut choices saved and active. Existing bindings were preserved.', ex: $elm$core$Maybe$Nothing, c: snapshot}) : (((status === 'Stored') && A2(
				$elm$core$Maybe$withDefault,
				false,
				A2(
					$elm$core$Maybe$map,
					function (current) {
						return _Utils_eq(current.ae, pending.ae);
					},
					snapshot))) ? _Utils_update(
				model,
				{cV: inventory, ft: 'Choices saved, but live bindings changed. Refresh and choose a free shortcut before applying.', ex: $elm$core$Maybe$Nothing, c: snapshot}) : ((status === 'Refused') ? _Utils_update(
				model,
				{ft: 'Shortcut choices refused. Bindings or stored choices changed; refresh and choose again.', ex: $elm$core$Maybe$Nothing}) : _Utils_update(
				model,
				{ft: 'Shortcut application not confirmed. Refresh reads stored choices and live bindings; this action will not be repeated.'}))));
		}
	});
var $author$project$Shortcuts$receive = F3(
	function (expected, snapshot, model) {
		if (!_Utils_eq(
			expected,
			$elm$core$Maybe$Just(snapshot.dk))) {
			return _Utils_Tuple3(model, $elm$core$Maybe$Nothing, $elm$core$Maybe$Nothing);
		} else {
			if (!_Utils_eq(model.dk, expected)) {
				return _Utils_Tuple3(
					{dk: expected, bM: snapshot.c6},
					$elm$core$Maybe$Nothing,
					$elm$core$Maybe$Nothing);
			} else {
				if (A2($author$project$UInt64$compare, snapshot.c6, model.bM) !== 2) {
					return _Utils_Tuple3(model, $elm$core$Maybe$Nothing, $elm$core$Maybe$Nothing);
				} else {
					var next = _Utils_update(
						model,
						{bM: snapshot.c6});
					var fresh = A2(
						$elm$core$List$filter,
						function (event) {
							return A2($author$project$UInt64$compare, event.c6, model.bM) === 2;
						},
						snapshot.by);
					var contiguous = A2(
						$elm$core$Maybe$withDefault,
						false,
						A2(
							$elm$core$Maybe$map,
							function (event) {
								return _Utils_eq(
									$author$project$UInt64$next(model.bM),
									$elm$core$Maybe$Just(event.c6));
							},
							$elm$core$List$head(fresh)));
					return snapshot.e6 ? _Utils_Tuple3(
						next,
						$elm$core$Maybe$Nothing,
						$elm$core$Maybe$Just('Shell shortcut unavailable while input is blocked.')) : ((!contiguous) ? _Utils_Tuple3(
						next,
						$elm$core$Maybe$Nothing,
						$elm$core$Maybe$Just('Shortcut history expired. Press the shortcut again.')) : _Utils_Tuple3(
						next,
						A2(
							$elm$core$Maybe$map,
							function ($) {
								return $.eM;
							},
							$elm$core$List$head(
								$elm$core$List$reverse(fresh))),
						$elm$core$Maybe$Nothing));
				}
			}
		}
	});
var $author$project$SystemMenu$observe = F2(
	function (current, model) {
		var admitted = function () {
			var _v0 = model.c;
			if (_v0.$ === 1) {
				return true;
			} else {
				var old = _v0.a;
				return _Utils_eq(current.c7, old.c7) && ((A2($author$project$UInt64$compare, current.c2, old.c2) === 2) || _Utils_eq(current, old));
			}
		}();
		return (!admitted) ? model : _Utils_update(
			model,
			{
				ft: (!_Utils_eq(model.ex, $elm$core$Maybe$Nothing)) ? model.ft : 'Current system state. Unavailable controls cannot be changed.',
				c: $elm$core$Maybe$Just(current)
			});
	});
var $author$project$SystemMenu$receive = F4(
	function (request, status, snapshot, model) {
		var _v0 = model.ex;
		if (_v0.$ === 1) {
			return model;
		} else {
			var pending = _v0.a;
			if ((!_Utils_eq(request, pending.c1)) || ((!A2(
				$elm$core$List$member,
				status,
				_List_fromArray(
					['Committed', 'Submitted', 'Refused', 'Unknown']))) || (!_Utils_eq(snapshot.c7, pending.aa.c7)))) {
				return model;
			} else {
				var notice = _Utils_ap(
					$author$project$SystemMenu$name(pending.aa.bh),
					(status === 'Committed') ? ': change observed.' : ((status === 'Submitted') ? ': request accepted by the native service.' : ((status === 'Refused') ? ': refused or no longer available. Refresh before choosing again.' : ': not confirmed. Refresh only reads state; the request will not be repeated.')));
				var next = A2($author$project$SystemMenu$observe, snapshot, model);
				return (!_Utils_eq(
					next.c,
					$elm$core$Maybe$Just(snapshot))) ? model : _Utils_update(
					next,
					{
						ft: notice,
						ex: (status === 'Unknown') ? model.ex : $elm$core$Maybe$Nothing
					});
			}
		}
	});
var $author$project$Menu$abandonPrepared = F3(
	function (local, bound, _v0) {
		var state = _v0;
		return _Utils_update(
			state,
			{
				aI: $elm$core$Maybe$Nothing,
				fx: A2(
					$elm$core$List$filter,
					function (entry) {
						return !(_Utils_eq(entry.cl, local) && (_Utils_eq(entry.dk, bound) && (!entry.bq)));
					},
					state.fx)
			});
	});
var $author$project$MenuBridge$retireChoices = function (_v0) {
	var state = _v0;
	var menu = function () {
		var _v2 = state.O;
		if (!_v2.$) {
			var slot = _v2.a;
			return A3($author$project$Menu$abandonPrepared, slot.cq, slot.b0, state.aI);
		} else {
			return state.aI;
		}
	}();
	var closed = function () {
		var _v1 = $author$project$Menu$snapshot(menu).aI;
		if (!_v1.$) {
			var view = _v1.a;
			return A2(
				$author$project$Menu$update,
				$author$project$Menu$Dismiss(view.cl),
				menu).a;
		} else {
			return menu;
		}
	}();
	return _Utils_update(
		state,
		{aI: closed, O: $elm$core$Maybe$Nothing});
};
var $elm$core$List$sum = function (numbers) {
	return A3($elm$core$List$foldl, $elm$core$Basics$add, 0, numbers);
};
var $author$project$Switcher$advanceSelection = function (model) {
	var through = A2(
		$elm$core$Maybe$withDefault,
		0,
		A2(
			$elm$core$Maybe$map,
			function ($) {
				return $.df;
			},
			model.ba));
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
				$elm$core$Dict$toList(model.bO))));
	var ring = _Utils_eq(model.ba, $elm$core$Maybe$Nothing) ? model.dL : A2(
		$elm$core$List$map,
		function ($) {
			return $.r;
		},
		model.af);
	var size = $elm$core$List$length(ring);
	var anchor = A2(
		$elm$core$Maybe$withDefault,
		_Utils_eq(
			A2($elm$core$Dict$get, 1, model.bO),
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
				A2($elm$core$Maybe$withDefault, $author$project$UInt64$zero, model.cY),
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.r;
					},
					model.ba))));
	var position = (!size) ? 0 : A2($elm$core$Basics$modBy, size, anchor + total);
	var survivor = $elm$core$List$head(
		A2(
			$elm$core$List$filter,
			function (identity) {
				return A2(
					$elm$core$List$any,
					function (row) {
						return _Utils_eq(row.r, identity);
					},
					model.af);
			},
			_Utils_ap(
				A2($elm$core$List$drop, position, ring),
				A2($elm$core$List$take, position, ring))));
	return _Utils_update(
		model,
		{
			fN: A2(
				$elm$core$Maybe$withDefault,
				0,
				A2(
					$elm$core$Maybe$andThen,
					function (identity) {
						return A2($author$project$Switcher$index, identity, model.af);
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
						model.c0))) {
					return _Utils_Tuple2(original, $elm$core$Maybe$Nothing);
				} else {
					var _v1 = A2($elm$core$Dict$get, ordinal, model.bO);
					if (!_v1.$) {
						var previous = _v1.a;
						return _Utils_eq(previous, direction) ? _Utils_Tuple2(original, $elm$core$Maybe$Nothing) : _Utils_Tuple2(
							_Utils_update(
								model,
								{af: _List_Nil, j: 4}),
							$elm$core$Maybe$Nothing);
					} else {
						var next = _Utils_update(
							model,
							{
								bO: A3($elm$core$Dict$insert, ordinal, direction, model.bO)
							});
						return $author$project$Switcher$settle(
							next.b5 ? $author$project$Switcher$advanceSelection(next) : next);
					}
				}
			}
		}
	});
var $author$project$Switcher$readyWith = F6(
	function (frozenRoots, token, history, candidates, origin, original) {
		var model = original;
		if ((!_Utils_eq(token, model.fh)) || ((!$author$project$Switcher$writable(model)) || model.b5)) {
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
									return _Utils_eq(old.r, row.r);
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
					return row.dj && A2(
						$elm$core$Maybe$withDefault,
						true,
						A2(
							$elm$core$Maybe$map,
							$elm$core$List$member(row.r),
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
									return _Utils_eq(row.r, root);
								},
								eligible));
					},
					history));
			var unranked = A2(
				$elm$core$List$sortWith,
				F2(
					function (a, b) {
						return A2($author$project$UInt64$compare, a.r, b.r);
					}),
				unique(
					A2(
						$elm$core$List$filter,
						function (row) {
							return !A2(
								$elm$core$List$any,
								function (old) {
									return _Utils_eq(old.r, row.r);
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
						return $.r;
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
					{j: 4}),
				$elm$core$Maybe$Nothing) : $author$project$Switcher$settle(
				$author$project$Switcher$advanceSelection(
					_Utils_update(
						model,
						{af: frozen, cY: origin, b5: true, dL: ring})));
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
		if ((!$author$project$Switcher$writable(model)) || (!model.b5)) {
			return original;
		} else {
			var prior = A2(
				$elm$core$Maybe$map,
				function ($) {
					return $.r;
				},
				$author$project$Switcher$selected(original));
			var current = function (old) {
				return $elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (row) {
							return row.dj && (_Utils_eq(row.r, old.r) && _Utils_eq(row.di, old.di));
						},
						candidates));
			};
			var surviving = A2($elm$core$List$filterMap, current, model.af);
			var after = _Utils_ap(
				A2($elm$core$List$drop, model.fN, model.af),
				A2($elm$core$List$take, model.fN, model.af));
			var fallback = $elm$core$List$head(
				A2(
					$elm$core$List$filterMap,
					function (old) {
						return A2(
							$elm$core$Maybe$map,
							function ($) {
								return $.r;
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
								return _Utils_eq(row.r, identity);
							},
							surviving) ? $elm$core$Maybe$Just(identity) : $elm$core$Maybe$Nothing;
					},
					prior));
			var baseline = (model.j === 2) ? $elm$core$Maybe$Just(
				{
					r: root,
					df: $author$project$Switcher$lastOrdinal(model)
				}) : model.ba;
			var position = A2(
				$elm$core$Maybe$withDefault,
				0,
				A2($author$project$Switcher$index, root, surviving));
			return _Utils_update(
				model,
				{
					ba: baseline,
					af: surviving,
					j: $elm$core$List$isEmpty(surviving) ? 4 : model.j,
					fN: position
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
							'switcher:family:' + $author$project$UInt64$string(family.r)))
					]);
			},
			$author$project$Switcher$selected(model.i)));
};
var $author$project$Switcher$ready = $author$project$Switcher$readyWith($elm$core$Maybe$Nothing);
var $author$project$Desktop$syncLocalSwitcher = function (model) {
	var _v0 = _Utils_Tuple3(
		model.aS,
		model.a.b._.as,
		$author$project$TaskView$groups(model.a.b));
	if (((!_v0.a.$) && (!_v0.b.$)) && (!_v0.c.$)) {
		var history = _v0.a.a;
		var observed = _v0.b.a;
		var groups = _v0.c.a;
		if ($author$project$Switcher$phase(model.i) === 2) {
			return _Utils_Tuple2(
				_Utils_update(
					model,
					{
						i: A2(
							$author$project$Switcher$reconcile,
							A2(
								$elm$core$List$concatMap,
								function ($) {
									return $.a;
								},
								groups),
							model.i)
					}),
				_List_Nil);
		} else {
			if (!_Utils_eq(history.P, observed.P)) {
				return _Utils_eq(model.aR, $elm$core$Maybe$Nothing) ? $author$project$Desktop$readSwitcherHistory(model) : _Utils_Tuple2(model, _List_Nil);
			} else {
				var _v1 = A5(
					$author$project$Switcher$ready,
					$author$project$Switcher$generation(model.i),
					history.aP,
					A2(
						$elm$core$List$concatMap,
						function ($) {
							return $.a;
						},
						groups),
					model.cw,
					model.i);
				var switcher = _v1.a;
				var selected = _v1.b;
				var next = $author$project$Desktop$advance(
					_Utils_update(
						model,
						{i: switcher}));
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
		var _v0 = model.ah;
		if (!_v0.$) {
			var chord = _v0.a;
			var _v1 = $author$project$TaskView$groups(model.a.b);
			if (!_v1.$) {
				var groups = _v1.a;
				var candidates = A2(
					$elm$core$List$filter,
					function (row) {
						return A2($elm$core$List$member, row.r, chord.aP);
					},
					A2(
						$elm$core$List$concatMap,
						function ($) {
							return $.a;
						},
						groups));
				var _v2 = ($author$project$Switcher$phase(model.i) === 2) ? _Utils_Tuple2(
					A2($author$project$Switcher$reconcile, candidates, model.i),
					$elm$core$Maybe$Nothing) : A6(
					$author$project$Switcher$readyFrozen,
					$author$project$Switcher$generation(model.i),
					chord.aP,
					chord.ck,
					candidates,
					chord.cY,
					model.i);
				var switcher = _v2.a;
				var selected = _v2.b;
				var next = $author$project$Desktop$advance(
					_Utils_update(
						model,
						{i: switcher}));
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
		var old = model.ah;
		var order = A2(
			$elm$core$Maybe$withDefault,
			2,
			A2(
				$elm$core$Maybe$map,
				function (previous) {
					return A2($author$project$UInt64$compare, chord.fh, previous.fh);
				},
				old));
		var inconsistent = A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (previous) {
					return (order === 1) && ((!_Utils_eq(previous.aP, chord.aP)) || ((!_Utils_eq(previous.ck, chord.ck)) || ((!_Utils_eq(previous.cY, chord.cY)) || ((!_Utils_eq(
						A2(
							$elm$core$List$take,
							$elm$core$List$length(previous.bO),
							chord.bO),
						previous.bO)) || ((previous.c0 && (!chord.c0)) || ((previous.cH && (!chord.cH)) || (previous.cL && (!chord.cL))))))));
				},
				old));
		var closed = function () {
			var retired = $author$project$Desktop$advance(
				$author$project$Desktop$retireSwitcher(
					_Utils_update(
						model,
						{
							p: false,
							B: false,
							o: $elm$core$Maybe$Nothing,
							w: false,
							ah: $elm$core$Maybe$Just(chord),
							t: false,
							D: false,
							n: false,
							L: false,
							s: $elm$core$Maybe$Nothing,
							v: false,
							E: false
						})));
			var choice = A2(
				$elm$core$Maybe$andThen,
				function (pending) {
					return _Utils_eq(
						pending.aV,
						$elm$core$Maybe$Just(chord.fh)) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(pending);
				},
				retired.k);
			return _Utils_Tuple2(
				_Utils_update(
					retired,
					{k: choice}),
				_List_Nil);
		}();
		if (_Utils_eq(chord.fh, $author$project$UInt64$zero) || (!order)) {
			return _Utils_Tuple2(model, _List_Nil);
		} else {
			if (inconsistent || (chord.cH || chord.cL)) {
				return closed;
			} else {
				var localGeneration = (order === 2) ? $author$project$UInt64$next(
					$author$project$Switcher$generation(model.i)) : $elm$core$Maybe$Just(
					$author$project$Switcher$generation(model.i));
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
							k: $elm$core$Maybe$Nothing,
							G: '',
							A: $elm$core$Maybe$Nothing,
							p: false,
							B: false,
							o: $elm$core$Maybe$Nothing,
							w: false,
							H: $elm$core$Maybe$Nothing,
							ah: $elm$core$Maybe$Just(chord),
							t: false,
							D: false,
							q: false,
							m: false,
							u: $elm$core$Maybe$Nothing,
							n: false,
							L: false,
							aR: $elm$core$Maybe$Nothing,
							aS: $elm$core$Maybe$Nothing,
							s: $elm$core$Maybe$Nothing,
							v: false,
							E: false,
							a: _Utils_update(
								windows,
								{
									h: $author$project$MenuBridge$retireChoices(windows.h),
									J: $elm$core$Maybe$Nothing
								})
						}) : _Utils_update(
						model,
						{
							p: false,
							B: false,
							o: $elm$core$Maybe$Nothing,
							w: false,
							ah: $elm$core$Maybe$Just(chord),
							t: false,
							D: false,
							n: false,
							L: false,
							s: $elm$core$Maybe$Nothing,
							v: false,
							E: false
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
						_Utils_Tuple2(base.i, $elm$core$Maybe$Nothing),
						A2($elm$core$List$indexedMap, $elm$core$Tuple$pair, chord.bO));
					var stepped = _v1.a;
					var _v4 = chord.c0 ? A3(
						$author$project$Switcher$release,
						generation,
						$elm$core$List$length(chord.bO),
						stepped) : _Utils_Tuple2(stepped, $elm$core$Maybe$Nothing);
					var released = _v4.a;
					var selected = _v4.b;
					var next = $author$project$Desktop$advance(
						_Utils_update(
							base,
							{i: released}));
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
var $author$project$Notifications$receiveReason = F5(
	function (request, status, reason, current, model) {
		var _v0 = model.ex;
		if (_v0.$ === 1) {
			return model;
		} else {
			var pending = _v0.a;
			if ((!_Utils_eq(request, pending.c1)) || ((!A2(
				$elm$core$List$member,
				status,
				_List_fromArray(
					['Dispatched', 'Refused', 'Unknown']))) || (!_Utils_eq(current.c7, pending.fR.c7)))) {
				return model;
			} else {
				var observed = A2($author$project$Notifications$observe, current, model);
				var expired = (reason === 'expired') || A2(
					$elm$core$Maybe$withDefault,
					pending.bV,
					A2(
						$elm$core$Maybe$map,
						function ($) {
							return $.bV;
						},
						observed.ex));
				var outcome = $elm$core$Maybe$Just(
					{bV: expired, c1: request, W: status, fR: pending.fR});
				return (!_Utils_eq(
					observed.c,
					$elm$core$Maybe$Just(current))) ? model : ((status === 'Unknown') ? _Utils_update(
					observed,
					{ft: 'Notification action not confirmed. It will not be repeated.', cZ: outcome}) : _Utils_update(
					observed,
					{
						ft: (status === 'Dispatched') ? 'Notification action sent.' : 'Notification action refused. The target expired or changed; choose a current notification.',
						cZ: outcome,
						ex: $elm$core$Maybe$Nothing
					}));
			}
		}
	});
var $author$project$Files$reconcile = F2(
	function (snapshot, model) {
		var next = A2($author$project$Files$observe, snapshot, model);
		var _v0 = next.ex;
		if (_v0.$ === 1) {
			return next;
		} else {
			var pending = _v0.a;
			return (_Utils_eq(
				next.c,
				$elm$core$Maybe$Just(snapshot)) && (A2($author$project$UInt64$compare, snapshot.c2, pending.aa.c2) === 2)) ? _Utils_update(
				next,
				{ft: 'Files state refreshed. The previous request will not be repeated.', ex: $elm$core$Maybe$Nothing}) : next;
		}
	});
var $author$project$JumpList$reconcile = F2(
	function (snapshot, model) {
		var next = A2($author$project$JumpList$observe, snapshot, model);
		var _v0 = next.ex;
		if (_v0.$ === 1) {
			return next;
		} else {
			var pending = _v0.a;
			return (_Utils_eq(
				next.c,
				$elm$core$Maybe$Just(snapshot)) && (A2($author$project$UInt64$compare, snapshot.c2, pending.aa.c2) === 2)) ? _Utils_update(
				next,
				{ft: 'Application actions refreshed. The previous request will not be repeated.', ex: $elm$core$Maybe$Nothing}) : next;
		}
	});
var $author$project$Notifications$reconcile = F2(
	function (snapshot, model) {
		var current = A2($author$project$Notifications$observe, snapshot, model);
		var _v0 = current.ex;
		if (_v0.$ === 1) {
			return current;
		} else {
			var pending = _v0.a;
			return (_Utils_eq(
				current.c,
				$elm$core$Maybe$Just(snapshot)) && (!A2(
				$elm$core$List$any,
				function (row) {
					return _Utils_eq(row.cl, pending.fR.cl) && (_Utils_eq(row.aq, pending.fR.aq) && (_Utils_eq(row.ab, pending.fR.ab) && (row.dc === 'live')));
				},
				snapshot.af))) ? _Utils_update(
				current,
				{ft: 'Notification target is no longer live. Its action will not be repeated.', ex: $elm$core$Maybe$Nothing}) : current;
		}
	});
var $author$project$SystemMenu$reconcile = F2(
	function (snapshot, model) {
		var next = A2($author$project$SystemMenu$observe, snapshot, model);
		var _v0 = next.ex;
		if (_v0.$ === 1) {
			return next;
		} else {
			var pending = _v0.a;
			return (_Utils_eq(
				next.c,
				$elm$core$Maybe$Just(snapshot)) && (A2($author$project$UInt64$compare, snapshot.c2, pending.aa.c2) === 2)) ? _Utils_update(
				next,
				{ft: 'System state refreshed. The previous request will not be repeated.', ex: $elm$core$Maybe$Nothing}) : next;
		}
	});
var $author$project$Desktop$requestApplications = F3(
	function (opening, stamp, model) {
		if ((!_Utils_eq(
			$author$project$Desktop$capture(model),
			$elm$core$Maybe$Just(stamp))) || (!_Utils_eq(
			$author$project$MenuBridge$preparedSnapshot(model.a.h),
			$elm$core$Maybe$Nothing))) {
			return _Utils_Tuple2(model, _List_Nil);
		} else {
			var base = function () {
				var _v1 = $author$project$MenuBridge$menuSnapshot(model.a.h).aI;
				if (_v1.$ === 1) {
					return model;
				} else {
					var menu = _v1.a;
					return A2(
						$author$project$Desktop$windowBase,
						$author$project$TaskbarShell$MenuEvent(
							$author$project$Menu$Dismiss(menu.cl)),
						model).a;
				}
			}();
			var windows = base.a;
			var retired = $author$project$Desktop$advance(
				$author$project$Desktop$retireSwitcher(
					_Utils_update(
						base,
						{
							aD: $elm$core$Maybe$Nothing,
							bu: $elm$core$Maybe$Nothing,
							bv: opening,
							A: $elm$core$Maybe$Nothing,
							p: false,
							B: false,
							o: $elm$core$Maybe$Nothing,
							w: false,
							M: A2($author$project$Launch$catalog, $elm$json$Json$Encode$null, model.M),
							H: $elm$core$Maybe$Nothing,
							t: false,
							D: false,
							q: true,
							m: false,
							u: $elm$core$Maybe$Nothing,
							n: false,
							L: false,
							x: $elm$core$Maybe$Nothing,
							s: $elm$core$Maybe$Nothing,
							v: false,
							E: false,
							a: _Utils_update(
								windows,
								{J: $elm$core$Maybe$Nothing})
						})));
			var _v0 = _Utils_Tuple2(
				model.a.b.dk,
				$author$project$UInt64$next(model.c1));
			if ((!_v0.a.$) && (!_v0.b.$)) {
				var binding = _v0.a.a;
				var request = _v0.b.a;
				return ((!model.a.b.j) || _Utils_eq(retired.aO, $elm$core$Maybe$Nothing)) ? _Utils_Tuple2(retired, _List_Nil) : _Utils_Tuple2(
					_Utils_update(
						retired,
						{
							A: $elm$core$Maybe$Just(request),
							c1: request
						}),
					_Utils_ap(
						_List_fromArray(
							[
								A2($author$project$Desktop$catalogRequest, binding, request)
							]),
						opening ? _List_fromArray(
							[
								$author$project$Desktop$Focus('launcher-search')
							]) : _List_Nil));
			} else {
				return _Utils_Tuple2(retired, _List_Nil);
			}
		}
	});
var $author$project$OverviewRecovery$Returning = function (a) {
	return {$: 3, a: a};
};
var $author$project$OverviewRecovery$observe = F5(
	function (authority, transaction, occupied, ready, model) {
		var origin = function () {
			switch (model.$) {
				case 0:
					return $elm$core$Maybe$Nothing;
				case 1:
					var owner = model.a;
					return $elm$core$Maybe$Just(owner);
				case 2:
					var owner = model.a;
					return $elm$core$Maybe$Just(owner);
				default:
					var owner = model.a;
					return $elm$core$Maybe$Just(owner);
			}
		}();
		var matched = function () {
			var _v1 = _Utils_Tuple2(model, transaction);
			if ((_v1.a.$ === 2) && (!_v1.b.$)) {
				var _v2 = _v1.a;
				var owner = _v2.a;
				var intent = _v2.b;
				var outcome = _v1.b.a;
				if (!_Utils_eq(outcome.aa, intent)) {
					return model;
				} else {
					var _v3 = outcome.W;
					switch (_v3) {
						case 2:
							return $author$project$OverviewRecovery$Returning(owner);
						case 1:
							return $author$project$OverviewRecovery$Idle;
						case 3:
							return $author$project$OverviewRecovery$Idle;
						default:
							return model;
					}
				}
			} else {
				return model;
			}
		}();
		if (occupied || A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (owner) {
					return !_Utils_eq(
						authority,
						$elm$core$Maybe$Just(owner.dk));
				},
				origin))) {
			return _Utils_Tuple2($author$project$OverviewRecovery$Idle, $elm$core$Maybe$Nothing);
		} else {
			if (matched.$ === 3) {
				var owner = matched.a;
				return ready ? _Utils_Tuple2(
					$author$project$OverviewRecovery$Idle,
					$elm$core$Maybe$Just(owner)) : _Utils_Tuple2(matched, $elm$core$Maybe$Nothing);
			} else {
				return _Utils_Tuple2(matched, $elm$core$Maybe$Nothing);
			}
		}
	});
var $author$project$Desktop$resumeOverview = function (model) {
	var occupied = model.m || (model.q || ((!_Utils_eq(model.x, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(model.o, $elm$core$Maybe$Nothing)) || (model.p || (model.v || (model.t || (model.n || ($author$project$Desktop$switcherOpen(model) || ((!_Utils_eq(model.a.J, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(
		$author$project$MenuBridge$menuSnapshot(model.a.h).aI,
		$elm$core$Maybe$Nothing)) || (!_Utils_eq(
		$author$project$MenuBridge$preparedSnapshot(model.a.h),
		$elm$core$Maybe$Nothing))))))))))));
	var groups = $author$project$TaskView$groups(model.a.b);
	var ready = $author$project$Shell$available(model.a.b) && (_Utils_eq(model.a.b.A, $elm$core$Maybe$Nothing) && (_Utils_eq(model.a.b.eb, $elm$core$Maybe$Nothing) && (_Utils_eq(model.k, $elm$core$Maybe$Nothing) && ((!_Utils_eq(model.aO, $elm$core$Maybe$Nothing)) && ((!_Utils_eq(groups, $elm$core$Maybe$Nothing)) && (!A2($author$project$PointerOwnership$blocked, model.a.b.dk, model.bH)))))));
	var authority = A2(
		$elm$core$List$member,
		model.a.b.j,
		_List_fromArray(
			[0, 3])) ? $elm$core$Maybe$Nothing : model.a.b.dk;
	var _v0 = A5($author$project$OverviewRecovery$observe, authority, model.a.b._.fS, occupied, ready, model.aN);
	var recovery = _v0.a;
	var origin = _v0.b;
	var next = _Utils_update(
		model,
		{aN: recovery});
	if (origin.$ === 1) {
		return _Utils_Tuple2(next, _List_Nil);
	} else {
		var owner = origin.a;
		var current = A2($elm$core$Maybe$withDefault, _List_Nil, groups);
		var workspace = A2(
			$elm$core$Maybe$andThen,
			function (selected) {
				return A2(
					$elm$core$List$any,
					function (group) {
						return _Utils_eq(group.cU, selected);
					},
					current) ? $elm$core$Maybe$Just(selected) : $elm$core$Maybe$Nothing;
			},
			owner.e$);
		var family = A2(
			$elm$core$List$any,
			function (row) {
				return _Utils_eq(row.r, owner.r) && (row.dj && (!A3($author$project$MenuBridge$blockedFor, row.r, model.a.b, model.a.h)));
			},
			A2(
				$elm$core$List$concatMap,
				function ($) {
					return $.a;
				},
				A2(
					$elm$core$List$filter,
					function (group) {
						return _Utils_eq(workspace, $elm$core$Maybe$Nothing) || _Utils_eq(
							workspace,
							$elm$core$Maybe$Just(group.cU));
					},
					current)));
		var reopened = $author$project$Desktop$advance(
			_Utils_update(
				next,
				{m: true, aB: $elm$core$Maybe$Nothing, at: workspace, u: $elm$core$Maybe$Nothing}));
		var target = family ? ('overview:family:' + $author$project$UInt64$string(owner.r)) : A2(
			$elm$core$Maybe$withDefault,
			'overview:all',
			A2(
				$elm$core$Maybe$map,
				$elm$core$Basics$append('overview:workspace:'),
				workspace));
		return (reopened.m && (!_Utils_eq(reopened.aO, $elm$core$Maybe$Nothing))) ? _Utils_Tuple2(
			reopened,
			_List_fromArray(
				[
					$author$project$Desktop$Focus(
					A2($author$project$Desktop$key, reopened, target))
				])) : _Utils_Tuple2(reopened, _List_Nil);
	}
};
var $author$project$Pins$encode = function (snapshot) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'revision',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(snapshot.c2))),
				_Utils_Tuple2(
				'identities',
				A2($elm$json$Json$Encode$list, $elm$json$Json$Encode$string, snapshot.fl))
			]));
};
var $author$project$Pins$propose = F3(
	function (request, values, model) {
		var _v0 = model.c;
		if (!_v0.$) {
			var snapshot = _v0.a;
			return ((!$author$project$Pins$writable(model)) || ((!$author$project$Pins$valid(values)) || _Utils_eq(values, snapshot.fl))) ? _Utils_Tuple2(model, $elm$core$Maybe$Nothing) : _Utils_Tuple2(
				_Utils_update(
					model,
					{
						ft: 'Saving pin order…',
						ex: $elm$core$Maybe$Just(
							{fl: values, c1: request})
					}),
				$elm$core$Maybe$Just(
					$author$project$Pins$encode(
						_Utils_update(
							snapshot,
							{fl: values}))));
		} else {
			return _Utils_Tuple2(model, $elm$core$Maybe$Nothing);
		}
	});
var $author$project$Desktop$savePins = F2(
	function (values, model) {
		var _v0 = _Utils_Tuple2(
			model.a.b.dk,
			$author$project$UInt64$next(model.c1));
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
			var _v1 = A3($author$project$Pins$propose, request, values, model.R);
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
							R: _Utils_update(
								pins,
								{ft: 'Pin order is too large to save.', ex: $elm$core$Maybe$Nothing})
						}),
					_List_Nil) : _Utils_Tuple2(
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{R: pins, c1: request})),
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
				{fN: region})) : $elm$core$Maybe$Nothing;
	});
var $author$project$Files$propose = F3(
	function (request, value, model) {
		return (_Utils_eq(request, $author$project$UInt64$zero) || (!A2($author$project$Files$supported, value, model))) ? _Utils_Tuple2(model, $elm$core$Maybe$Nothing) : _Utils_Tuple2(
			_Utils_update(
				model,
				{
					ft: 'Files: waiting for the requested location…',
					ex: $elm$core$Maybe$Just(
						{aa: value, c1: request}),
					ca: A2(
						$elm$core$List$take,
						128,
						A2($elm$core$List$cons, value, model.ca))
				}),
			$elm$core$Maybe$Just(
				$elm$json$Json$Encode$object(
					_List_fromArray(
						[
							_Utils_Tuple2(
							'service',
							$elm$json$Json$Encode$string(
								$author$project$UInt64$string(value.c7))),
							_Utils_Tuple2(
							'revision',
							$elm$json$Json$Encode$string(
								$author$project$UInt64$string(value.c2))),
							_Utils_Tuple2(
							'target',
							$elm$json$Json$Encode$string(value.fR))
						]))));
	});
var $author$project$Desktop$sendFiles = F2(
	function (target, model) {
		if (!_Utils_eq(model.aW, $elm$core$Maybe$Nothing)) {
			return _Utils_Tuple2(model, _List_Nil);
		} else {
			var _v0 = _Utils_Tuple2(
				model.a.b.dk,
				$author$project$UInt64$next(model.c1));
			if ((!_v0.a.$) && (!_v0.b.$)) {
				var binding = _v0.a.a;
				var request = _v0.b.a;
				var _v1 = A3($author$project$Files$propose, request, target, model.T);
				var files = _v1.a;
				var proposal = _v1.b;
				if (proposal.$ === 1) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var value = proposal.a;
					return _Utils_Tuple2(
						$author$project$Desktop$advance(
							_Utils_update(
								model,
								{T: files, p: false, B: false, o: $elm$core$Maybe$Nothing, w: false, c1: request})),
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
											$elm$json$Json$Encode$string('files-open')),
											_Utils_Tuple2(
											'binding',
											$author$project$Binding$encode(binding)),
											_Utils_Tuple2(
											'requestId',
											$elm$json$Json$Encode$string(
												$author$project$UInt64$string(request))),
											_Utils_Tuple2('intent', value)
										])))
							]));
				}
			} else {
				return _Utils_Tuple2(model, _List_Nil);
			}
		}
	});
var $author$project$SystemMenu$encode = function (value) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'service',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(value.c7))),
				_Utils_Tuple2(
				'revision',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(value.c2))),
				_Utils_Tuple2(
				'operation',
				$elm$json$Json$Encode$string(
					$author$project$SystemMenu$code(value.bh))),
				_Utils_Tuple2(
				'value',
				$elm$json$Json$Encode$int(value.Y))
			]));
};
var $author$project$SystemMenu$propose = F3(
	function (request, value, model) {
		return ((!_Utils_eq(model.ex, $elm$core$Maybe$Nothing)) || (!A2($author$project$SystemMenu$supported, value, model))) ? _Utils_Tuple2(model, $elm$core$Maybe$Nothing) : _Utils_Tuple2(
			_Utils_update(
				model,
				{
					ft: $author$project$SystemMenu$name(value.bh) + ': waiting for native result…',
					ex: $elm$core$Maybe$Just(
						{aa: value, c1: request}),
					ca: A2(
						$elm$core$List$take,
						128,
						A2($elm$core$List$cons, value, model.ca))
				}),
			$elm$core$Maybe$Just(
				$author$project$SystemMenu$encode(value)));
	});
var $author$project$Desktop$sendSystemChange = F2(
	function (intent, model) {
		var _v0 = _Utils_Tuple2(
			model.a.b.dk,
			$author$project$UInt64$next(model.c1));
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var binding = _v0.a.a;
			var request = _v0.b.a;
			var _v1 = A3($author$project$SystemMenu$propose, request, intent, model.ak);
			var menu = _v1.a;
			var proposal = _v1.b;
			if (proposal.$ === 1) {
				return _Utils_Tuple2(model, _List_Nil);
			} else {
				var value = proposal.a;
				return _Utils_Tuple2(
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{c1: request, ak: menu, s: $elm$core$Maybe$Nothing})),
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
										$elm$json$Json$Encode$string('system-menu-effect')),
										_Utils_Tuple2(
										'binding',
										$author$project$Binding$encode(binding)),
										_Utils_Tuple2(
										'requestId',
										$elm$json$Json$Encode$string(
											$author$project$UInt64$string(request))),
										_Utils_Tuple2('intent', value)
									])))
						]));
			}
		} else {
			return _Utils_Tuple2(model, _List_Nil);
		}
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
			var _v3 = model.j;
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
			model.c,
			$author$project$UInt64$next(model.c1));
		if ((!_v1.a.$) && (!_v1.b.$)) {
			var snapshot = _v1.a.a;
			var request = _v1.b.a;
			var scope = $author$project$Catalog$scope(snapshot);
			if (ready && (_Utils_eq(
				model.be,
				$elm$core$Maybe$Just(host)) && (_Utils_eq(model.c2, revision) && (_Utils_eq(lifetime, scope.fp) && _Utils_eq(generation, scope.fh))))) {
				var _v2 = A3($author$project$Catalog$intent, request, entry, snapshot);
				if (!_v2.$) {
					var wire = _v2.a;
					return _Utils_Tuple2(
						$author$project$Launch$advance(
							_Utils_update(
								model,
								{
									j: A2(
										$author$project$Launch$Pending,
										host,
										{
											d2: $author$project$Catalog$id(entry),
											fh: generation,
											fp: lifetime,
											c1: request
										}),
									c1: request
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
var $author$project$Motion$request = function (pending) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'protocolVersion',
				$elm$json$Json$Encode$int(3)),
				_Utils_Tuple2(
				'kind',
				$elm$json$Json$Encode$string('motion-profile-set')),
				_Utils_Tuple2(
				'binding',
				$author$project$Binding$encode(pending.dk)),
				_Utils_Tuple2(
				'requestId',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(pending.c1))),
				_Utils_Tuple2(
				'profile',
				$elm$json$Json$Encode$string(
					$author$project$Motion$name(pending.aC)))
			]));
};
var $author$project$Motion$propose = F3(
	function (binding, request_, model) {
		if ((!_Utils_eq(model.ex, $elm$core$Maybe$Nothing)) || (_Utils_eq(request_, $author$project$UInt64$zero) || (_Utils_eq(model.a1.c, $elm$core$Maybe$Nothing) || ((_Utils_eq(model.bF, $elm$core$Maybe$Nothing) && (!$author$project$MotionPreferences$selected(model.a1))) || A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (a) {
					return _Utils_eq(a.dk, binding) && _Utils_eq(
						a.aC,
						$author$project$Motion$desired(model));
				},
				model.bT)))))) {
			return _Utils_Tuple2(model, $elm$core$Maybe$Nothing);
		} else {
			var pending = {
				dk: binding,
				aC: $author$project$Motion$desired(model),
				c1: request_
			};
			return _Utils_Tuple2(
				_Utils_update(
					model,
					{
						ex: $elm$core$Maybe$Just(pending)
					}),
				$elm$core$Maybe$Just(
					$author$project$Motion$request(pending)));
		}
	});
var $author$project$Desktop$syncMotion = function (model) {
	if ((!model.a.b.j) || (model.a.b.j === 3)) {
		return _Utils_Tuple2(model, _List_Nil);
	} else {
		var _v0 = _Utils_Tuple2(
			model.a.b.dk,
			$author$project$UInt64$next(model.c1));
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var binding = _v0.a.a;
			var request = _v0.b.a;
			var _v1 = A3($author$project$Motion$propose, binding, request, model.I);
			var motion = _v1.a;
			var command = _v1.b;
			if (command.$ === 1) {
				return _Utils_Tuple2(model, _List_Nil);
			} else {
				var wire = command.a;
				return _Utils_Tuple2(
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{I: motion, c1: request})),
					_List_fromArray(
						[
							$author$project$Desktop$Send(wire)
						]));
			}
		} else {
			return _Utils_Tuple2(model, _List_Nil);
		}
	}
};
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
var $author$project$OverviewRecovery$Issued = F2(
	function (a, b) {
		return {$: 2, a: a, b: b};
	});
var $author$project$OverviewRecovery$issue = F3(
	function (read, sent, model) {
		if (model.$ === 1) {
			var origin = model.a;
			var expected = model.b;
			if (!_Utils_eq(read, expected)) {
				return model;
			} else {
				if (!sent.$) {
					var _v2 = sent.a;
					var binding = _v2.a;
					var intent = _v2.b;
					return (_Utils_eq(binding, origin.dk) && (_Utils_eq(intent.aq, origin.r) && A2(
						$elm$core$List$member,
						intent.bh,
						_List_fromArray(
							[$author$project$Effects$Activate, $author$project$Effects$Restore])))) ? A2($author$project$OverviewRecovery$Issued, origin, intent) : $author$project$OverviewRecovery$Idle;
				} else {
					return $author$project$OverviewRecovery$Idle;
				}
			}
		} else {
			return model;
		}
	});
var $author$project$Desktop$trackOverviewChoice = F3(
	function (_v0, effects, model) {
		var read = _v0.b;
		var sent = $elm$core$List$head(
			A2(
				$elm$core$List$filterMap,
				function (effect) {
					if ((!effect.$) && (!effect.a.$)) {
						var wire = effect.a.a;
						return (!_Utils_eq(
							A2(
								$elm$json$Json$Decode$decodeValue,
								A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
								wire),
							$elm$core$Result$Ok('window-effect'))) ? $elm$core$Maybe$Nothing : $elm$core$Result$toMaybe(
							A2(
								$elm$json$Json$Decode$decodeValue,
								A3(
									$elm$json$Json$Decode$map2,
									$elm$core$Tuple$pair,
									A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
									A2($elm$json$Json$Decode$field, 'intent', $author$project$Effects$intentDecoder)),
								wire));
					} else {
						return $elm$core$Maybe$Nothing;
					}
				},
				effects));
		return _Utils_update(
			model,
			{
				aN: A3($author$project$OverviewRecovery$issue, read, sent, model.aN)
			});
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
									$author$project$MenuBridge$menuSnapshot(model.a.h).aI,
									$author$project$MenuBridge$currentProvider(model.a.h));
								if ((!_v3.a.$) && (!_v3.b.$)) {
									var menu = _v3.a.a;
									var provider = _v3.b.a;
									return _Utils_eq(menu.cl, menuId) && (_Utils_eq(menu.dk, binding) && (_Utils_eq(
										A2(
											$elm$core$Maybe$map,
											function ($) {
												return $.e3;
											},
											$elm$core$List$head(
												A2($elm$core$List$drop, index, menu.fo))),
										$elm$core$Maybe$Just($author$project$Menu$Minimize)) && A2(
										$elm$core$List$any,
										function (family) {
											return _Utils_eq(
												family.r,
												$author$project$Provider$incarnation(provider)) && (!family.bt);
										},
										A2(
											$elm$core$List$concatMap,
											function ($) {
												return $.aG;
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
									{u: $elm$core$Maybe$Nothing}));
							var next = _v2.a;
							var effects = _v2.b;
							var admitted = _Utils_eq(
								$author$project$MenuBridge$preparedSnapshot(model.a.h),
								$elm$core$Maybe$Nothing) && (!_Utils_eq(
								$author$project$MenuBridge$preparedSnapshot(next.a.h),
								$elm$core$Maybe$Nothing));
							return (inactiveMinimize && admitted) ? _Utils_Tuple2(
								_Utils_update(
									next,
									{
										u: (model.bI === 1) ? model.H : $elm$core$Maybe$Nothing
									}),
								effects) : _Utils_Tuple2(next, effects);
						case 5:
							var menuId = message.a.a;
							var _v4 = _Utils_Tuple2(
								$author$project$MenuBridge$menuSnapshot(model.a.h).aI,
								model.H);
							if ((!_v4.a.$) && (!_v4.b.$)) {
								var menu = _v4.a.a;
								var origin = _v4.b.a;
								if (!_Utils_eq(menu.cl, menuId)) {
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
												H: $elm$core$Maybe$Nothing,
												u: (model.bI === 1) ? $elm$core$Maybe$Just(origin) : $elm$core$Maybe$Nothing
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
					var _v7 = _Utils_Tuple2(model.a.J, model.a.b.dk);
					if ((!_v7.a.$) && (!_v7.b.$)) {
						var picker = _v7.a.a;
						var binding = _v7.b.a;
						var _v8 = A2($author$project$Desktop$windowBase, message, model);
						var closed = _v8.a;
						var effects = _v8.b;
						if ((!_Utils_eq(closed.a.J, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(picker.c5, scope)) || (!_Utils_eq(picker.fh, generation)))) {
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
										u: (model.bI === 1) ? $elm$core$Maybe$Just(
											{
												dk: binding,
												bx: $author$project$Desktop$TaskbarGroup(picker.a_),
												y: A2(
													$elm$core$Maybe$map,
													A2(
														$elm$core$Basics$composeR,
														function ($) {
															return $.P;
														},
														function ($) {
															return $.y;
														}),
													model.a.b._.as)
											}) : $elm$core$Maybe$Nothing
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
					var _v11 = _Utils_Tuple3(model.a.J, model.a.b.dk, model.a.b._.as);
					if (((!_v11.a.$) && (!_v11.b.$)) && (!_v11.c.$)) {
						var picker = _v11.a.a;
						var binding = _v11.b.a;
						var observed = _v11.c.a;
						if ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(picker.c5, scope)) || ((!_Utils_eq(picker.fh, generation)) || ((!_Utils_eq(
							$author$project$Shell$capture(model.a.b),
							$elm$core$Maybe$Just(scope))) || (!$author$project$Shell$available(model.a.b)))))) {
							return _Utils_Tuple2(model, _List_Nil);
						} else {
							var _v12 = $elm$core$List$head(
								A2(
									$elm$core$List$filter,
									function (family) {
										return _Utils_eq(family.r, root) && family.dj;
									},
									A2(
										$elm$core$List$concatMap,
										function ($) {
											return $.aG;
										},
										A2(
											$elm$core$List$filter,
											function (group) {
												return _Utils_eq(group.a_, picker.a_);
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
											G: '',
											a: _Utils_update(
												windows,
												{J: $elm$core$Maybe$Nothing})
										}));
								var next = _v13.a;
								var effects = _v13.b;
								var _v14 = next.a.b.A;
								if (!_v14.$) {
									var request = _v14.a;
									var token = A2($author$project$Desktop$ChoiceToken, binding, request);
									return _Utils_Tuple2(
										_Utils_update(
											next,
											{
												k: $elm$core$Maybe$Just(
													{di: family.di, dk: binding, aV: $elm$core$Maybe$Nothing, y: observed.P.y, bk: $elm$core$Maybe$Nothing, r: root, bp: token, a4: $elm$core$Maybe$Nothing})
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
						function (_v34) {
							var kind = _v34.a;
							var request = _v34.b;
							return (kind === 'action-projection') && _Utils_eq(
								model.a.b.A,
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
					{u: $elm$core$Maybe$Nothing});
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
					return $._;
				},
				updated.a.b.ds)) ? A2(
			$elm$core$Maybe$map,
			A2(
				$elm$core$Basics$composeR,
				function ($) {
					return $.P;
				},
				function ($) {
					return $.y;
				}),
			updated.a.b.ap) : A2(
			$elm$core$Maybe$map,
			A2(
				$elm$core$Basics$composeR,
				function ($) {
					return $.P;
				},
				function ($) {
					return $.y;
				}),
			updated.a.b._.as);
		var matchingGeometry = function () {
			if ((!message.$) && (message.a.$ === 3)) {
				var raw = message.a.a;
				return A2(
					$elm$core$Result$withDefault,
					false,
					A2(
						$elm$core$Result$map,
						function (_v31) {
							var kind = _v31.a;
							var request = _v31.b;
							return (kind === 'geometry-facts') && (_Utils_eq(
								model.a.b.eb,
								$elm$core$Maybe$Just(request)) && (_Utils_eq(
								A2(
									$elm$core$Maybe$map,
									function ($) {
										return $.c1;
									},
									updated.a.b.ap),
								$elm$core$Maybe$Just(request)) && (!_Utils_eq(updated.a.b.ap, model.a.b.ap))));
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
			var _v17 = updated.u;
			if (!_v17.$) {
				var target = _v17.a;
				var blocked = function () {
					var _v20 = target.bx;
					if (!_v20.$) {
						var groupKey = _v20.a;
						return A2(
							$elm$core$List$any,
							function (family) {
								return A3($author$project$MenuBridge$blockedFor, family.r, updated.a.b, updated.a.h);
							},
							A2(
								$elm$core$List$concatMap,
								function ($) {
									return $.aG;
								},
								A2(
									$elm$core$List$filter,
									function (group) {
										return _Utils_eq(group.a_, groupKey);
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
						{u: $elm$core$Maybe$Nothing});
					var focus = function () {
						var _v19 = target.bx;
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
						var _v18 = target.bx;
						if (!_v18.$) {
							var groupKey = _v18.a;
							return A2(
								$elm$core$List$any,
								function (group) {
									return _Utils_eq(group.a_, groupKey) && A2(
										$elm$core$List$any,
										function ($) {
											return $.dj;
										},
										group.aG);
								},
								$author$project$TaskbarShell$groups(retired.a));
						} else {
							return _Utils_eq(retired.k, $elm$core$Maybe$Nothing);
						}
					}();
					return (retired.q || (retired.m || ((!_Utils_eq(retired.a.J, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(
						$author$project$MenuBridge$menuSnapshot(retired.a.h).aI,
						$elm$core$Maybe$Nothing)) || ((!_Utils_eq(
						retired.a.b.dk,
						$elm$core$Maybe$Just(target.dk))) || (_Utils_eq(target.y, $elm$core$Maybe$Nothing) || ((!_Utils_eq(
						A2(
							$elm$core$Maybe$map,
							A2(
								$elm$core$Basics$composeR,
								function ($) {
									return $.P;
								},
								function ($) {
									return $.y;
								}),
							retired.a.b._.as),
						target.y)) || ((!_Utils_eq(geometryOutput, target.y)) || (!exists))))))))) ? _Utils_Tuple2(retired, ordinaryEffects) : _Utils_Tuple2(
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
		var _v21 = next.k;
		if (!_v21.$) {
			var pending = _v21.a;
			if ((!matchingObservation) || ((!$author$project$Shell$available(next.a.b)) || (((!_Utils_eq(pending.a4, $elm$core$Maybe$Nothing)) && (!matchingGeometry)) || (((!_Utils_eq(pending.bk, $elm$core$Maybe$Nothing)) || (!_Utils_eq(pending.a4, $elm$core$Maybe$Nothing))) && A2(
				$elm$core$Maybe$withDefault,
				true,
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.e6;
					},
					next.a.b.ap)))))) {
				return _Utils_Tuple2(next, effects);
			} else {
				var retired = _Utils_update(
					next,
					{k: $elm$core$Maybe$Nothing, G: 'The window changed. Choose again.'});
				var output = A2(
					$elm$core$Maybe$map,
					A2(
						$elm$core$Basics$composeR,
						function ($) {
							return $.P;
						},
						function ($) {
							return $.y;
						}),
					next.a.b._.as);
				var family = $elm$core$List$head(
					A2(
						$elm$core$List$filter,
						function (item) {
							return _Utils_eq(item.r, pending.r) && (_Utils_eq(item.di, pending.di) && item.dj);
						},
						A2(
							$elm$core$List$concatMap,
							function ($) {
								return $.aG;
							},
							$author$project$TaskbarShell$groups(next.a))));
				if ((!_Utils_eq(
					next.a.b.dk,
					$elm$core$Maybe$Just(pending.dk))) || ((!_Utils_eq(
					output,
					$elm$core$Maybe$Just(pending.y))) || (!_Utils_eq(
					geometryOutput,
					$elm$core$Maybe$Just(pending.y))))) {
					return _Utils_Tuple2(retired, effects);
				} else {
					var _v22 = _Utils_Tuple2(
						$author$project$Shell$capture(next.a.b),
						family);
					if ((!_v22.a.$) && (!_v22.b.$)) {
						var scope = _v22.a.a;
						var selected = _v22.b.a;
						if (!_Utils_eq(pending.a4, $elm$core$Maybe$Nothing)) {
							var _v23 = _Utils_Tuple3(
								pending.a4,
								next.a.b.ap,
								$author$project$Shell$captureGeometry(next.a.b));
							if (((!_v23.a.$) && (!_v23.b.$)) && (!_v23.c.$)) {
								var proposed = _v23.a.a;
								var geometry = _v23.b.a;
								var stamp = _v23.c.a;
								if (!A3($author$project$Transfer$matches, geometry, pending.r, proposed)) {
									return _Utils_Tuple2(
										_Utils_update(
											retired,
											{G: 'Window workspace changed. Choose again.'}),
										effects);
								} else {
									var _v24 = A2(
										$author$project$Desktop$windowBase,
										$author$project$TaskbarShell$Native(
											A3(
												$author$project$Shell$Act,
												stamp,
												$author$project$Effects$TransferWorkspace(proposed),
												pending.r)),
										_Utils_update(
											retired,
											{G: ''}));
									var applied = _v24.a;
									var commands = _v24.b;
									return _Utils_Tuple2(
										applied,
										_Utils_ap(effects, commands));
								}
							} else {
								return _Utils_Tuple2(retired, effects);
							}
						} else {
							var _v25 = pending.bk;
							if (!_v25.$) {
								var proposed = _v25.a;
								var _v26 = _Utils_Tuple2(
									next.a.b.ap,
									$author$project$Shell$captureGeometry(next.a.b));
								if ((!_v26.a.$) && (!_v26.b.$)) {
									var geometry = _v26.a.a;
									var stamp = _v26.b.a;
									var current = _Utils_update(
										proposed,
										{P: geometry.P});
									if (!A3($author$project$Snap$matches, geometry, pending.r, current)) {
										return _Utils_Tuple2(
											_Utils_update(
												retired,
												{G: 'Output or window changed. Open snapping again.'}),
											effects);
									} else {
										var _v27 = A2(
											$author$project$Desktop$windowBase,
											$author$project$TaskbarShell$Native(
												A3(
													$author$project$Shell$Act,
													stamp,
													$author$project$Effects$SnapPlacement(current),
													pending.r)),
											_Utils_update(
												retired,
												{G: ''}));
										var applied = _v27.a;
										var commands = _v27.b;
										return _Utils_Tuple2(
											applied,
											_Utils_ap(effects, commands));
									}
								} else {
									return _Utils_Tuple2(retired, effects);
								}
							} else {
								var _v28 = $author$project$Taskbar$selection(selected);
								if (_v28.$ === 2) {
									var operation = _v28.a;
									var root = _v28.b;
									var _v29 = A2(
										$author$project$Desktop$windowBase,
										$author$project$TaskbarShell$Native(
											A3($author$project$Shell$Act, scope, operation, root)),
										_Utils_update(
											retired,
											{G: ''}));
									var applied = _v29.a;
									var commands = _v29.b;
									return _Utils_Tuple2(
										A3($author$project$Desktop$trackOverviewChoice, pending.bp, commands, applied),
										_Utils_ap(
											effects,
											A3($author$project$Desktop$fenceSwitcherSelection, pending.aV, pending.dk, commands)));
								} else {
									return _Utils_Tuple2(retired, effects);
								}
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
		update:
		while (true) {
			if (!message.$) {
				var origin = message.a;
				var inner = message.b;
				var $temp$message = inner,
					$temp$model = _Utils_update(
					model,
					{bI: origin});
				message = $temp$message;
				model = $temp$model;
				continue update;
			} else {
				return A2($author$project$Desktop$updateOrdinary, message, model);
			}
		}
	});
var $author$project$Desktop$updateAvailable = F2(
	function (message, model) {
		switch (message.$) {
			case 3:
				var stamp = message.a;
				var root = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!$author$project$Shell$available(model.a.b)) || A3($author$project$MenuBridge$blockedFor, root, model.a.b, model.a.h))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v4 = A2(
						$elm$core$Maybe$andThen,
						function (geometry) {
							return A2($author$project$Snap$open, geometry, root);
						},
						model.a.b.ap);
					if (_v4.$ === 1) {
						return _Utils_Tuple2(model, _List_Nil);
					} else {
						var choice = _v4.a;
						var windows = model.a;
						return _Utils_Tuple2(
							$author$project$Desktop$advance(
								$author$project$Desktop$retireSwitcher(
									_Utils_update(
										model,
										{
											k: $elm$core$Maybe$Nothing,
											A: $elm$core$Maybe$Nothing,
											p: false,
											B: false,
											o: $elm$core$Maybe$Nothing,
											w: false,
											H: $elm$core$Maybe$Nothing,
											t: false,
											D: false,
											q: false,
											m: false,
											u: $elm$core$Maybe$Nothing,
											n: false,
											L: false,
											x: $elm$core$Maybe$Just(choice),
											s: $elm$core$Maybe$Nothing,
											v: false,
											E: false,
											a: _Utils_update(
												windows,
												{
													h: $author$project$MenuBridge$retireChoices(windows.h),
													J: $elm$core$Maybe$Nothing
												})
										}))),
							_List_Nil);
					}
				}
			case 4:
				var stamp = message.a;
				var region = message.b;
				if (!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v5 = _Utils_Tuple2(model.a.b.ap, model.x);
					if ((!_v5.a.$) && (!_v5.b.$)) {
						var geometry = _v5.a.a;
						var choice = _v5.b.a;
						return _Utils_Tuple2(
							_Utils_update(
								model,
								{
									x: A3($author$project$Snap$select, geometry, region, choice)
								}),
							_List_Nil);
					} else {
						return _Utils_Tuple2(model, _List_Nil);
					}
				}
			case 5:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) || ((!$author$project$Shell$available(model.a.b)) || (!A2(
					$elm$core$Maybe$withDefault,
					false,
					A2(
						$elm$core$Maybe$map,
						function (caps) {
							return A2($elm$core$List$member, 'snap', caps.ev);
						},
						model.a.b.ds)))))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v6 = _Utils_Tuple2(model.x, model.a.b.ap);
					if ((!_v6.a.$) && (!_v6.b.$)) {
						var choice = _v6.a.a;
						var geometry = _v6.b.a;
						if (!A2($author$project$Snap$valid, geometry, choice)) {
							return _Utils_Tuple2(model, _List_Nil);
						} else {
							var _v7 = _Utils_Tuple2(
								$author$project$Snap$proposal(choice),
								$elm$core$List$head(
									A2(
										$elm$core$List$filter,
										function (family) {
											return _Utils_eq(family.r, choice.fR) && family.dj;
										},
										A2(
											$elm$core$List$concatMap,
											function ($) {
												return $.aG;
											},
											$author$project$TaskbarShell$groups(model.a)))));
							if ((!_v7.a.$) && (!_v7.b.$)) {
								var proposed = _v7.a.a;
								var family = _v7.b.a;
								var _v8 = A2(
									$author$project$Desktop$chooseFamily,
									family,
									_Utils_update(
										model,
										{x: $elm$core$Maybe$Nothing}));
								var next = _v8.a;
								var effects = _v8.b;
								return _Utils_Tuple2(
									_Utils_update(
										next,
										{
											k: A2(
												$elm$core$Maybe$map,
												function (pending) {
													return _Utils_update(
														pending,
														{
															bk: $elm$core$Maybe$Just(proposed)
														});
												},
												next.k)
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
			case 6:
				var stamp = message.a;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || _Utils_eq(model.x, $elm$core$Maybe$Nothing)) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{x: $elm$core$Maybe$Nothing})),
					_List_Nil);
			case 7:
				return _Utils_eq(model.x, $elm$core$Maybe$Nothing) ? _Utils_Tuple2(model, _List_Nil) : A2(
					$author$project$Desktop$windowBase,
					$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{G: 'Output changed. Open snapping again.', x: $elm$core$Maybe$Nothing})));
			case 67:
				var token = message.a;
				if (!_Utils_eq(
					A2(
						$elm$core$Maybe$map,
						function ($) {
							return $.bp;
						},
						model.k),
					$elm$core$Maybe$Just(token))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v9 = token;
					var request = _v9.b;
					return _Utils_Tuple2(
						_Utils_update(
							model,
							{
								k: $elm$core$Maybe$Nothing,
								G: 'Window information took too long. Refresh windows, then choose again.',
								aN: A2($author$project$OverviewRecovery$cancelChoice, request, model.aN)
							}),
						_List_Nil);
				}
			case 68:
				return ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) || $elm$core$String$isEmpty(model.G)) ? _Utils_Tuple2(model, _List_Nil) : A2(
					$author$project$Desktop$windowBase,
					$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
					_Utils_update(
						model,
						{G: ''}));
			case 9:
				var snapshot = message.a;
				var allowed = message.b;
				if ((!model.a.b.j) || (model.a.b.j === 3)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v10 = A3($author$project$Shortcuts$receive, model.a.b.dk, snapshot, model.b8);
					var shortcuts = _v10.a;
					var route = _v10.b;
					var failure = _v10.c;
					var notice = ((!_Utils_eq(route, $elm$core$Maybe$Nothing)) && (!allowed)) ? $elm$core$Maybe$Just('Shell shortcut output is unavailable. Press the shortcut again.') : failure;
					var priorNotice = ((!_Utils_eq(route, $elm$core$Maybe$Nothing)) && (allowed && A2(
						$elm$core$List$member,
						model.G,
						_List_fromArray(
							['Shell shortcut output is unavailable. Press the shortcut again.', 'Shell shortcut unavailable while input is blocked.', 'Shortcut history expired. Press the shortcut again.'])))) ? '' : model.G;
					var next = _Utils_update(
						model,
						{
							G: A2($elm$core$Maybe$withDefault, priorNotice, notice),
							bI: 1,
							b8: shortcuts
						});
					var _v11 = _Utils_Tuple2(
						allowed ? route : $elm$core$Maybe$Nothing,
						$author$project$Desktop$capture(next));
					if ((!_v11.a.$) && (!_v11.b.$)) {
						switch (_v11.a.a) {
							case 0:
								var _v12 = _v11.a.a;
								var stamp = _v11.b.a;
								return A2(
									$author$project$Desktop$update,
									$author$project$Desktop$OpenApplications(stamp),
									next);
							case 1:
								var _v13 = _v11.a.a;
								var stamp = _v11.b.a;
								return A2(
									$author$project$Desktop$update,
									$author$project$Desktop$OpenSystemMenu(stamp),
									next);
							default:
								var _v14 = _v11.a.a;
								var stamp = _v11.b.a;
								return A2(
									$author$project$Desktop$update,
									$author$project$Desktop$OpenNotifications(stamp),
									next);
						}
					} else {
						return _Utils_Tuple2(next, _List_Nil);
					}
				}
			case 10:
				var scope = message.a;
				if (_Utils_eq(scope, model.bj)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v15 = function () {
						var _v16 = $author$project$MenuBridge$currentProvider(model.a.h);
						if (_v16.$ === 1) {
							return _Utils_Tuple2(model, _List_Nil);
						} else {
							var provider = _v16.a;
							return A2(
								$author$project$Desktop$windowBase,
								$author$project$TaskbarShell$MenuEvent(
									$author$project$Menu$Invalidate(
										$author$project$Provider$getBinding(provider))),
								model);
						}
					}();
					var retired = _v15.a;
					var effects = _v15.b;
					return _Utils_Tuple2(
						$author$project$Desktop$retireSwitcher(
							_Utils_update(
								retired,
								{H: $elm$core$Maybe$Nothing, b1: false, bj: scope, u: $elm$core$Maybe$Nothing, x: $elm$core$Maybe$Nothing})),
						effects);
				}
			case 8:
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
									{dC: output, dI: provider});
							}),
						A2($elm$json$Json$Decode$field, 'surfaceProtocol', $elm$json$Json$Decode$int),
						A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
						A2($elm$json$Json$Decode$field, 'outputId', positive),
						A2($elm$json$Json$Decode$field, 'providerId', positive)));
				var _v17 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
				if (((!_v17.$) && (_v17.a.a === 2)) && (_v17.a.b === 'surface-owner')) {
					var _v18 = _v17.a;
					var owner = _v18.c;
					if (model.b1) {
						return _Utils_Tuple2(model, _List_Nil);
					} else {
						var _v19 = model.bj;
						if (_v19.$ === 1) {
							return _Utils_Tuple2(
								_Utils_update(
									model,
									{
										bj: $elm$core$Maybe$Just(owner)
									}),
								_List_Nil);
						} else {
							var previous = _v19.a;
							if (_Utils_eq(previous, owner)) {
								return _Utils_Tuple2(model, _List_Nil);
							} else {
								var retired = function () {
									var _v20 = $author$project$MenuBridge$currentProvider(model.a.h);
									if (_v20.$ === 1) {
										return model;
									} else {
										var provider = _v20.a;
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
											{H: $elm$core$Maybe$Nothing, b1: true, bj: $elm$core$Maybe$Nothing, u: $elm$core$Maybe$Nothing, x: $elm$core$Maybe$Nothing})),
									_List_Nil);
							}
						}
					}
				} else {
					return _Utils_Tuple2(model, _List_Nil);
				}
			case 2:
				var stamp = message.a;
				var root = message.b;
				if (model.b1 || ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(
					$author$project$MenuBridge$preparedSnapshot(model.a.h),
					$elm$core$Maybe$Nothing)) || ((!_Utils_eq(
					$author$project$Shell$capture(model.a.b),
					$elm$core$Maybe$Just(stamp))) || (!$author$project$Shell$available(model.a.b)))))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v21 = model.a.b._.as;
					if (_v21.$ === 1) {
						return _Utils_Tuple2(model, _List_Nil);
					} else {
						var observed = _v21.a;
						var _v22 = model.bj;
						if (_v22.$ === 1) {
							return _Utils_Tuple2(model, _List_Nil);
						} else {
							var owner = _v22.a;
							var _v23 = A3(
								$author$project$NativeProvider$fromShell,
								{e7: observed.P.c2, dC: owner.dC, dI: owner.dI},
								root,
								model.a.b);
							if (_v23.$ === 1) {
								return _Utils_Tuple2(model, _List_Nil);
							} else {
								var provider = _v23.a;
								var _v24 = A2(
									$author$project$Desktop$windowBase,
									$author$project$TaskbarShell$OpenMenu(provider),
									model);
								var next = _v24.a;
								var effects = _v24.b;
								return _Utils_eq(
									$author$project$MenuBridge$menuSnapshot(next.a.h).aI,
									$author$project$MenuBridge$menuSnapshot(model.a.h).aI) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
									$author$project$Desktop$retireSwitcher(
										_Utils_update(
											next,
											{
												A: $elm$core$Maybe$Nothing,
												p: false,
												B: false,
												o: $elm$core$Maybe$Nothing,
												w: false,
												H: A2(
													$elm$core$Maybe$andThen,
													function (binding) {
														return A2(
															$elm$core$Maybe$map,
															function (group) {
																return {
																	dk: binding,
																	bx: $author$project$Desktop$TaskbarGroup(group.a_),
																	y: $elm$core$Maybe$Just(observed.P.y)
																};
															},
															$elm$core$List$head(
																A2(
																	$elm$core$List$filter,
																	function (group) {
																		return A2(
																			$elm$core$List$any,
																			function (family) {
																				return _Utils_eq(family.r, root);
																			},
																			group.aG);
																	},
																	$author$project$TaskbarShell$groups(model.a))));
													},
													model.a.b.dk),
												t: false,
												D: false,
												q: false,
												m: false,
												u: $elm$core$Maybe$Nothing,
												n: false,
												L: false,
												x: $elm$core$Maybe$Nothing,
												s: $elm$core$Maybe$Nothing,
												v: false,
												E: false
											})),
									effects);
							}
						}
					}
				}
			case 49:
				var stamp = message.a;
				var direction = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) || ((!$author$project$Shell$available(model.a.b)) || (!_Utils_eq(
					$author$project$MenuBridge$preparedSnapshot(model.a.h),
					$elm$core$Maybe$Nothing))))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v25 = $author$project$UInt64$next(
						$author$project$Switcher$generation(model.i));
					if (_v25.$ === 1) {
						return _Utils_Tuple2(
							$author$project$Desktop$retireSwitcher(model),
							_List_Nil);
					} else {
						var generation = _v25.a;
						var base = A2(
							$elm$core$Maybe$withDefault,
							model,
							A2(
								$elm$core$Maybe$map,
								function (menu) {
									return A2(
										$author$project$Desktop$windowBase,
										$author$project$TaskbarShell$MenuEvent(
											$author$project$Menu$Dismiss(menu.cl)),
										model).a;
								},
								$author$project$MenuBridge$menuSnapshot(model.a.h).aI));
						var origin = A2(
							$elm$core$Maybe$andThen,
							function (observed) {
								return A2(
									$elm$core$Maybe$andThen,
									function (root) {
										return A2($author$project$ActionProjection$rootOf, root, observed.eN);
									},
									$author$project$ActionProjection$focused(observed.eN));
							},
							base.a.b._.as);
						var windows = base.a;
						var _v26 = A4($author$project$Switcher$step, generation, 1, direction, base.i);
						var switcher = _v26.a;
						var opened = $author$project$Desktop$advance(
							_Utils_update(
								base,
								{
									A: $elm$core$Maybe$Nothing,
									p: false,
									B: false,
									o: $elm$core$Maybe$Nothing,
									w: false,
									H: $elm$core$Maybe$Nothing,
									ah: $elm$core$Maybe$Nothing,
									t: false,
									D: false,
									q: false,
									m: false,
									u: $elm$core$Maybe$Nothing,
									n: false,
									L: false,
									x: $elm$core$Maybe$Nothing,
									i: switcher,
									aS: $elm$core$Maybe$Nothing,
									cw: origin,
									s: $elm$core$Maybe$Nothing,
									v: false,
									E: false,
									a: _Utils_update(
										windows,
										{J: $elm$core$Maybe$Nothing})
								}));
						var _v27 = A2(
							$author$project$Desktop$windowBase,
							$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
							opened);
						var refreshing = _v27.a;
						var commands = _v27.b;
						var _v28 = $author$project$Desktop$readSwitcherHistory(refreshing);
						var next = _v28.a;
						var history = _v28.b;
						return _Utils_Tuple2(
							next,
							_Utils_ap(commands, history));
					}
				}
			case 50:
				var stamp = message.a;
				var direction = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!$author$project$Desktop$switcherOpen(model))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v29 = (!_Utils_eq(model.ah, $elm$core$Maybe$Nothing)) ? _Utils_Tuple2(
						A2($author$project$Switcher$navigate, direction, model.i),
						$elm$core$Maybe$Nothing) : A4(
						$author$project$Switcher$step,
						$author$project$Switcher$generation(model.i),
						$author$project$Switcher$lastStep(model.i) + 1,
						direction,
						model.i);
					var switcher = _v29.a;
					var chosen = _v29.b;
					var next = $author$project$Desktop$advance(
						_Utils_update(
							model,
							{i: switcher}));
					if (!chosen.$) {
						var family = chosen.a;
						return A2($author$project$Desktop$chooseFamily, family, next);
					} else {
						return _Utils_Tuple2(
							next,
							$author$project$Desktop$switcherFocus(next));
					}
				}
			case 51:
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
							return _Utils_eq(family.r, root);
						},
						$author$project$Switcher$entries(model.i))) {
						return _Utils_Tuple2(model, _List_Nil);
					} else {
						var switcher = A3(
							$author$project$Switcher$choose,
							$author$project$Switcher$generation(model.i),
							root,
							model.i);
						var _v31 = A2(
							$author$project$Switcher$commit,
							$author$project$Switcher$generation(switcher),
							switcher);
						var resolved = _v31.a;
						var selected = _v31.b;
						if (!selected.$) {
							var family = selected.a;
							return A2(
								$author$project$Desktop$chooseFamily,
								family,
								$author$project$Desktop$advance(
									_Utils_update(
										model,
										{i: resolved})));
						} else {
							return _Utils_Tuple2(model, _List_Nil);
						}
					}
				}
			case 52:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!$author$project$Desktop$switcherOpen(model))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v33 = A2(
						$author$project$Switcher$commit,
						$author$project$Switcher$generation(model.i),
						model.i);
					var switcher = _v33.a;
					var selected = _v33.b;
					if (!selected.$) {
						var family = selected.a;
						return A2(
							$author$project$Desktop$chooseFamily,
							family,
							$author$project$Desktop$advance(
								_Utils_update(
									model,
									{i: switcher})));
					} else {
						return _Utils_Tuple2(model, _List_Nil);
					}
				}
			case 53:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!$author$project$Desktop$switcherOpen(model))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var closed = $author$project$Desktop$advance(
						$author$project$Desktop$retireSwitcher(model));
					var _v35 = _Utils_Tuple3(
						model.ah,
						model.a.b.dk,
						$author$project$UInt64$next(model.c1));
					if (((!_v35.a.$) && (!_v35.b.$)) && (!_v35.c.$)) {
						var chord = _v35.a.a;
						var binding = _v35.b.a;
						var request = _v35.c.a;
						var _v36 = A2(
							$author$project$Desktop$windowBase,
							$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
							_Utils_update(
								closed,
								{c1: request}));
						var next = _v36.a;
						var reads = _v36.b;
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
													$author$project$UInt64$string(chord.fh)))
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
				return _Utils_Tuple2(model, _List_Nil);
			case 1:
				var value = message.a;
				var _v37 = A2($author$project$Desktop$window, value, model);
				var next = _v37.a;
				var effects = _v37.b;
				var _v38 = $author$project$Desktop$syncSwitcher(next);
				var synced = _v38.a;
				var commands = _v38.b;
				return ((!_Utils_eq(next.a.J, $elm$core$Maybe$Nothing)) && (!_Utils_eq(next.a.J, model.a.J))) ? _Utils_Tuple2(
					$author$project$Desktop$retireSwitcher(
						_Utils_update(
							next,
							{A: $elm$core$Maybe$Nothing, p: false, B: false, o: $elm$core$Maybe$Nothing, w: false, H: $elm$core$Maybe$Nothing, t: false, D: false, q: false, m: false, u: $elm$core$Maybe$Nothing, n: false, L: false, x: $elm$core$Maybe$Nothing, s: $elm$core$Maybe$Nothing, v: false, E: false})),
					effects) : _Utils_Tuple2(
					synced,
					_Utils_ap(effects, commands));
			case 11:
				var raw = message.a;
				var _v39 = A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
					raw);
				_v39$24:
				while (true) {
					if (!_v39.$) {
						switch (_v39.a) {
							case 'motion-preferences':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'snapshot']),
									A5(
										$elm$json$Json$Decode$map4,
										F4(
											function (_v41, binding, request, snapshot) {
												return {dk: binding, c1: request, c: snapshot};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2(
											$elm$json$Json$Decode$field,
											'snapshot',
											$elm$json$Json$Decode$nullable($author$project$MotionPreferences$decoder))));
								var _v40 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (_v40.$ === 1) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var receipt = _v40.a;
									if ((!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(receipt.dk))) || (!_Utils_eq(
										model.aK,
										$elm$core$Maybe$Just(receipt.c1)))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var motion = model.I;
										var preference = A2($author$project$MotionPreferences$observe, receipt.c, motion.a1);
										return _Utils_Tuple2(
											$author$project$Desktop$advance(
												_Utils_update(
													model,
													{
														F: A7(
															$author$project$AdapterNotice$failedRead,
															6,
															receipt.dk,
															receipt.c1,
															$elm$core$Maybe$Nothing,
															$elm$core$Maybe$Nothing,
															_Utils_eq(receipt.c, $elm$core$Maybe$Nothing),
															model.F),
														I: _Utils_update(
															motion,
															{a1: preference}),
														aK: $elm$core$Maybe$Nothing
													})),
											_List_Nil);
									}
								}
							case 'motion-preferences-outcome':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'status', 'snapshot']),
									A6(
										$elm$json$Json$Decode$map5,
										F5(
											function (_v43, binding, request, status, snapshot) {
												return {dk: binding, c1: request, c: snapshot, W: status};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string),
										A2(
											$elm$json$Json$Decode$field,
											'snapshot',
											$elm$json$Json$Decode$nullable($author$project$MotionPreferences$decoder))));
								var _v42 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (_v42.$ === 1) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var receipt = _v42.a;
									if (!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(receipt.dk))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var motion = model.I;
										var preference = A4($author$project$MotionPreferences$receive, receipt.c1, receipt.W, receipt.c, motion.a1);
										return _Utils_eq(preference, motion.a1) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
											$author$project$Desktop$advance(
												_Utils_update(
													model,
													{
														I: _Utils_update(
															motion,
															{a1: preference})
													})),
											_List_Nil);
									}
								}
							case 'host-motion-preference':
								var _v44 = A2($elm$json$Json$Decode$decodeValue, $author$project$Motion$decoder, raw);
								if (_v44.$ === 1) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var observation = _v44.a;
									var motion = A2($author$project$Motion$observe, observation, model.I);
									return _Utils_eq(motion, model.I) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
										$author$project$Desktop$advance(
											_Utils_update(
												model,
												{I: motion})),
										_List_Nil);
								}
							case 'motion-profile':
								var _v45 = A2($elm$json$Json$Decode$decodeValue, $author$project$Motion$receiptDecoder, raw);
								if (_v45.$ === 1) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var receipt = _v45.a;
									var motion = A3($author$project$Motion$receive, model.a.b.dk, receipt, model.I);
									return _Utils_eq(motion, model.I) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
										$author$project$Desktop$advance(
											_Utils_update(
												model,
												{I: motion})),
										_List_Nil);
								}
							case 'pointer-ownership':
								var _v46 = A2($elm$json$Json$Decode$decodeValue, $author$project$PointerOwnership$decoder, raw);
								if (_v46.$ === 1) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var snapshot = _v46.a;
									var pointer = A3($author$project$PointerOwnership$receive, model.a.b.dk, snapshot, model.bH);
									var next = _Utils_update(
										model,
										{bH: pointer});
									if (_Utils_eq(pointer, model.bH)) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										if (!A2($author$project$PointerOwnership$blocked, model.a.b.dk, pointer)) {
											return _Utils_Tuple2(next, _List_Nil);
										} else {
											var windows = next.a;
											var retired = $author$project$Desktop$advance(
												$author$project$Desktop$retireSwitcher(
													_Utils_update(
														next,
														{
															k: $elm$core$Maybe$Nothing,
															p: false,
															B: false,
															o: $elm$core$Maybe$Nothing,
															w: false,
															H: $elm$core$Maybe$Nothing,
															t: false,
															D: false,
															q: false,
															m: false,
															u: $elm$core$Maybe$Nothing,
															n: false,
															L: false,
															x: $elm$core$Maybe$Nothing,
															s: $elm$core$Maybe$Nothing,
															v: false,
															E: false,
															a: _Utils_update(
																windows,
																{
																	h: $author$project$MenuBridge$retireChoices(windows.h),
																	J: $elm$core$Maybe$Nothing
																})
														})));
											return _Utils_Tuple2(retired, _List_Nil);
										}
									}
								}
							case 'shell-shortcuts':
								var _v47 = A2($elm$json$Json$Decode$decodeValue, $author$project$Shortcuts$decoder, raw);
								if (_v47.$ === 1) {
									return _Utils_Tuple2(model, _List_Nil);
								} else {
									var snapshot = _v47.a;
									return A2(
										$author$project$Desktop$update,
										A2($author$project$Desktop$ScopedShortcut, snapshot, true),
										model);
								}
							case 'switcher-journal':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'chord']),
									A5(
										$elm$json$Json$Decode$map4,
										F4(
											function (_v49, binding, request, chord) {
												return {dk: binding, aV: chord, c1: request};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'chord', $author$project$Desktop$nativeChordDecoder)));
								var _v48 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v48.$) {
									var receipt = _v48.a;
									return ((!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(receipt.dk))) || ((!model.a.b.j) || (model.a.b.j === 3))) ? _Utils_Tuple2(model, _List_Nil) : A2($author$project$Desktop$receiveChord, receipt.aV, model);
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
												return {fe: epoch, fp: lifetime, y: output, c2: revision};
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
											function (_v51, binding, request, scope, rows) {
												return {dk: binding, P: scope, c1: request, aP: rows};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', positive),
										A2($elm$json$Json$Decode$field, 'context', context),
										A2($elm$json$Json$Decode$field, 'roots', roots)));
								var _v50 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v50.$) {
									var receipt = _v50.a;
									return ((!$author$project$Desktop$switcherOpen(model)) || ((!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(receipt.dk))) || (!_Utils_eq(
										model.aR,
										$elm$core$Maybe$Just(receipt.c1))))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Desktop$syncSwitcher(
										_Utils_update(
											model,
											{
												aR: $elm$core$Maybe$Nothing,
												aS: $elm$core$Maybe$Just(
													{P: receipt.P, aP: receipt.aP})
											}));
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'jump-list-snapshot':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'snapshot']),
									A5(
										$elm$json$Json$Decode$map4,
										F4(
											function (_v53, binding, request, snapshot) {
												return {dk: binding, c1: request, c: snapshot};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'snapshot', $author$project$JumpList$decoder)));
								var _v52 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v52.$) {
									var result = _v52.a;
									if ((!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(result.dk))) || ((!_Utils_eq(
										model.aZ,
										$elm$core$Maybe$Just(result.c1))) || ((!_Utils_eq(
										model.o,
										$elm$core$Maybe$Just(result.c.d2))) || (!model.a.b.j)))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var reconciled = A2($author$project$JumpList$reconcile, result.c, model.ar);
										var failed = (!result.c.dj) && _Utils_eq(
											reconciled.c,
											$elm$core$Maybe$Just(result.c));
										var next = $author$project$Desktop$advance(
											_Utils_update(
												model,
												{
													F: A7(
														$author$project$AdapterNotice$failedRead,
														3,
														result.dk,
														result.c1,
														$elm$core$Maybe$Just(result.c.c7),
														$elm$core$Maybe$Just(result.c.c2),
														failed,
														model.F),
													aZ: $elm$core$Maybe$Nothing,
													ar: reconciled,
													w: false
												}));
										return _Utils_Tuple2(
											next,
											(model.w && (!failed)) ? _List_fromArray(
												[
													$author$project$Desktop$Focus(
													A2($author$project$Desktop$key, next, 'jump:close'))
												]) : _List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'jump-list-outcome':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'status', 'snapshot']),
									A6(
										$elm$json$Json$Decode$map5,
										F5(
											function (_v55, binding, request, status, snapshot) {
												return {dk: binding, c1: request, c: snapshot, W: status};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string),
										A2($elm$json$Json$Decode$field, 'snapshot', $author$project$JumpList$decoder)));
								var _v54 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v54.$) {
									var result = _v54.a;
									if ((!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(result.dk))) || (!model.a.b.j)) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var jumpList = A4($author$project$JumpList$receive, result.c1, result.W, result.c, model.ar);
										return _Utils_eq(jumpList, model.ar) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
											$author$project$Desktop$advance(
												_Utils_update(
													model,
													{ar: jumpList})),
											_List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'files-snapshot':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'snapshot']),
									A5(
										$elm$json$Json$Decode$map4,
										F4(
											function (_v57, binding, request, snapshot) {
												return {dk: binding, c1: request, c: snapshot};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'snapshot', $author$project$Files$decoder)));
								var _v56 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v56.$) {
									var result = _v56.a;
									if ((!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(result.dk))) || ((!_Utils_eq(
										model.aW,
										$elm$core$Maybe$Just(result.c1))) || (!model.a.b.j))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var reconciled = A2($author$project$Files$reconcile, result.c, model.T);
										var failed = (!result.c.dj) && _Utils_eq(
											reconciled.c,
											$elm$core$Maybe$Just(result.c));
										var next = $author$project$Desktop$advance(
											_Utils_update(
												model,
												{
													F: A7(
														$author$project$AdapterNotice$failedRead,
														2,
														result.dk,
														result.c1,
														$elm$core$Maybe$Just(result.c.c7),
														$elm$core$Maybe$Just(result.c.c2),
														failed,
														model.F),
													T: reconciled,
													aW: $elm$core$Maybe$Nothing,
													B: false
												}));
										return _Utils_Tuple2(
											next,
											(model.p && (model.B && (!failed))) ? _List_fromArray(
												[
													$author$project$Desktop$Focus(
													A2($author$project$Desktop$key, next, 'files:close'))
												]) : _List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'files-outcome':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'status', 'snapshot']),
									A6(
										$elm$json$Json$Decode$map5,
										F5(
											function (_v59, binding, request, status, snapshot) {
												return {dk: binding, c1: request, c: snapshot, W: status};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string),
										A2($elm$json$Json$Decode$field, 'snapshot', $author$project$Files$decoder)));
								var _v58 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v58.$) {
									var result = _v58.a;
									if ((!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(result.dk))) || (!model.a.b.j)) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var files = A4($author$project$Files$receive, result.c1, result.W, result.c, model.T);
										return _Utils_eq(files, model.T) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
											$author$project$Desktop$advance(
												_Utils_update(
													model,
													{T: files})),
											_List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'system-menu-snapshot':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'snapshot']),
									A5(
										$elm$json$Json$Decode$map4,
										F4(
											function (_v61, binding, request, snapshot) {
												return {dk: binding, c1: request, c: snapshot};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'snapshot', $author$project$SystemMenu$decoder)));
								var _v60 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v60.$) {
									var receipt = _v60.a;
									if ((!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(receipt.dk))) || (!_Utils_eq(
										model.aT,
										$elm$core$Maybe$Just(receipt.c1)))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var reconciled = A2($author$project$SystemMenu$reconcile, receipt.c, model.ak);
										var failed = (_Utils_eq(receipt.c.fV, $elm$core$Maybe$Nothing) && (_Utils_eq(receipt.c.fs, $elm$core$Maybe$Nothing) && (_Utils_eq(receipt.c.fE, $elm$core$Maybe$Nothing) && _Utils_eq(receipt.c.fO, $elm$core$Maybe$Nothing)))) && _Utils_eq(
											reconciled.c,
											$elm$core$Maybe$Just(receipt.c));
										var next = $author$project$Desktop$advance(
											_Utils_update(
												model,
												{
													F: A7(
														$author$project$AdapterNotice$failedRead,
														4,
														receipt.dk,
														receipt.c1,
														$elm$core$Maybe$Just(receipt.c.c7),
														$elm$core$Maybe$Just(receipt.c.c2),
														failed,
														model.F),
													ak: reconciled,
													s: $elm$core$Maybe$Nothing,
													aT: $elm$core$Maybe$Nothing,
													E: false
												}));
										return _Utils_Tuple2(
											next,
											(model.v && (model.E && (!failed))) ? _List_fromArray(
												[
													$author$project$Desktop$Focus(
													A2($author$project$Desktop$key, next, 'system:close'))
												]) : _List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'system-menu-outcome':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'status', 'snapshot']),
									A6(
										$elm$json$Json$Decode$map5,
										F5(
											function (_v63, binding, request, status, snapshot) {
												return {dk: binding, c1: request, c: snapshot, W: status};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string),
										A2($elm$json$Json$Decode$field, 'snapshot', $author$project$SystemMenu$decoder)));
								var _v62 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v62.$) {
									var receipt = _v62.a;
									if (!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(receipt.dk))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var menu = A4($author$project$SystemMenu$receive, receipt.c1, receipt.W, receipt.c, model.ak);
										return _Utils_eq(menu, model.ak) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
											$author$project$Desktop$advance(
												_Utils_update(
													model,
													{ak: menu})),
											_List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'notification-snapshot':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'snapshot']),
									A5(
										$elm$json$Json$Decode$map4,
										F4(
											function (_v65, binding, request, snapshot) {
												return {dk: binding, c1: request, c: snapshot};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'snapshot', $author$project$Notifications$decoder)));
								var _v64 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v64.$) {
									var receipt = _v64.a;
									if ((!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(receipt.dk))) || (!_Utils_eq(
										model.a0,
										$elm$core$Maybe$Just(receipt.c1)))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var reconciled = A2($author$project$Notifications$reconcile, receipt.c, model.C);
										var failed = (!receipt.c.dj) && _Utils_eq(
											reconciled.c,
											$elm$core$Maybe$Just(receipt.c));
										var next = $author$project$Desktop$advance(
											_Utils_update(
												model,
												{
													F: A7(
														$author$project$AdapterNotice$failedRead,
														1,
														receipt.dk,
														receipt.c1,
														$elm$core$Maybe$Just(receipt.c.c7),
														$elm$core$Maybe$Just(receipt.c.c2),
														failed,
														model.F),
													C: reconciled,
													a0: $elm$core$Maybe$Nothing,
													D: false
												}));
										return _Utils_Tuple2(
											next,
											(model.t && (model.D && (!failed))) ? _List_fromArray(
												[
													$author$project$Desktop$Focus(
													A2($author$project$Desktop$key, next, 'notifications:close'))
												]) : _List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'notification-update':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'snapshot']),
									A4(
										$elm$json$Json$Decode$map3,
										F3(
											function (_v67, binding, snapshot) {
												return {dk: binding, c: snapshot};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'snapshot', $author$project$Notifications$decoder)));
								var _v66 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v66.$) {
									var receipt = _v66.a;
									if ((!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(receipt.dk))) || (!model.a.b.j)) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var notifications = A2($author$project$Notifications$observe, receipt.c, model.C);
										return _Utils_eq(notifications, model.C) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
											$author$project$Desktop$advance(
												_Utils_update(
													model,
													{C: notifications})),
											_List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'notification-outcome':
								var hasReason = !_Utils_eq(
									$elm$core$Maybe$Nothing,
									$elm$core$Result$toMaybe(
										A2(
											$elm$json$Json$Decode$decodeValue,
											A2($elm$json$Json$Decode$field, 'reason', $elm$json$Json$Decode$value),
											raw)));
								var reasonDecoder = hasReason ? A2(
									$elm$json$Json$Decode$field,
									'reason',
									A2(
										$elm$json$Json$Decode$andThen,
										function (value) {
											return A2(
												$elm$core$List$member,
												value,
												_List_fromArray(
													['', 'expired', 'changed', 'unavailable', 'already-handled'])) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Notification refusal reason');
										},
										$elm$json$Json$Decode$string)) : $elm$json$Json$Decode$succeed('');
								var decoder = A2(
									$author$project$Desktop$strict,
									_Utils_ap(
										_List_fromArray(
											['protocolVersion', 'kind', 'binding', 'requestId', 'status', 'snapshot']),
										hasReason ? _List_fromArray(
											['reason']) : _List_Nil),
									A7(
										$elm$json$Json$Decode$map6,
										F6(
											function (_v69, binding, request, status, reason, snapshot) {
												return {dk: binding, eH: reason, c1: request, c: snapshot, W: status};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string),
										reasonDecoder,
										A2($elm$json$Json$Decode$field, 'snapshot', $author$project$Notifications$decoder)));
								var _v68 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v68.$) {
									var receipt = _v68.a;
									if (!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(receipt.dk))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var notifications = A5($author$project$Notifications$receiveReason, receipt.c1, receipt.W, receipt.eH, receipt.c, model.C);
										return _Utils_eq(notifications, model.C) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
											$author$project$Desktop$advance(
												_Utils_update(
													model,
													{C: notifications})),
											_List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'shortcut-preferences':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'snapshot', 'inventory']),
									A6(
										$elm$json$Json$Decode$map5,
										F5(
											function (_v71, binding, request, snapshot, inventory) {
												return {dk: binding, cV: inventory, c1: request, c: snapshot};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2(
											$elm$json$Json$Decode$field,
											'snapshot',
											$elm$json$Json$Decode$nullable($author$project$ShortcutPreferences$decoder)),
										A2($elm$json$Json$Decode$field, 'inventory', $author$project$ShortcutPreferences$inventoryDecoder)));
								var _v70 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v70.$) {
									var receipt = _v70.a;
									return ((!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(receipt.dk))) || (!_Utils_eq(
										model.aQ,
										$elm$core$Maybe$Just(receipt.c1)))) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
										$author$project$Desktop$advance(
											_Utils_update(
												model,
												{
													F: A7(
														$author$project$AdapterNotice$failedRead,
														7,
														receipt.dk,
														receipt.c1,
														$elm$core$Maybe$Nothing,
														$elm$core$Maybe$Nothing,
														_Utils_eq(receipt.c, $elm$core$Maybe$Nothing),
														model.F),
													aQ: $elm$core$Maybe$Nothing,
													ac: A3(
														$author$project$ShortcutPreferences$observe,
														receipt.c,
														$elm$core$Maybe$Just(receipt.cV),
														model.ac)
												})),
										_List_Nil);
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'shortcut-preferences-outcome':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'status', 'snapshot', 'inventory']),
									A7(
										$elm$json$Json$Decode$map6,
										F6(
											function (_v73, binding, request, status, snapshot, inventory) {
												return {dk: binding, cV: inventory, c1: request, c: snapshot, W: status};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string),
										A2(
											$elm$json$Json$Decode$field,
											'snapshot',
											$elm$json$Json$Decode$nullable($author$project$ShortcutPreferences$decoder)),
										A2($elm$json$Json$Decode$field, 'inventory', $author$project$ShortcutPreferences$inventoryDecoder)));
								var _v72 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v72.$) {
									var receipt = _v72.a;
									if (!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(receipt.dk))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var preferences = A5(
											$author$project$ShortcutPreferences$receive,
											receipt.c1,
											receipt.W,
											receipt.c,
											$elm$core$Maybe$Just(receipt.cV),
											model.ac);
										return _Utils_eq(preferences, model.ac) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
											$author$project$Desktop$advance(
												_Utils_update(
													model,
													{ac: preferences})),
											_List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'shell-settings':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'snapshot']),
									A5(
										$elm$json$Json$Decode$map4,
										F4(
											function (_v75, binding, request, snapshot) {
												return {dk: binding, c1: request, c: snapshot};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2(
											$elm$json$Json$Decode$field,
											'snapshot',
											$elm$json$Json$Decode$nullable($author$project$Settings$decoder))));
								var _v74 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v74.$) {
									var receipt = _v74.a;
									if ((!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(receipt.dk))) || (!_Utils_eq(
										model.bo,
										$elm$core$Maybe$Just(receipt.c1)))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var next = $author$project$Desktop$advance(
											_Utils_update(
												model,
												{
													F: A7(
														$author$project$AdapterNotice$failedRead,
														5,
														receipt.dk,
														receipt.c1,
														$elm$core$Maybe$Nothing,
														$elm$core$Maybe$Nothing,
														_Utils_eq(receipt.c, $elm$core$Maybe$Nothing),
														model.F),
													aj: A2($author$project$Settings$observe, receipt.c, model.aj),
													bo: $elm$core$Maybe$Nothing,
													L: false
												}));
										return _Utils_Tuple2(
											next,
											(model.n && (model.L && (!_Utils_eq(receipt.c, $elm$core$Maybe$Nothing)))) ? _List_fromArray(
												[
													$author$project$Desktop$Focus(
													A2($author$project$Desktop$key, next, 'settings:close'))
												]) : _List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							case 'shell-settings-outcome':
								var decoder = A2(
									$author$project$Desktop$strict,
									_List_fromArray(
										['protocolVersion', 'kind', 'binding', 'requestId', 'status', 'snapshot']),
									A6(
										$elm$json$Json$Decode$map5,
										F5(
											function (_v77, binding, request, status, snapshot) {
												return {dk: binding, c1: request, c: snapshot, W: status};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string),
										A2(
											$elm$json$Json$Decode$field,
											'snapshot',
											$elm$json$Json$Decode$nullable($author$project$Settings$decoder))));
								var _v76 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v76.$) {
									var receipt = _v76.a;
									if (!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(receipt.dk))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var settings = A4($author$project$Settings$receive, receipt.c1, receipt.W, receipt.c, model.aj);
										return _Utils_eq(settings, model.aj) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
											$author$project$Desktop$advance(
												_Utils_update(
													model,
													{aj: settings})),
											_List_Nil);
									}
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
													function (_v79, binding, request, snapshot, pins) {
														return {dk: binding, R: pins, c1: request, c: snapshot};
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
								var _v78 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v78.$) {
									var receipt = _v78.a;
									if ((!(!model.a.b.j)) && (_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(receipt.dk)) && _Utils_eq(
										model.A,
										$elm$core$Maybe$Just(receipt.c1)))) {
										var target = 'launcher-search';
										var applications = $elm$core$Result$toMaybe(
											$author$project$Catalog$decode(receipt.c));
										var next = $author$project$Desktop$advance(
											_Utils_update(
												model,
												{
													F: A7(
														$author$project$AdapterNotice$failedRead,
														0,
														receipt.dk,
														receipt.c1,
														$elm$core$Maybe$Nothing,
														$elm$core$Maybe$Nothing,
														_Utils_eq(applications, $elm$core$Maybe$Nothing),
														model.F),
													aD: applications,
													bu: $elm$core$Maybe$Nothing,
													bv: false,
													A: $elm$core$Maybe$Nothing,
													M: A2($author$project$Launch$catalog, receipt.c, model.M),
													R: A2($author$project$Pins$observe, receipt.R, model.R)
												}));
										return _Utils_Tuple2(
											next,
											(next.q && (model.bv && (!_Utils_eq(applications, $elm$core$Maybe$Nothing)))) ? _List_fromArray(
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
											function (_v81, binding, request, status, pins) {
												return {dk: binding, R: pins, c1: request, W: status};
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder),
										A2($elm$json$Json$Decode$field, 'status', $elm$json$Json$Decode$string),
										A2(
											$elm$json$Json$Decode$field,
											'preferences',
											$elm$json$Json$Decode$nullable($author$project$Pins$decoder))));
								var _v80 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v80.$) {
									var receipt = _v80.a;
									if ((!model.a.b.j) || ((!_Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(receipt.dk))) || (!A2(
										$elm$core$List$member,
										receipt.W,
										_List_fromArray(
											['Saved', 'Refused', 'Unknown']))))) {
										return _Utils_Tuple2(model, _List_Nil);
									} else {
										var pins = A4($author$project$Pins$receive, receipt.c1, receipt.W, receipt.R, model.R);
										return _Utils_Tuple2(
											_Utils_update(
												model,
												{R: pins}),
											(model.q && (!_Utils_eq(pins, model.R))) ? _List_fromArray(
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
											function (_v84, binding, outcome) {
												return _Utils_Tuple2(binding, outcome);
											}),
										$author$project$Desktop$version,
										A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
										A2($elm$json$Json$Decode$field, 'outcome', $elm$json$Json$Decode$value)));
								var _v82 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
								if (!_v82.$) {
									var _v83 = _v82.a;
									var binding = _v83.a;
									var outcome = _v83.b;
									if ((!(!model.a.b.j)) && _Utils_eq(
										model.a.b.dk,
										$elm$core$Maybe$Just(binding))) {
										var launch = A3(
											$author$project$Launch$receive,
											$author$project$Desktop$host(binding),
											outcome,
											model.M);
										var refused = ($author$project$Launch$status(model.M) === 'Pending') && ($author$project$Launch$status(launch) === 'Refused');
										var next = _Utils_update(
											model,
											{
												M: launch,
												q: refused ? true : (model.q && ($author$project$Launch$status(launch) !== 'Submitted'))
											});
										return _Utils_Tuple2(next, _List_Nil);
									} else {
										return _Utils_Tuple2(model, _List_Nil);
									}
								} else {
									return _Utils_Tuple2(model, _List_Nil);
								}
							default:
								break _v39$24;
						}
					} else {
						break _v39$24;
					}
				}
				var _v85 = A2(
					$author$project$Desktop$window,
					$author$project$TaskbarShell$Native(
						$author$project$Shell$Incoming(raw)),
					model);
				var next = _v85.a;
				var effects = _v85.b;
				var _v86 = $author$project$Desktop$syncSwitcher(next);
				var synced = _v86.a;
				var commands = _v86.b;
				return _Utils_Tuple2(
					synced,
					_Utils_ap(effects, commands));
			case 14:
				var stamp = message.a;
				var entry = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) || (_Utils_eq(model.a.b.dk, $elm$core$Maybe$Nothing) || ((!_Utils_eq(
					$author$project$MenuBridge$preparedSnapshot(model.a.h),
					$elm$core$Maybe$Nothing)) || _Utils_eq(
					A2(
						$elm$core$Maybe$andThen,
						$author$project$Catalog$lookup(entry),
						model.aD),
					$elm$core$Maybe$Nothing))))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var windows = model.a;
					var next = $author$project$Desktop$advance(
						$author$project$Desktop$retireSwitcher(
							_Utils_update(
								model,
								{
									p: false,
									B: false,
									cW: model.q,
									o: $elm$core$Maybe$Just(entry),
									w: true,
									H: $elm$core$Maybe$Nothing,
									t: false,
									D: false,
									q: false,
									m: false,
									u: $elm$core$Maybe$Nothing,
									n: false,
									L: false,
									x: $elm$core$Maybe$Nothing,
									s: $elm$core$Maybe$Nothing,
									v: false,
									E: false,
									a: _Utils_update(
										windows,
										{
											h: $author$project$MenuBridge$retireChoices(windows.h),
											J: $elm$core$Maybe$Nothing
										})
								})));
					var _v87 = $author$project$Desktop$readJumpList(next);
					var reading = _v87.a;
					var commands = _v87.b;
					return _Utils_Tuple2(
						reading,
						_Utils_ap(
							commands,
							_List_fromArray(
								[
									$author$project$Desktop$Focus(
									A2($author$project$Desktop$key, reading, 'jump:close'))
								])));
				}
			case 15:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || _Utils_eq(model.o, $elm$core$Maybe$Nothing)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var next = $author$project$Desktop$advance(
						_Utils_update(
							model,
							{o: $elm$core$Maybe$Nothing, w: false}));
					return model.cW ? A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(next, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (current) {
								return A2(
									$author$project$Desktop$update,
									$author$project$Desktop$OpenApplications(current),
									next);
							},
							$author$project$Desktop$capture(next))) : _Utils_Tuple2(
						next,
						_List_fromArray(
							[
								$author$project$Desktop$Focus(
								A2($author$project$Desktop$key, next, 'control:opener'))
							]));
				}
			case 16:
				var stamp = message.a;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || _Utils_eq(model.o, $elm$core$Maybe$Nothing)) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Desktop$readJumpList(model);
			case 17:
				var stamp = message.a;
				var intent = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!_Utils_eq(
					model.o,
					$elm$core$Maybe$Just(intent.d2))) || (!_Utils_eq(model.aZ, $elm$core$Maybe$Nothing)))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v88 = _Utils_Tuple2(
						model.a.b.dk,
						$author$project$UInt64$next(model.c1));
					if ((!_v88.a.$) && (!_v88.b.$)) {
						var binding = _v88.a.a;
						var request = _v88.b.a;
						var _v89 = A3($author$project$JumpList$propose, request, intent, model.ar);
						var jumpList = _v89.a;
						var proposal = _v89.b;
						if (proposal.$ === 1) {
							return _Utils_Tuple2(model, _List_Nil);
						} else {
							var value = proposal.a;
							return _Utils_Tuple2(
								$author$project$Desktop$advance(
									_Utils_update(
										model,
										{o: $elm$core$Maybe$Nothing, ar: jumpList, w: false, c1: request})),
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
													$elm$json$Json$Encode$string('jump-list-effect')),
													_Utils_Tuple2(
													'binding',
													$author$project$Binding$encode(binding)),
													_Utils_Tuple2(
													'requestId',
													$elm$json$Json$Encode$string(
														$author$project$UInt64$string(request))),
													_Utils_Tuple2('intent', value)
												])))
									]));
						}
					} else {
						return _Utils_Tuple2(model, _List_Nil);
					}
				}
			case 18:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) || (_Utils_eq(model.a.b.dk, $elm$core$Maybe$Nothing) || (!_Utils_eq(
					$author$project$MenuBridge$preparedSnapshot(model.a.h),
					$elm$core$Maybe$Nothing))))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var windows = model.a;
					var next = $author$project$Desktop$advance(
						$author$project$Desktop$retireSwitcher(
							_Utils_update(
								model,
								{
									p: true,
									B: true,
									o: $elm$core$Maybe$Nothing,
									w: false,
									H: $elm$core$Maybe$Nothing,
									t: false,
									D: false,
									q: false,
									m: false,
									u: $elm$core$Maybe$Nothing,
									n: false,
									L: false,
									x: $elm$core$Maybe$Nothing,
									s: $elm$core$Maybe$Nothing,
									v: false,
									E: false,
									a: _Utils_update(
										windows,
										{
											h: $author$project$MenuBridge$retireChoices(windows.h),
											J: $elm$core$Maybe$Nothing
										})
								})));
					var _v91 = $author$project$Desktop$readFiles(next);
					var reading = _v91.a;
					var commands = _v91.b;
					return _Utils_Tuple2(
						reading,
						_Utils_ap(
							commands,
							_List_fromArray(
								[
									$author$project$Desktop$Focus(
									A2($author$project$Desktop$key, reading, 'files:close'))
								])));
				}
			case 19:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.p)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var next = $author$project$Desktop$advance(
						_Utils_update(
							model,
							{p: false, B: false, o: $elm$core$Maybe$Nothing, w: false}));
					return _Utils_Tuple2(
						next,
						_List_fromArray(
							[
								$author$project$Desktop$Focus(
								A2($author$project$Desktop$key, next, 'files:opener'))
							]));
				}
			case 20:
				var stamp = message.a;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.p)) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Desktop$readFiles(model);
			case 21:
				var stamp = message.a;
				var value = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.p)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var files = A2($author$project$Files$edit, value, model.T);
					return _Utils_eq(files, model.T) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
						$author$project$Desktop$advance(
							_Utils_update(
								model,
								{T: files})),
						_List_Nil);
				}
			case 23:
				var stamp = message.a;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.p)) ? _Utils_Tuple2(model, _List_Nil) : A2(
					$elm$core$Maybe$withDefault,
					_Utils_Tuple2(model, _List_Nil),
					A2(
						$elm$core$Maybe$map,
						function (snapshot) {
							return A2(
								$author$project$Desktop$sendFiles,
								A2($author$project$Files$intent, snapshot, model.T.fb),
								model);
						},
						model.T.c));
			case 22:
				var stamp = message.a;
				var target = message.b;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.p)) ? _Utils_Tuple2(model, _List_Nil) : A2($author$project$Desktop$sendFiles, target, model);
			case 24:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) || (_Utils_eq(model.a.b.dk, $elm$core$Maybe$Nothing) || (!_Utils_eq(
					$author$project$MenuBridge$preparedSnapshot(model.a.h),
					$elm$core$Maybe$Nothing))))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var windows = model.a;
					var next = $author$project$Desktop$advance(
						$author$project$Desktop$retireSwitcher(
							_Utils_update(
								model,
								{
									p: false,
									B: false,
									o: $elm$core$Maybe$Nothing,
									w: false,
									H: $elm$core$Maybe$Nothing,
									t: false,
									D: false,
									q: false,
									m: false,
									u: $elm$core$Maybe$Nothing,
									n: false,
									L: false,
									x: $elm$core$Maybe$Nothing,
									s: $elm$core$Maybe$Nothing,
									v: true,
									E: true,
									a: _Utils_update(
										windows,
										{
											h: $author$project$MenuBridge$retireChoices(windows.h),
											J: $elm$core$Maybe$Nothing
										})
								})));
					var _v92 = $author$project$Desktop$readSystemMenu(next);
					var reading = _v92.a;
					var commands = _v92.b;
					return _Utils_Tuple2(
						reading,
						_Utils_ap(
							commands,
							_List_fromArray(
								[
									$author$project$Desktop$Focus(
									A2($author$project$Desktop$key, reading, 'system:close'))
								])));
				}
			case 25:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.v)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var next = $author$project$Desktop$advance(
						_Utils_update(
							model,
							{p: false, B: false, o: $elm$core$Maybe$Nothing, w: false, s: $elm$core$Maybe$Nothing, v: false, E: false}));
					return _Utils_Tuple2(
						next,
						_List_fromArray(
							[
								$author$project$Desktop$Focus(
								A2($author$project$Desktop$key, next, 'system:opener'))
							]));
				}
			case 26:
				var stamp = message.a;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.v) || (!_Utils_eq(model.aT, $elm$core$Maybe$Nothing)))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Desktop$readSystemMenu(
					_Utils_update(
						model,
						{s: $elm$core$Maybe$Nothing}));
			case 27:
				var stamp = message.a;
				var intent = message.b;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.v) || ((!_Utils_eq(model.aT, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(model.ak.ex, $elm$core$Maybe$Nothing)) || (!A2($author$project$SystemMenu$supported, intent, model.ak)))))) ? _Utils_Tuple2(model, _List_Nil) : ($author$project$SystemMenu$confirmed(intent) ? _Utils_Tuple2(
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{
								s: $elm$core$Maybe$Just(intent)
							})),
					_List_fromArray(
						[
							$author$project$Desktop$Focus(
							A2($author$project$Desktop$key, model, 'system:cancel'))
						])) : A2($author$project$Desktop$sendSystemChange, intent, model));
			case 28:
				var stamp = message.a;
				var intent = message.b;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.v) || ((!_Utils_eq(
					model.s,
					$elm$core$Maybe$Just(intent))) || (!_Utils_eq(model.aT, $elm$core$Maybe$Nothing))))) ? _Utils_Tuple2(model, _List_Nil) : A2(
					$author$project$Desktop$sendSystemChange,
					intent,
					_Utils_update(
						model,
						{s: $elm$core$Maybe$Nothing}));
			case 29:
				var stamp = message.a;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.v) || _Utils_eq(model.s, $elm$core$Maybe$Nothing))) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{s: $elm$core$Maybe$Nothing})),
					_List_fromArray(
						[
							$author$project$Desktop$Focus(
							A2($author$project$Desktop$key, model, 'system:close'))
						]));
			case 30:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) || _Utils_eq(model.a.b.dk, $elm$core$Maybe$Nothing))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var windows = model.a;
					var next = $author$project$Desktop$advance(
						$author$project$Desktop$retireSwitcher(
							_Utils_update(
								model,
								{
									p: false,
									B: false,
									o: $elm$core$Maybe$Nothing,
									w: false,
									H: $elm$core$Maybe$Nothing,
									C: $author$project$Notifications$clearFocus(model.C),
									t: true,
									D: true,
									q: false,
									m: false,
									u: $elm$core$Maybe$Nothing,
									n: false,
									L: false,
									x: $elm$core$Maybe$Nothing,
									s: $elm$core$Maybe$Nothing,
									v: false,
									E: false,
									a: _Utils_update(
										windows,
										{
											h: $author$project$MenuBridge$retireChoices(windows.h),
											J: $elm$core$Maybe$Nothing
										})
								})));
					var _v93 = $author$project$Desktop$readNotifications(next);
					var reading = _v93.a;
					var commands = _v93.b;
					return _Utils_Tuple2(
						reading,
						_Utils_ap(
							commands,
							_List_fromArray(
								[
									$author$project$Desktop$Focus(
									A2($author$project$Desktop$key, reading, 'notifications:close'))
								])));
				}
			case 31:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.t)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var next = $author$project$Desktop$advance(
						_Utils_update(
							model,
							{
								C: $author$project$Notifications$clearFocus(model.C),
								t: false,
								D: false
							}));
					return _Utils_Tuple2(
						next,
						_List_fromArray(
							[
								$author$project$Desktop$Focus(
								A2($author$project$Desktop$key, next, 'notifications:opener'))
							]));
				}
			case 32:
				var stamp = message.a;
				var identity = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.t)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var notifications = A2($author$project$Notifications$focus, identity, model.C);
					return _Utils_eq(notifications, model.C) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
						_Utils_update(
							model,
							{C: notifications}),
						_List_Nil);
				}
			case 33:
				var stamp = message.a;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.t)) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Desktop$readNotifications(model);
			case 34:
				var stamp = message.a;
				var policy = message.b;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.t) || _Utils_eq(model.C.fD, policy))) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{
								C: A2($author$project$Notifications$configure, policy, model.C)
							})),
					_List_Nil);
			case 35:
				var stamp = message.a;
				var target = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.t) || (!_Utils_eq(model.a0, $elm$core$Maybe$Nothing)))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v94 = _Utils_Tuple2(
						model.a.b.dk,
						$author$project$UInt64$next(model.c1));
					if ((!_v94.a.$) && (!_v94.b.$)) {
						var binding = _v94.a.a;
						var request = _v94.b.a;
						var _v95 = A3($author$project$Notifications$propose, request, target, model.C);
						var notifications = _v95.a;
						var proposal = _v95.b;
						if (proposal.$ === 1) {
							return _Utils_Tuple2(model, _List_Nil);
						} else {
							var value = proposal.a;
							return _Utils_Tuple2(
								$author$project$Desktop$advance(
									_Utils_update(
										model,
										{C: notifications, c1: request})),
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
													$elm$json$Json$Encode$string('notification-effect')),
													_Utils_Tuple2(
													'binding',
													$author$project$Binding$encode(binding)),
													_Utils_Tuple2(
													'requestId',
													$elm$json$Json$Encode$string(
														$author$project$UInt64$string(request))),
													_Utils_Tuple2('intent', value)
												])))
									]));
						}
					} else {
						return _Utils_Tuple2(model, _List_Nil);
					}
				}
			case 36:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) || _Utils_eq(model.a.b.dk, $elm$core$Maybe$Nothing))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var windows = model.a;
					var next = $author$project$Desktop$advance(
						$author$project$Desktop$retireSwitcher(
							_Utils_update(
								model,
								{
									p: false,
									B: false,
									o: $elm$core$Maybe$Nothing,
									w: false,
									H: $elm$core$Maybe$Nothing,
									t: false,
									D: false,
									q: false,
									m: false,
									u: $elm$core$Maybe$Nothing,
									n: true,
									L: true,
									x: $elm$core$Maybe$Nothing,
									s: $elm$core$Maybe$Nothing,
									v: false,
									E: false,
									a: _Utils_update(
										windows,
										{
											h: $author$project$MenuBridge$retireChoices(windows.h),
											J: $elm$core$Maybe$Nothing
										})
								})));
					var _v97 = $author$project$Desktop$readSettings(next);
					var reading = _v97.a;
					var commands = _v97.b;
					var _v98 = $author$project$Desktop$readShortcutPreferences(reading);
					var shortcutsReading = _v98.a;
					var shortcutCommands = _v98.b;
					return _Utils_Tuple2(
						shortcutsReading,
						_Utils_ap(
							commands,
							_Utils_ap(
								shortcutCommands,
								_List_fromArray(
									[
										$author$project$Desktop$Focus(
										A2($author$project$Desktop$key, shortcutsReading, 'settings:close'))
									]))));
				}
			case 37:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.n)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var next = $author$project$Desktop$advance(
						_Utils_update(
							model,
							{p: false, B: false, o: $elm$core$Maybe$Nothing, w: false, t: false, D: false, n: false, L: false, s: $elm$core$Maybe$Nothing, v: false, E: false}));
					return _Utils_Tuple2(
						next,
						_List_fromArray(
							[
								$author$project$Desktop$Focus(
								A2($author$project$Desktop$key, next, 'settings:opener'))
							]));
				}
			case 38:
				var stamp = message.a;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.n)) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{c8: !model.c8})),
					_List_Nil);
			case 39:
				var stamp = message.a;
				var route = message.b;
				var choice = message.c;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.n) || (!_Utils_eq(model.aQ, $elm$core$Maybe$Nothing)))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var preferences = A3($author$project$ShortcutPreferences$edit, route, choice, model.ac);
					return _Utils_eq(preferences, model.ac) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
						$author$project$Desktop$advance(
							_Utils_update(
								model,
								{ac: preferences})),
						_List_Nil);
				}
			case 40:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.n) || (!_Utils_eq(model.aQ, $elm$core$Maybe$Nothing)))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v99 = _Utils_Tuple2(
						model.a.b.dk,
						$author$project$UInt64$next(model.c1));
					if ((!_v99.a.$) && (!_v99.b.$)) {
						var binding = _v99.a.a;
						var request = _v99.b.a;
						var _v100 = A2($author$project$ShortcutPreferences$propose, request, model.ac);
						var preferences = _v100.a;
						var proposal = _v100.b;
						if (proposal.$ === 1) {
							return _Utils_Tuple2(model, _List_Nil);
						} else {
							var value = proposal.a;
							return _Utils_Tuple2(
								$author$project$Desktop$advance(
									_Utils_update(
										model,
										{c1: request, ac: preferences})),
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
													$elm$json$Json$Encode$string('shortcut-preferences-write')),
													_Utils_Tuple2(
													'binding',
													$author$project$Binding$encode(binding)),
													_Utils_Tuple2(
													'requestId',
													$elm$json$Json$Encode$string(
														$author$project$UInt64$string(request))),
													_Utils_Tuple2('proposal', value)
												])))
									]));
						}
					} else {
						return _Utils_Tuple2(model, _List_Nil);
					}
				}
			case 41:
				var stamp = message.a;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.n) || (!_Utils_eq(model.aQ, $elm$core$Maybe$Nothing)))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Desktop$readShortcutPreferences(model);
			case 42:
				var stamp = message.a;
				var values = message.b;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.n)) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{
								aj: A2($author$project$Settings$edit, values, model.aj)
							})),
					_List_Nil);
			case 43:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.n) || (!_Utils_eq(model.bo, $elm$core$Maybe$Nothing)))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v102 = _Utils_Tuple2(
						model.a.b.dk,
						$author$project$UInt64$next(model.c1));
					if ((!_v102.a.$) && (!_v102.b.$)) {
						var binding = _v102.a.a;
						var request = _v102.b.a;
						var _v103 = A2($author$project$Settings$propose, request, model.aj);
						var settings = _v103.a;
						var proposal = _v103.b;
						if (proposal.$ === 1) {
							return _Utils_Tuple2(model, _List_Nil);
						} else {
							var value = proposal.a;
							return _Utils_Tuple2(
								$author$project$Desktop$advance(
									_Utils_update(
										model,
										{c1: request, aj: settings})),
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
													$elm$json$Json$Encode$string('shell-settings-write')),
													_Utils_Tuple2(
													'binding',
													$author$project$Binding$encode(binding)),
													_Utils_Tuple2(
													'requestId',
													$elm$json$Json$Encode$string(
														$author$project$UInt64$string(request))),
													_Utils_Tuple2('proposal', value)
												])))
									]));
						}
					} else {
						return _Utils_Tuple2(model, _List_Nil);
					}
				}
			case 44:
				var stamp = message.a;
				var override = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.n) || (!_Utils_eq(model.aK, $elm$core$Maybe$Nothing)))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var motion = model.I;
					return _Utils_Tuple2(
						$author$project$Desktop$advance(
							_Utils_update(
								model,
								{
									I: _Utils_update(
										motion,
										{
											a1: A2($author$project$MotionPreferences$edit, override, motion.a1)
										})
								})),
						_List_Nil);
				}
			case 45:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.n) || (!_Utils_eq(model.aK, $elm$core$Maybe$Nothing)))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v105 = _Utils_Tuple2(
						model.a.b.dk,
						$author$project$UInt64$next(model.c1));
					if ((!_v105.a.$) && (!_v105.b.$)) {
						var binding = _v105.a.a;
						var request = _v105.b.a;
						var motion = model.I;
						var _v106 = A2($author$project$MotionPreferences$propose, request, motion.a1);
						var preference = _v106.a;
						var proposal = _v106.b;
						if (proposal.$ === 1) {
							return _Utils_Tuple2(model, _List_Nil);
						} else {
							var value = proposal.a;
							return _Utils_Tuple2(
								$author$project$Desktop$advance(
									_Utils_update(
										model,
										{
											I: _Utils_update(
												motion,
												{a1: preference}),
											c1: request
										})),
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
													$elm$json$Json$Encode$string('motion-preferences-write')),
													_Utils_Tuple2(
													'binding',
													$author$project$Binding$encode(binding)),
													_Utils_Tuple2(
													'requestId',
													$elm$json$Json$Encode$string(
														$author$project$UInt64$string(request))),
													_Utils_Tuple2('proposal', value)
												])))
									]));
						}
					} else {
						return _Utils_Tuple2(model, _List_Nil);
					}
				}
			case 46:
				var stamp = message.a;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.n) || (!_Utils_eq(model.aK, $elm$core$Maybe$Nothing)))) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Desktop$readMotionPreferences(model);
			case 47:
				var stamp = message.a;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.n)) ? _Utils_Tuple2(model, _List_Nil) : $author$project$Desktop$readSettings(model);
			case 12:
				var stamp = message.a;
				return A3($author$project$Desktop$requestApplications, true, stamp, model);
			case 13:
				var stamp = message.a;
				return (!model.q) ? _Utils_Tuple2(model, _List_Nil) : A3($author$project$Desktop$requestApplications, false, stamp, model);
			case 64:
				var binding = message.a;
				var request = message.b;
				return (!A3($author$project$Desktop$canProveCatalogUnsent, binding, request, model)) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
					_Utils_update(
						model,
						{
							F: A7($author$project$AdapterNotice$failedRead, 0, binding, request, $elm$core$Maybe$Nothing, $elm$core$Maybe$Nothing, true, model.F),
							bu: $elm$core$Maybe$Just(
								{dk: binding, c1: request}),
							bv: false,
							A: $elm$core$Maybe$Nothing
						}),
					_List_Nil);
			case 60:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.q)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var next = $author$project$Desktop$advance(
						_Utils_update(
							model,
							{bv: false, A: $elm$core$Maybe$Nothing, q: false}));
					return _Utils_Tuple2(
						next,
						_List_fromArray(
							[
								$author$project$Desktop$Focus(
								A2($author$project$Desktop$key, next, 'control:opener'))
							]));
				}
			case 48:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) || ((!$author$project$Shell$available(model.a.b)) || (!_Utils_eq(
					$author$project$MenuBridge$preparedSnapshot(model.a.h),
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
										$author$project$Menu$Dismiss(menu.cl)),
									model).a;
							},
							$author$project$MenuBridge$menuSnapshot(model.a.h).aI));
					var windows = base.a;
					var next = $author$project$Desktop$advance(
						$author$project$Desktop$retireSwitcher(
							_Utils_update(
								base,
								{
									A: $elm$core$Maybe$Nothing,
									p: false,
									B: false,
									o: $elm$core$Maybe$Nothing,
									w: false,
									H: $elm$core$Maybe$Nothing,
									t: false,
									D: false,
									q: false,
									m: true,
									aB: $elm$core$Maybe$Nothing,
									at: $elm$core$Maybe$Nothing,
									u: $elm$core$Maybe$Nothing,
									n: false,
									L: false,
									x: $elm$core$Maybe$Nothing,
									s: $elm$core$Maybe$Nothing,
									v: false,
									E: false,
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
			case 54:
				var stamp = message.a;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.m)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var target = A2(
						$elm$core$Maybe$map,
						function (binding) {
							return {
								dk: binding,
								bx: $author$project$Desktop$OverviewOpener,
								y: A2(
									$elm$core$Maybe$map,
									A2(
										$elm$core$Basics$composeR,
										function ($) {
											return $.P;
										},
										function ($) {
											return $.y;
										}),
									model.a.b._.as)
							};
						},
						model.a.b.dk);
					var next = $author$project$Desktop$advance(
						_Utils_update(
							model,
							{m: false, aB: $elm$core$Maybe$Nothing, at: $elm$core$Maybe$Nothing}));
					var _v108 = A2(
						$author$project$Desktop$windowBase,
						$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
						next);
					var refreshing = _v108.a;
					var commands = _v108.b;
					return _Utils_Tuple2(
						_Utils_update(
							refreshing,
							{u: target}),
						commands);
				}
			case 55:
				var stamp = message.a;
				var selected = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.m) || _Utils_eq(selected, model.at))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var next = $author$project$Desktop$advance(
						_Utils_update(
							model,
							{at: selected}));
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
												return _Utils_eq(g.cU, workspace);
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
			case 57:
				var stamp = message.a;
				var root = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.m) || ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) || (!$author$project$Shell$available(model.a.b))))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var listed = A2(
						$elm$core$List$any,
						function (family) {
							return _Utils_eq(family.r, root) && family.dj;
						},
						A2(
							$elm$core$List$concatMap,
							function ($) {
								return $.a;
							},
							A2(
								$elm$core$Maybe$withDefault,
								_List_Nil,
								$author$project$TaskView$groups(model.a.b))));
					var enabled = A2(
						$elm$core$Maybe$withDefault,
						false,
						A2(
							$elm$core$Maybe$map,
							function (caps) {
								return A2($elm$core$List$member, 'transfer-workspace', caps.ev);
							},
							model.a.b.ds));
					return (!(listed && enabled)) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
						$author$project$Desktop$advance(
							_Utils_update(
								model,
								{
									aB: $elm$core$Maybe$Just(root)
								})),
						_List_Nil);
				}
			case 58:
				var stamp = message.a;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || (!model.m)) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{aB: $elm$core$Maybe$Nothing})),
					_List_Nil);
			case 59:
				var stamp = message.a;
				var root = message.b;
				var destination = message.c;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!_Utils_eq(
					model.aB,
					$elm$core$Maybe$Just(root))) || (!_Utils_eq(model.k, $elm$core$Maybe$Nothing)))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v109 = _Utils_Tuple3(
						A2(
							$elm$core$Maybe$andThen,
							function (g) {
								return A3($author$project$Transfer$propose, g, root, destination);
							},
							model.a.b.ap),
						model.a.b.dk,
						model.a.b._.as);
					if (((!_v109.a.$) && (!_v109.b.$)) && (!_v109.c.$)) {
						var proposed = _v109.a.a;
						var binding = _v109.b.a;
						var observed = _v109.c.a;
						var _v110 = $elm$core$List$head(
							A2(
								$elm$core$List$filter,
								function (f) {
									return _Utils_eq(f.r, root) && f.dj;
								},
								A2(
									$elm$core$List$concatMap,
									function ($) {
										return $.aG;
									},
									$author$project$TaskbarShell$groups(model.a))));
						if (!_v110.$) {
							var family = _v110.a;
							var _v111 = A2(
								$author$project$Desktop$windowBase,
								$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
								_Utils_update(
									model,
									{G: '', m: false, aB: $elm$core$Maybe$Nothing}));
							var next = _v111.a;
							var effects = _v111.b;
							var _v112 = next.a.b.A;
							if (!_v112.$) {
								var request = _v112.a;
								var token = A2($author$project$Desktop$ChoiceToken, binding, request);
								return _Utils_Tuple2(
									_Utils_update(
										next,
										{
											k: $elm$core$Maybe$Just(
												{
													di: family.di,
													dk: binding,
													aV: $elm$core$Maybe$Nothing,
													y: observed.P.y,
													bk: $elm$core$Maybe$Nothing,
													r: root,
													bp: token,
													a4: $elm$core$Maybe$Just(proposed)
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
						} else {
							return _Utils_Tuple2(model, _List_Nil);
						}
					} else {
						return _Utils_Tuple2(model, _List_Nil);
					}
				}
			case 56:
				var stamp = message.a;
				var root = message.b;
				if ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.m) || ((!_Utils_eq(model.k, $elm$core$Maybe$Nothing)) || (!$author$project$Shell$available(model.a.b))))) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var selected = $elm$core$List$head(
						A2(
							$elm$core$List$filter,
							function (family) {
								return _Utils_eq(family.r, root) && (family.dj && (!A3($author$project$MenuBridge$blockedFor, root, model.a.b, model.a.h)));
							},
							A2(
								$elm$core$List$concatMap,
								function ($) {
									return $.a;
								},
								A2(
									$elm$core$List$filter,
									function (g) {
										return _Utils_eq(model.at, $elm$core$Maybe$Nothing) || _Utils_eq(
											model.at,
											$elm$core$Maybe$Just(g.cU));
									},
									A2(
										$elm$core$Maybe$withDefault,
										_List_Nil,
										$author$project$TaskView$groups(model.a.b))))));
					var _v113 = _Utils_Tuple3(selected, model.a.b.dk, model.a.b._.as);
					if (((!_v113.a.$) && (!_v113.b.$)) && (!_v113.c.$)) {
						var family = _v113.a.a;
						var binding = _v113.b.a;
						var observed = _v113.c.a;
						var _v114 = A2(
							$author$project$Desktop$windowBase,
							$author$project$TaskbarShell$Native($author$project$Shell$Refresh),
							_Utils_update(
								model,
								{G: '', m: false}));
						var next = _v114.a;
						var effects = _v114.b;
						var _v115 = next.a.b.A;
						if (!_v115.$) {
							var request = _v115.a;
							var token = A2($author$project$Desktop$ChoiceToken, binding, request);
							return _Utils_Tuple2(
								_Utils_update(
									next,
									{
										k: $elm$core$Maybe$Just(
											{di: family.di, dk: binding, aV: $elm$core$Maybe$Nothing, y: observed.P.y, bk: $elm$core$Maybe$Nothing, r: root, bp: token, a4: $elm$core$Maybe$Nothing}),
										aN: A2(
											$author$project$OverviewRecovery$begin,
											{dk: binding, r: root, e$: model.at},
											request)
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
			case 61:
				var stamp = message.a;
				var query = message.b;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.q) || (_Utils_eq(query, model.c_) || (($elm$core$String$length(query) > 256) || A2(
					$elm$core$String$any,
					function (c) {
						return ($elm$core$Char$toCode(c) < 32) || ($elm$core$Char$toCode(c) === 127);
					},
					query))))) ? _Utils_Tuple2(model, _List_Nil) : _Utils_Tuple2(
					$author$project$Desktop$advance(
						_Utils_update(
							model,
							{c_: query})),
					_List_Nil);
			case 62:
				var stamp = message.a;
				var identity = message.b;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.q) || ((!$author$project$Pins$writable(model.R)) || ((!A2(
					$elm$core$List$member,
					identity,
					$author$project$Desktop$pinIdentities(model))) && _Utils_eq(
					A2(
						$elm$core$Maybe$andThen,
						$author$project$Catalog$lookup(identity),
						model.aD),
					$elm$core$Maybe$Nothing))))) ? _Utils_Tuple2(model, _List_Nil) : A2(
					$author$project$Desktop$savePins,
					A2(
						$author$project$Pins$toggle,
						identity,
						$author$project$Desktop$pinIdentities(model)),
					model);
			case 63:
				var stamp = message.a;
				var identity = message.b;
				var direction = message.c;
				return ((!_Utils_eq(
					$author$project$Desktop$capture(model),
					$elm$core$Maybe$Just(stamp))) || ((!model.q) || (!$author$project$Pins$writable(model.R)))) ? _Utils_Tuple2(model, _List_Nil) : A2(
					$author$project$Desktop$savePins,
					A3(
						$author$project$Pins$move,
						identity,
						direction,
						$author$project$Desktop$pinIdentities(model)),
					model);
			case 65:
				var selection = message.a;
				if (!_Utils_eq(
					$author$project$MenuBridge$preparedSnapshot(model.a.h),
					$elm$core$Maybe$Nothing)) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v116 = A2($author$project$Launch$start, selection, model.M);
					var launch = _v116.a;
					var intent = _v116.b;
					var _v117 = _Utils_Tuple2(intent, model.a.b.dk);
					if ((!_v117.a.$) && (!_v117.b.$)) {
						var wire = _v117.a.a;
						var binding = _v117.b.a;
						return _Utils_Tuple2(
							$author$project$Desktop$retireSwitcher(
								_Utils_update(
									model,
									{A: $elm$core$Maybe$Nothing, M: launch, q: false, m: false})),
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
								{M: launch}),
							_List_Nil);
					}
				}
			case 66:
				var token = message.a;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							M: A2($author$project$Launch$timeout, token, model.M)
						}),
					_List_Nil);
			default:
				var token = message.a;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							M: A2($author$project$Launch$acknowledgeUnknown, token, model.M)
						}),
					_List_Nil);
		}
	});
var $author$project$Desktop$updateOrdinary = F2(
	function (message, model) {
		if ((A2($author$project$PointerOwnership$blocked, model.a.b.dk, model.bH) && $author$project$Desktop$gestureAction(message)) || ((!A2($author$project$Motion$ready, model.a.b.dk, model.I)) && $author$project$Desktop$motionGesture(message))) {
			return _Utils_Tuple2(model, _List_Nil);
		} else {
			var _v0 = A2($author$project$Desktop$updateAvailable, message, model);
			var next = _v0.a;
			var effects = _v0.b;
			var _v1 = $author$project$Desktop$resumeOverview(next);
			var recovered = _v1.a;
			var recoveryEffects = _v1.b;
			var _v2 = $author$project$Desktop$syncMotion(recovered);
			var synced = _v2.a;
			var commands = _v2.b;
			return _Utils_Tuple2(
				synced,
				_Utils_ap(
					effects,
					_Utils_ap(recoveryEffects, commands)));
		}
	});
var $author$project$SurfaceController$applyOrdinary = F2(
	function (message, current) {
		var model = current;
		if (model.az) {
			return _Utils_Tuple2(current, _List_Nil);
		} else {
			var oldMode = $author$project$Surface$mode(model.d);
			var _v0 = A2($author$project$Desktop$update, message, model.d);
			var next = _v0.a;
			var effects = _v0.b;
			var changed = !_Utils_eq(next, model.d);
			var nextMode = $author$project$Surface$mode(next);
			var newLease = (nextMode !== 'closed') && ((!_Utils_eq(nextMode, oldMode)) || ((!_Utils_eq(
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.cl;
					},
					$author$project$MenuBridge$menuSnapshot(model.d.a.h).aI),
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.cl;
					},
					$author$project$MenuBridge$menuSnapshot(next.a.h).aI))) || (((nextMode === 'picker') && (!_Utils_eq(
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.fh;
					},
					model.d.a.J),
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.fh;
					},
					next.a.J)))) || ((nextMode === 'switcher') && (!_Utils_eq(
				$author$project$Switcher$generation(model.d.i),
				$author$project$Switcher$generation(next.i)))))));
			var lease = newLease ? $author$project$UInt64$next(model.em) : $elm$core$Maybe$Just(model.em);
			if ((!changed) && $elm$core$List$isEmpty(effects)) {
				return _Utils_Tuple2(current, _List_Nil);
			} else {
				var stableSurface = (!_Utils_eq(model.eF, $author$project$UInt64$zero)) && ((!newLease) && ($elm$core$List$isEmpty(effects) && _Utils_eq(
					A2(
						$elm$json$Json$Encode$encode,
						0,
						A3($author$project$Surface$packet, model.eF, model.em, next)),
					A2(
						$elm$json$Json$Encode$encode,
						0,
						$author$project$SurfaceController$frame(current)))));
				var stableApplications = function () {
					if (((message.$ === 1) && (!message.a.$)) && (message.a.a.$ === 11)) {
						return (oldMode === 'applications') && ((nextMode === 'applications') && ((!newLease) && _Utils_eq(
							A2(
								$elm$json$Json$Encode$encode,
								0,
								A3($author$project$Surface$packet, model.eF, model.em, next)),
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
							{d: next}),
						A2($elm$core$List$map, $author$project$SurfaceController$DesktopEffect, effects));
				} else {
					var _v1 = _Utils_Tuple2(
						$author$project$UInt64$next(model.eF),
						lease);
					if ((!_v1.a.$) && (!_v1.b.$)) {
						var publication = _v1.a.a;
						var token = _v1.b.a;
						var result = _Utils_update(
							model,
							{d: next, em: token, eF: publication});
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
								{az: true}),
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
			$elm$core$Result$Ok('host-uncertain'))) || ((shell.j !== 1) || ((!_Utils_eq(
			$elm$core$Result$toMaybe(
				A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
					raw)),
			shell.dk)) || (!_Utils_eq(
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
				var entry = {aa: intent, eE: protocol};
				return (A2($elm$core$List$member, entry, model.bC) || (($elm$core$List$length(model.bC) >= 64) || (!A2(
					$elm$core$List$any,
					function (t) {
						return _Utils_eq(t.aa, intent) && (_Utils_eq(t.ay, protocol) && (t.W === 4));
					},
					shell._.z)))) ? model : _Utils_update(
					model,
					{
						bC: A2($elm$core$List$cons, entry, model.bC)
					});
			}
		}
	});
var $author$project$ReceiptRouter$reservationKey = F3(
	function (bound, protocolId, original) {
		var operationValue = function () {
			var _v0 = original.bh;
			switch (_v0.$) {
				case 0:
					return $elm$core$Maybe$Just(0);
				case 1:
					return $elm$core$Maybe$Just(1);
				case 3:
					return $elm$core$Maybe$Just(2);
				case 4:
					return $elm$core$Maybe$Just(3);
				case 5:
					return $elm$core$Maybe$Just(4);
				case 8:
					return $elm$core$Maybe$Just(5);
				case 9:
					return $elm$core$Maybe$Just(6);
				default:
					return $elm$core$Maybe$Nothing;
			}
		}();
		return A2(
			$elm$core$Maybe$map,
			function (op) {
				return {
					aa: {P: original.P, fh: original.fh, aq: original.aq, bh: op, c1: original.c1},
					er: bound,
					eE: protocolId
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
						return _Utils_Tuple2(entry.cq, entry.dk);
					},
					$elm$core$List$head(
						A2(
							$elm$core$List$filter,
							function (entry) {
								return _Utils_eq(entry.a_, _native);
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
				aI: A2(
					$elm$core$Maybe$map,
					function (menu) {
						return (_Utils_eq(menu.dk, bound) && _Utils_eq(
							menu.W,
							$author$project$Menu$Pending(local))) ? _Utils_update(
							menu,
							{
								W: $author$project$Menu$Unknown(local)
							}) : menu;
					},
					state.aI),
				fx: A2(
					$elm$core$List$map,
					function (entry) {
						return (_Utils_eq(entry.cl, local) && _Utils_eq(entry.dk, bound)) ? _Utils_update(
							entry,
							{bq: true}) : entry;
					},
					state.fx)
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
							aI: A3($author$project$Menu$observeUnknown, local, original, state.aI)
						});
				},
				A4($author$project$ReceiptRouter$findReservation, bound, protocolId, intent, state.au)));
	});
var $author$project$ReconciliationFrame$Context = F4(
	function (lifetime, epoch, output, revision) {
		return {fe: epoch, fp: lifetime, y: output, c2: revision};
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
					return $.P;
				},
				after.ap);
			var geometryAccepted = (kind === 'geometry-facts') && (_Utils_eq(
				before.eb,
				$elm$core$Maybe$Just(request)) && ((!_Utils_eq(
				after.eb,
				$elm$core$Maybe$Just(request))) && _Utils_eq(
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.c1;
					},
					after.ap),
				$elm$core$Maybe$Just(request))));
			var actionContext = $elm$core$Result$toMaybe(
				A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'context', $author$project$ReconciliationFrame$contextDecoder),
					raw));
			var actionAccepted = (kind === 'action-projection') && (_Utils_eq(
				before.A,
				$elm$core$Maybe$Just(request)) && ((!_Utils_eq(
				after.A,
				$elm$core$Maybe$Just(request))) && ((!_Utils_eq(actionContext, $elm$core$Maybe$Nothing)) && _Utils_eq(
				A2(
					$elm$core$Maybe$map,
					function ($) {
						return $.P;
					},
					after._.as),
				actionContext))));
			return _Utils_update(
				model,
				{
					N: A2(
						$elm$core$List$map,
						function (slot) {
							return _Utils_eq(slot.eC, $elm$core$Maybe$Nothing) ? slot : ((actionAccepted && _Utils_eq(
								slot.bR,
								$elm$core$Maybe$Just(request))) ? _Utils_update(
								slot,
								{
									e3: A2(
										$elm$core$Maybe$map,
										function (context) {
											return {P: context, c1: request};
										},
										actionContext)
								}) : ((geometryAccepted && _Utils_eq(
								slot.bd,
								$elm$core$Maybe$Just(request))) ? _Utils_update(
								slot,
								{
									ap: A2(
										$elm$core$Maybe$map,
										function (context) {
											return {P: context, c1: request};
										},
										geometryContext)
								}) : slot));
						},
						model.N)
				});
		}
	});
var $author$project$ReconciliationFrame$ReservationReleased = F3(
	function (a, b, c) {
		return {$: 1, a: a, b: b, c: c};
	});
var $author$project$ReconciliationFrame$contextMatches = F2(
	function (binding, context) {
		return A3($author$project$Binding$matchesContext, context.fp, context.fe, binding);
	});
var $author$project$ReconciliationFrame$Record = F5(
	function (schema, effectProtocol, binding, intent, status) {
		return {dk: binding, ay: effectProtocol, aa: intent, fM: schema, W: status};
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
		var operationMatches = (record.ay === 1) ? A2(
			$elm$core$List$member,
			record.aa.bh,
			_List_fromArray(
				[$author$project$Effects$Minimize, $author$project$Effects$Restore, $author$project$Effects$Activate])) : ($author$project$Effects$protocol(record.aa.bh) === 2);
		return (A3($author$project$Binding$matchesContext, record.aa.P.fp, record.aa.P.fe, record.dk) && operationMatches) ? $elm$json$Json$Decode$succeed(record) : $elm$json$Json$Decode$fail('Record authority or operation/protocol mismatch');
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
		return {cl: id, bF: observation, eC: proof};
	});
var $author$project$ReconciliationFrame$Observation = F4(
	function (actionRequestId, geometryRequestId, actionContext, geometryContext) {
		return {a8: actionContext, cF: actionRequestId, bc: geometryContext, cR: geometryRequestId};
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
				var proof = release.eC;
				var observation = release.bF;
				var expectedValid = A2($author$project$ReconciliationFrame$contextMatches, expected.cO, expected.a8) && (A2($author$project$ReconciliationFrame$contextMatches, expected.cO, expected.bc) && _Utils_eq(expected.a8.y, expected.bc.y));
				var correlated = _Utils_eq(binding, expected.cO) && (_Utils_eq(record, expected.eI) && (_Utils_eq(proof.dk, binding) && (_Utils_eq(proof.eG, record.dk) && (_Utils_eq(proof.eK, expected.eD) && ((!_Utils_eq(record.dk, binding)) && (A2($author$project$Binding$sameLifetime, record.aa.P.fp, binding) && (_Utils_eq(observation.cF, expected.cF) && (_Utils_eq(observation.cR, expected.cR) && (_Utils_eq(observation.a8, expected.a8) && (_Utils_eq(observation.bc, expected.bc) && (A2($author$project$ReconciliationFrame$contextMatches, binding, observation.a8) && (A2($author$project$ReconciliationFrame$contextMatches, binding, observation.bc) && _Utils_eq(observation.a8.y, observation.bc.y)))))))))))));
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
		return _Utils_eq(a.dk, b.dk) && (_Utils_eq(a.aa, b.aa) && _Utils_eq(a.ay, b.ay));
	});
var $author$project$ReconciliationTracking$release = F3(
	function (current, raw, model) {
		return A2(
			$elm$core$Result$andThen,
			function (record) {
				if (A2(
					$elm$core$List$any,
					function (entry) {
						return _Utils_eq(entry.aa, record.aa) && _Utils_eq(entry.eE, record.ay);
					},
					model.bC)) {
					return $elm$core$Result$Err('Legacy origin remains unsupported');
				} else {
					var _v0 = $elm$core$List$head(
						A2(
							$elm$core$List$filter,
							function (slot) {
								return A2($author$project$ReconciliationTracking$same, slot.eI, record);
							},
							model.N));
					if (_v0.$ === 1) {
						return $elm$core$Result$Err('No stored Unknown reservation');
					} else {
						var slot = _v0.a;
						var _v1 = _Utils_Tuple3(slot.eC, slot.e3, slot.ap);
						if (((!_v1.a.$) && (!_v1.b.$)) && (!_v1.c.$)) {
							var proof = _v1.a.a;
							var action = _v1.b.a;
							var geometry = _v1.c.a;
							return A2(
								$elm$core$Result$andThen,
								function (frame) {
									if (frame.$ === 1) {
										var accepted = frame.c;
										return (!_Utils_eq(accepted.eC, proof)) ? $elm$core$Result$Err('Announced proof changed') : $elm$core$Result$Ok(
											_Utils_Tuple2(
												_Utils_update(
													model,
													{
														bf: _Utils_eq(
															model.bf,
															$elm$core$Maybe$Just(proof)) ? $elm$core$Maybe$Nothing : model.bf,
														N: A2(
															$elm$core$List$map,
															function (entry) {
																return A2($author$project$ReconciliationTracking$same, entry.eI, record) ? _Utils_update(
																	entry,
																	{c0: true}) : entry;
															},
															model.N)
													}),
												record));
									} else {
										return $elm$core$Result$Err('Expected released frame');
									}
								},
								A2(
									$author$project$ReconciliationFrame$decodeReleased,
									{a8: action.P, cF: action.c1, cO: current, bc: geometry.P, cR: geometry.c1, eD: proof.eK, eI: slot.eI},
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
				return !_Utils_eq(entry.cq, local);
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
					return _Utils_eq(entry.cl, local) && (_Utils_eq(entry.dk, bound) && entry.bq);
				},
				state.fx));
		if (_v0.$ === 1) {
			return _Utils_Tuple2(model, false);
		} else {
			var entry = _v0.a;
			return (_Utils_cmp(
				$elm$core$List$length(state.bL),
				$author$project$Menu$maxOutstanding) > -1) ? _Utils_Tuple2(model, false) : _Utils_Tuple2(
				_Utils_update(
					state,
					{
						fx: A2(
							$elm$core$List$filter,
							function (current) {
								return !_Utils_eq(current.cl, local);
							},
							state.fx),
						bL: A2($elm$core$List$cons, entry, state.bL)
					}),
				true);
		}
	});
var $author$project$MenuBridge$releaseReservationUnknown = F4(
	function (bound, protocolId, intent, model) {
		var state = model;
		var _v0 = A4($author$project$ReceiptRouter$findReservation, bound, protocolId, intent, state.au);
		if (_v0.$ === 1) {
			return model;
		} else {
			var _v1 = _v0.a;
			var local = _v1.a;
			var original = _v1.b;
			var _v2 = A3($author$project$Menu$releaseUnknown, local, original, state.aI);
			var menu = _v2.a;
			var accepted = _v2.b;
			return accepted ? _Utils_update(
				state,
				{
					aI: menu,
					au: A2($author$project$ReceiptRouter$forgetReservation, local, state.au)
				}) : model;
		}
	});
var $author$project$ReconciliationTracking$requested = F3(
	function (kind, request, model) {
		return _Utils_update(
			model,
			{
				N: A2(
					$elm$core$List$map,
					function (slot) {
						return _Utils_eq(slot.eC, $elm$core$Maybe$Nothing) ? slot : ((kind === 'projection-request') ? _Utils_update(
							slot,
							{
								bR: $elm$core$Maybe$Just(request)
							}) : ((kind === 'geometry-facts-request') ? _Utils_update(
							slot,
							{
								bd: $elm$core$Maybe$Just(request)
							}) : slot));
					},
					model.N)
			});
	});
var $author$project$ReconciliationTracking$reset = function (model) {
	return _Utils_update(
		model,
		{
			bf: $elm$core$Maybe$Nothing,
			N: A2(
				$elm$core$List$map,
				function (slot) {
					return _Utils_update(
						slot,
						{e3: $elm$core$Maybe$Nothing, bR: $elm$core$Maybe$Nothing, ap: $elm$core$Maybe$Nothing, bd: $elm$core$Maybe$Nothing, eC: $elm$core$Maybe$Nothing});
				},
				model.N)
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
								return A2($author$project$ReconciliationTracking$same, slot.eI, record);
							},
							model.N));
					if (!_v1.$) {
						var slot = _v1.a;
						return slot.c0 ? $elm$core$Result$Err('Historical reservation already released') : $elm$core$Result$Ok(
							_Utils_Tuple2(model, record));
					} else {
						return ($elm$core$List$length(model.N) >= 64) ? $elm$core$Result$Err('Historical reservation capacity') : $elm$core$Result$Ok(
							_Utils_Tuple2(
								_Utils_update(
									model,
									{
										N: A2(
											$elm$core$List$cons,
											{e3: $elm$core$Maybe$Nothing, bR: $elm$core$Maybe$Nothing, ap: $elm$core$Maybe$Nothing, bd: $elm$core$Maybe$Nothing, eC: $elm$core$Maybe$Nothing, eI: record, c0: false},
											model.N)
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
				if (_Utils_eq(next, model.d)) {
					return _Utils_Tuple2(
						_Utils_update(
							model,
							{ai: recovery}),
						_List_Nil);
				} else {
					var _v19 = $author$project$UInt64$next(model.eF);
					if (_v19.$ === 1) {
						return _Utils_Tuple2(
							_Utils_update(
								model,
								{az: true}),
							_List_Nil);
					} else {
						var publication = _v19.a;
						var updated = _Utils_update(
							model,
							{d: next, eF: publication, ai: recovery});
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
					case 11:
						var raw = message.a;
						return $elm$core$Maybe$Just(raw);
					case 1:
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
							result.d.a.b,
							A4($author$project$ReconciliationTracking$observed, raw, model.d.a.b, result.d.a.b, result.ai));
					} else {
						return result.ai;
					}
				}();
				var reset = ((!_Utils_eq(model.d.a.b.dk, result.d.a.b.dk)) || (!result.d.a.b.j)) ? $author$project$ReconciliationTracking$reset(recovery) : recovery;
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
								return $.eC;
							},
							A2(
								$elm$core$List$filter,
								function (slot) {
									return !slot.c0;
								},
								reset.N)),
						A2(
							$elm$core$Maybe$withDefault,
							_List_Nil,
							A2($elm$core$Maybe$map, $elm$core$List$singleton, reset.bf))));
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
											$author$project$Binding$encode(proof.dk)),
											_Utils_Tuple2(
											'proofRequestId',
											$elm$json$Json$Encode$string(
												$author$project$UInt64$string(proof.eK))),
											_Utils_Tuple2(
											'queriedBinding',
											$author$project$Binding$encode(proof.eG))
										]))));
					},
					proofs) : _List_Nil;
				var emitted = _Utils_ap(readyEffects, effects);
				if ((!_Utils_eq(result.d, model.d)) && (!A2(
					$elm$core$List$any,
					function (effect) {
						if (effect.$ === 1) {
							return true;
						} else {
							return false;
						}
					},
					effects))) {
					var _v15 = $author$project$UInt64$next(result.eF);
					if (!_v15.$) {
						var publication = _v15.a;
						var updated = _Utils_update(
							result,
							{
								eF: publication,
								ai: A2(register, emitted, reset)
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
								{az: true}),
							_List_Nil);
					}
				} else {
					return _Utils_Tuple2(
						_Utils_update(
							result,
							{
								ai: A2(register, emitted, reset)
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
					k: $elm$core$Maybe$Nothing,
					p: false,
					B: false,
					o: $elm$core$Maybe$Nothing,
					w: false,
					H: $elm$core$Maybe$Nothing,
					t: false,
					D: false,
					m: false,
					at: $elm$core$Maybe$Nothing,
					u: $elm$core$Maybe$Nothing,
					n: false,
					L: false,
					i: A2(
						$author$project$Switcher$cancel,
						$author$project$Switcher$generation(application.i),
						application.i),
					aR: $elm$core$Maybe$Nothing,
					aS: $elm$core$Maybe$Nothing,
					s: $elm$core$Maybe$Nothing,
					v: false,
					E: false,
					a: _Utils_update(
						windows,
						{
							h: $author$project$MenuBridge$retireChoices(windows.h),
							J: $elm$core$Maybe$Nothing,
							b: _Utils_update(
								shell,
								{d$: false})
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
				model.d.a.b.dk);
			_v1$3:
			while (true) {
				if ((!_v1.a.$) && (!_v1.b.$)) {
					switch (_v1.a.a) {
						case 'host-reservation-unknown':
							var currentBinding = _v1.b.a;
							if ((!model.d.a.b.j) || (model.d.a.b.j === 3)) {
								return _Utils_Tuple2(current, _List_Nil);
							} else {
								var _v2 = A3($author$project$ReconciliationTracking$unknown, currentBinding, raw, model.ai);
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
												A2($author$project$Shell$RecoveredUnknown, record.ay, record.aa))),
										model.d);
									var admitted = _v4.a;
									var windows = admitted.a;
									var menus = A4($author$project$MenuBridge$observeReservationUnknown, record.dk, record.ay, record.aa, windows.h);
									var tracked = A2(
										$elm$core$List$any,
										function (entry) {
											return _Utils_eq(entry.aa, record.aa) && (_Utils_eq(entry.ay, record.ay) && (entry.W === 4));
										},
										windows.b._.z);
									return (!tracked) ? _Utils_Tuple2(current, _List_Nil) : A2(
										publishDesktop,
										recovery,
										_Utils_update(
											admitted,
											{
												a: _Utils_update(
													windows,
													{h: menus})
											}));
								}
							}
						case 'binding-retirement':
							var currentBinding = _v1.b.a;
							if ((!model.d.a.b.j) || (model.d.a.b.j === 3)) {
								return _Utils_Tuple2(current, _List_Nil);
							} else {
								var _v5 = A3($author$project$ReconciliationTracking$announce, currentBinding, raw, model.ai);
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
														$author$project$UInt64$string(proof.eK))),
													_Utils_Tuple2(
													'queriedBinding',
													$author$project$Binding$encode(proof.eG))
												]));
										var _v7 = A2(
											ordinary,
											_Utils_update(
												model,
												{
													d: clearChoices(model.d),
													ai: recovery
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
							if ((!model.d.a.b.j) || (model.d.a.b.j === 3)) {
								return _Utils_Tuple2(current, _List_Nil);
							} else {
								var _v9 = A3($author$project$ReconciliationTracking$release, currentBinding, raw, model.ai);
								if (_v9.$ === 1) {
									return _Utils_Tuple2(current, _List_Nil);
								} else {
									var _v10 = _v9.a;
									var recovery = _v10.a;
									var record = _v10.b;
									if (!A2(
										$elm$core$List$any,
										function (entry) {
											return (entry.W === 4) && (_Utils_eq(entry.ay, record.ay) && _Utils_eq(entry.aa, record.aa));
										},
										model.d.a.b._.z)) {
										return _Utils_Tuple2(
											_Utils_update(
												model,
												{ai: recovery}),
											_List_Nil);
									} else {
										var preserveShared = A2(
											$elm$core$List$any,
											function (slot) {
												return (!slot.c0) && (_Utils_eq(slot.eI.aa, record.aa) && _Utils_eq(slot.eI.ay, record.ay));
											},
											recovery.N);
										var cleared = clearChoices(model.d);
										var windows = cleared.a;
										var menus = A4($author$project$MenuBridge$releaseReservationUnknown, record.dk, record.ay, record.aa, windows.h);
										var _v11 = A2(
											$author$project$Desktop$update,
											$author$project$Desktop$Window(
												$author$project$TaskbarShell$Native(
													A4($author$project$Shell$ReservationReleased, preserveShared, record.dk, record.ay, record.aa))),
											_Utils_update(
												cleared,
												{
													a: _Utils_update(
														windows,
														{h: menus})
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
var $author$project$Desktop$PointerEntry = 0;
var $author$project$Desktop$SurfaceEntry = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$Menu$Down = 1;
var $author$project$Menu$End = 3;
var $author$project$Menu$Home = 2;
var $author$project$Menu$Navigate = F2(
	function (a, b) {
		return {$: 2, a: a, b: b};
	});
var $author$project$Desktop$NotificationFocus = F2(
	function (a, b) {
		return {$: 32, a: a, b: b};
	});
var $author$project$Desktop$OpenWindowMenu = F2(
	function (a, b) {
		return {$: 2, a: a, b: b};
	});
var $author$project$Menu$Up = 0;
var $author$project$Surface$resolveAction = F4(
	function (publication, lease, raw, model) {
		var hasTrigger = !_Utils_eq(
			$elm$core$Maybe$Nothing,
			$elm$core$Result$toMaybe(
				A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'trigger', $elm$json$Json$Decode$value),
					raw)));
		var strict = function (child) {
			return A2(
				$elm$json$Json$Decode$andThen,
				function (pairs) {
					return _Utils_eq(
						$elm$core$List$sort(
							A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
						_Utils_ap(
							_List_fromArray(
								['id', 'kind', 'lease', 'publication', 'surface', 'surfaceProtocol']),
							hasTrigger ? _List_fromArray(
								['trigger']) : _List_Nil)) ? child : $elm$json$Json$Decode$fail('Surface action fields');
				},
				$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
		};
		var trigger = hasTrigger ? A2(
			$elm$json$Json$Decode$field,
			'trigger',
			A2(
				$elm$json$Json$Decode$andThen,
				function (value) {
					return A2(
						$elm$core$List$member,
						value,
						_List_fromArray(
							['pointer', 'keyboard'])) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Surface action origin');
				},
				$elm$json$Json$Decode$string)) : $elm$json$Json$Decode$succeed('keyboard');
		var decoder = strict(
			A8(
				$elm$json$Json$Decode$map7,
				F7(
					function (version, kind, shown, scoped, identity, role, origin) {
						return {cU: identity, ej: kind, cY: origin, c3: role, eO: scoped, eP: shown, eU: version};
					}),
				A2($elm$json$Json$Decode$field, 'surfaceProtocol', $elm$json$Json$Decode$int),
				A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
				A2($elm$json$Json$Decode$field, 'publication', $author$project$UInt64$decoder),
				A2($elm$json$Json$Decode$field, 'lease', $author$project$UInt64$decoder),
				A2($elm$json$Json$Decode$field, 'id', $elm$json$Json$Decode$string),
				A2($elm$json$Json$Decode$field, 'surface', $elm$json$Json$Decode$string),
				trigger));
		var _v0 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
		if (!_v0.$) {
			var event = _v0.a;
			return ((event.eU !== 2) || ((event.ej !== 'surface-action') || ((!_Utils_eq(event.eP, publication)) || (!_Utils_eq(event.eO, lease))))) ? $elm$core$Maybe$Nothing : A2(
				$elm$core$Maybe$map,
				(event.c3 === 'bar') ? $author$project$Desktop$SurfaceEntry(
					(event.cY === 'keyboard') ? 1 : 0) : $elm$core$Basics$identity,
				A2(
					$elm$core$Maybe$andThen,
					function ($) {
						return $.aJ;
					},
					$elm$core$List$head(
						A2(
							$elm$core$List$filter,
							function (control) {
								return _Utils_eq(control.cl, event.cU) && control.fd;
							},
							(event.c3 === 'bar') ? $author$project$Surface$barControls(model) : ((event.c3 === 'popup') ? $author$project$Surface$controls(model) : _List_Nil)))));
		} else {
			return $elm$core$Maybe$Nothing;
		}
	});
var $author$project$Surface$resolveBase = F4(
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
				function (_v7) {
					var valid = _v7.a;
					var role = _v7.b;
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
					return ((role === 'popup') && (model.q || model.p)) ? A3(
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
								$author$project$Menu$Dismiss(menu.cl));
						case 'Close':
							return send(
								$author$project$Menu$Dismiss(menu.cl));
						case 'ArrowUp':
							return send(
								A2($author$project$Menu$Navigate, menu.cl, 0));
						case 'ArrowDown':
							return send(
								A2($author$project$Menu$Navigate, menu.cl, 1));
						case 'Home':
							return send(
								A2($author$project$Menu$Navigate, menu.cl, 2));
						case 'End':
							return send(
								A2($author$project$Menu$Navigate, menu.cl, 3));
						case 'Enter':
							return ($author$project$Shell$available(model.a.b) && (_Utils_eq(menu.W, $author$project$Menu$Ready) && (!$author$project$Surface$menuBlocked(model)))) ? A2(
								$elm$core$Maybe$map,
								function (index) {
									return $author$project$Desktop$Window(
										$author$project$TaskbarShell$MenuEvent(
											A3($author$project$Menu$Activate, menu.cl, menu.dk, index)));
								},
								menu.fN) : $elm$core$Maybe$Nothing;
						default:
							return $elm$core$Maybe$Nothing;
					}
				},
				$author$project$MenuBridge$menuSnapshot(model.a.h).aI);
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
		var attention = A2(
			strict,
			_List_fromArray(
				['surfaceProtocol', 'kind', 'surface', 'publication', 'lease', 'id']),
			scopes(
				function (role) {
					return ((role === 'popup') && model.t) ? A2($elm$json$Json$Decode$field, 'id', $elm$json$Json$Decode$string) : $elm$json$Json$Decode$fail('No notification popup');
				}));
		var _v0 = A2(
			$elm$json$Json$Decode$decodeValue,
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			raw);
		_v0$5:
		while (true) {
			if (!_v0.$) {
				switch (_v0.a) {
					case 'surface-notification-focus':
						return A2(
							$elm$core$Maybe$andThen,
							function (identity) {
								return ((identity === '') || A2(
									$elm$core$List$any,
									function (control) {
										return _Utils_eq(control.cl, identity);
									},
									$author$project$Surface$controls(model))) ? A2(
									$elm$core$Maybe$map,
									function (stamp) {
										return A2($author$project$Desktop$NotificationFocus, stamp, identity);
									},
									$author$project$Desktop$capture(model)) : $elm$core$Maybe$Nothing;
							},
							$elm$core$Result$toMaybe(
								A2($elm$json$Json$Decode$decodeValue, attention, raw)));
					case 'surface-action':
						return A4($author$project$Surface$resolveAction, publication, lease, raw, model);
					case 'surface-query':
						return A2(
							$elm$core$Maybe$andThen,
							function (_v1) {
								var identity = _v1.a;
								var value = _v1.b;
								return ((identity === 'control:search') && model.q) ? A2(
									$elm$core$Maybe$map,
									function (stamp) {
										return A2($author$project$Desktop$SearchQuery, stamp, value);
									},
									$author$project$Desktop$capture(model)) : (((identity === 'control:files-path') && model.p) ? A2(
									$elm$core$Maybe$map,
									function (stamp) {
										return A2($author$project$Desktop$EditFilesPath, stamp, value);
									},
									$author$project$Desktop$capture(model)) : $elm$core$Maybe$Nothing);
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
										['pointer', 'keyboard']))) || (!_Utils_eq(model.k, $elm$core$Maybe$Nothing))) ? $elm$core$Maybe$Nothing : A2(
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
																return _Utils_eq('bar:group:' + candidate.a_, identity);
															},
															$author$project$TaskbarShell$groups(model.a)));
												}
											}();
											var enabled = A2(
												$elm$core$List$any,
												function (control) {
													return _Utils_eq(control.cl, identity) && control.fd;
												},
												$author$project$Surface$barControls(model));
											var emptyPin = function () {
												if (enabled && A2($elm$core$String$startsWith, 'bar:pin:', identity)) {
													var entryId = A2($elm$core$String$dropLeft, 8, identity);
													return (A2(
														$elm$core$List$member,
														entryId,
														$author$project$Desktop$pinIdentities(model)) && $elm$core$List$isEmpty(
														A2($author$project$Desktop$pinGroups, entryId, model))) ? A2(
														$elm$core$Maybe$andThen,
														function (_v4) {
															return A2(
																$elm$core$Maybe$map,
																function (current) {
																	return A2($author$project$Desktop$OpenJumpList, current, entryId);
																},
																$author$project$Desktop$capture(model));
														},
														A2(
															$elm$core$Maybe$andThen,
															$author$project$Catalog$lookup(entryId),
															model.aD)) : $elm$core$Maybe$Nothing;
												} else {
													return $elm$core$Maybe$Nothing;
												}
											}();
											return _Utils_eq(group, $elm$core$Maybe$Nothing) ? emptyPin : A2(
												$elm$core$Maybe$andThen,
												function (current) {
													var _v3 = current.aG;
													if (_v3.b && (!_v3.b.b)) {
														var family = _v3.a;
														return family.dj ? $elm$core$Maybe$Just(
															A2($author$project$Desktop$OpenWindowMenu, stamp, family.r)) : $elm$core$Maybe$Nothing;
													} else {
														return _Utils_eq(
															A2($author$project$Taskbar$primary, false, current.aG),
															$author$project$Taskbar$Picker) ? $elm$core$Maybe$Just(
															$author$project$Desktop$Window(
																A2($author$project$TaskbarShell$Primary, stamp, current.a_))) : $elm$core$Maybe$Nothing;
													}
												},
												enabled ? group : $elm$core$Maybe$Nothing);
										} else {
											if ((role === 'popup') && (model.q && A2($elm$core$String$startsWith, 'entry:', identity))) {
												var entry = A2($elm$core$String$dropLeft, 6, identity);
												return A2(
													$elm$core$Maybe$andThen,
													function (_v5) {
														return A2(
															$elm$core$Maybe$map,
															function (current) {
																return A2($author$project$Desktop$OpenJumpList, current, entry);
															},
															$author$project$Desktop$capture(model));
													},
													A2(
														$elm$core$Maybe$andThen,
														$author$project$Catalog$lookup(entry),
														model.aD));
											} else {
												if ((role === 'popup') && ($author$project$Surface$mode(model) === 'picker')) {
													return A2(
														$elm$core$Maybe$andThen,
														function (picker) {
															return (!_Utils_eq(picker.c5, stamp)) ? $elm$core$Maybe$Nothing : A2(
																$elm$core$Maybe$map,
																function (family) {
																	return A2($author$project$Desktop$OpenWindowMenu, stamp, family.r);
																},
																$elm$core$List$head(
																	A2(
																		$elm$core$List$filter,
																		function (family) {
																			return _Utils_eq(
																				'family:' + $author$project$UInt64$string(family.r),
																				identity) && family.dj;
																		},
																		A2(
																			$elm$core$List$concatMap,
																			function ($) {
																				return $.aG;
																			},
																			A2(
																				$elm$core$List$filter,
																				function (group) {
																					return _Utils_eq(group.a_, picker.a_);
																				},
																				$author$project$TaskbarShell$groups(model.a))))));
														},
														model.a.J);
												} else {
													return $elm$core$Maybe$Nothing;
												}
											}
										}
									},
									$author$project$Shell$capture(model.a.b));
							},
							$elm$core$Result$toMaybe(
								A2($elm$json$Json$Decode$decodeValue, context, raw)));
					default:
						break _v0$5;
				}
			} else {
				break _v0$5;
			}
		}
		return $elm$core$Maybe$Nothing;
	});
var $author$project$Surface$resolve = F4(
	function (publication, lease, raw, model) {
		return A2(
			$elm$core$Maybe$map,
			function (message) {
				return (_Utils_eq(
					A2(
						$elm$json$Json$Decode$decodeValue,
						A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
						raw),
					$elm$core$Result$Ok('surface-context')) && _Utils_eq(
					A2(
						$elm$json$Json$Decode$decodeValue,
						A2($elm$json$Json$Decode$field, 'surface', $elm$json$Json$Decode$string),
						raw),
					$elm$core$Result$Ok('bar'))) ? A2(
					$author$project$Desktop$SurfaceEntry,
					_Utils_eq(
						A2(
							$elm$json$Json$Decode$decodeValue,
							A2($elm$json$Json$Decode$field, 'trigger', $elm$json$Json$Decode$string),
							raw),
						$elm$core$Result$Ok('keyboard')) ? 1 : 0,
					message) : message;
			},
			A4($author$project$Surface$resolveBase, publication, lease, raw, model));
	});
var $author$project$SurfaceController$update = F2(
	function (event, current) {
		var model = current;
		if (model.az) {
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
							A4($author$project$Surface$resolve, model.eF, model.em, raw, model.d)));
				case 4:
					if ($author$project$Surface$mode(model.d) === 'closed') {
						return _Utils_Tuple2(current, _List_Nil);
					} else {
						var _v1 = _Utils_Tuple2(
							$author$project$UInt64$next(model.em),
							$author$project$UInt64$next(model.eF));
						if ((!_v1.a.$) && (!_v1.b.$)) {
							var token = _v1.a.a;
							var shown = _v1.b.a;
							var result = _Utils_update(
								model,
								{em: token, eF: shown});
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
									{az: true}),
								_List_Nil);
						}
					}
				case 3:
					var lease = event.a;
					if ((!_Utils_eq(lease, model.em)) || ($author$project$Surface$mode(model.d) === 'closed')) {
						return _Utils_Tuple2(current, _List_Nil);
					} else {
						if (!_Utils_eq(model.d.x, $elm$core$Maybe$Nothing)) {
							return A2($author$project$SurfaceController$apply, $author$project$Desktop$InvalidateSnap, current);
						} else {
							var _v2 = _Utils_Tuple2(
								$author$project$UInt64$next(model.em),
								$author$project$UInt64$next(model.eF));
							if ((!_v2.a.$) && (!_v2.b.$)) {
								var token = _v2.a.a;
								var shown = _v2.b.a;
								var result = _Utils_update(
									model,
									{em: token, eF: shown});
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
										{az: true}),
									_List_Nil);
							}
						}
					}
				default:
					var lease = event.a;
					return ((!_Utils_eq(lease, model.em)) || ($author$project$Surface$mode(model.d) === 'closed')) ? _Utils_Tuple2(current, _List_Nil) : ((!_Utils_eq(model.d.o, $elm$core$Maybe$Nothing)) ? A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (stamp) {
								return A2(
									$author$project$SurfaceController$apply,
									$author$project$Desktop$CloseJumpList(stamp),
									current);
							},
							$author$project$Desktop$capture(model.d))) : (model.d.p ? A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (stamp) {
								return A2(
									$author$project$SurfaceController$apply,
									$author$project$Desktop$CloseFiles(stamp),
									current);
							},
							$author$project$Desktop$capture(model.d))) : (model.d.v ? A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (stamp) {
								return A2(
									$author$project$SurfaceController$apply,
									$author$project$Desktop$CloseSystemMenu(stamp),
									current);
							},
							$author$project$Desktop$capture(model.d))) : (model.d.t ? A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (stamp) {
								return A2(
									$author$project$SurfaceController$apply,
									$author$project$Desktop$CloseNotifications(stamp),
									current);
							},
							$author$project$Desktop$capture(model.d))) : (model.d.n ? A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (stamp) {
								return A2(
									$author$project$SurfaceController$apply,
									$author$project$Desktop$CloseSettings(stamp),
									current);
							},
							$author$project$Desktop$capture(model.d))) : ((!_Utils_eq(model.d.x, $elm$core$Maybe$Nothing)) ? A2(
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
							$author$project$Desktop$capture(model.d))) : (($author$project$Surface$mode(model.d) === 'menu') ? A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (menu) {
								return A2(
									$author$project$SurfaceController$apply,
									$author$project$Desktop$Window(
										$author$project$TaskbarShell$MenuEvent(
											$author$project$Menu$Dismiss(menu.cl))),
									current);
							},
							$author$project$MenuBridge$menuSnapshot(model.d.a.h).aI)) : ($author$project$Desktop$switcherOpen(model.d) ? A2(
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
							$author$project$Desktop$capture(model.d))) : (model.d.m ? A2(
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
							$author$project$Desktop$capture(model.d))) : (model.d.q ? A2(
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
							$author$project$Desktop$capture(model.d))) : A2(
						$elm$core$Maybe$withDefault,
						_Utils_Tuple2(current, _List_Nil),
						A2(
							$elm$core$Maybe$map,
							function (picker) {
								return A2(
									$author$project$SurfaceController$apply,
									$author$project$Desktop$Window(
										A2($author$project$TaskbarShell$Close, picker.c5, picker.fh)),
									current);
							},
							model.d.a.J))))))))))));
			}
		}
	});
var $author$project$OutputController$apply = F2(
	function (event, _v0) {
		var model = _v0;
		var _v1 = A2($author$project$SurfaceController$update, event, model.cM);
		var next = _v1.a;
		var effects = _v1.b;
		var changed = !_Utils_eq(
			$author$project$SurfaceController$desktop(next).a.b.dk,
			$author$project$SurfaceController$desktop(model.cM).a.b.dk);
		return _Utils_Tuple2(
			A2(
				$author$project$OutputController$track,
				model,
				_Utils_update(
					model,
					{
						aE: changed ? false : model.aE,
						aw: changed ? _List_Nil : model.aw,
						aF: changed ? false : model.aF,
						cM: next
					})),
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
						{dk: binding, c1: request});
				}),
			A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int),
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			A2($elm$json$Json$Decode$field, 'binding', $author$project$Binding$decoder),
			A2($elm$json$Json$Decode$field, 'requestId', $author$project$UInt64$decoder)));
	var _v0 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
	if (((!_v0.$) && (_v0.a.a === 3)) && (_v0.a.b === 'catalog-request')) {
		var _v1 = _v0.a;
		var request = _v1.c;
		return _Utils_eq(request.c1, $author$project$UInt64$zero) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(request);
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
					key.eE,
					$author$project$Effects$protocol(key.aa.bh))) || (!A3($author$project$Binding$matchesContext, key.aa.P.fp, key.aa.P.fe, key.dk))))) ? $elm$json$Json$Decode$fail('Operation command authority/protocol') : $elm$json$Json$Decode$succeed(key);
			},
			A6(
				$elm$json$Json$Decode$map5,
				F5(
					function (version, kind, binding, protocol, intent) {
						return _Utils_Tuple3(
							version,
							kind,
							{dk: binding, aa: intent, eE: protocol});
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
					$elm$json$Json$Decode$andThen,
					function (pairs) {
						var hasChecked = A2(
							$elm$core$List$member,
							'checked',
							A2($elm$core$List$map, $elm$core$Tuple$first, pairs));
						var extended = A2(
							$elm$core$List$member,
							'focusOnly',
							A2($elm$core$List$map, $elm$core$Tuple$first, pairs));
						var base = A7(
							$elm$json$Json$Decode$map6,
							F6(
								function (identity, domId, label, ariaLabel, detail, available) {
									return {f: ariaLabel, aU: $elm$core$Maybe$Nothing, e: detail, g: domId, fd: available, aH: false, cU: identity, el: label};
								}),
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
							A2($elm$json$Json$Decode$field, 'enabled', $elm$json$Json$Decode$bool));
						return (hasChecked && (!extended)) ? $elm$json$Json$Decode$fail('Checked presentation requires current control shape') : A2(
							$author$project$SurfaceRenderer$strict,
							_Utils_ap(
								_List_fromArray(
									['id', 'domId', 'label', 'ariaLabel', 'detail', 'enabled']),
								_Utils_ap(
									extended ? _List_fromArray(
										['focusOnly']) : _List_Nil,
									hasChecked ? _List_fromArray(
										['checked']) : _List_Nil)),
							A4(
								$elm$json$Json$Decode$map3,
								F3(
									function (row, focusOnly, checked) {
										return _Utils_update(
											row,
											{aU: checked, aH: focusOnly});
									}),
								base,
								extended ? A2($elm$json$Json$Decode$field, 'focusOnly', $elm$json$Json$Decode$bool) : $elm$json$Json$Decode$succeed(false),
								hasChecked ? A2(
									$elm$json$Json$Decode$field,
									'checked',
									A2($elm$json$Json$Decode$map, $elm$core$Maybe$Just, $elm$json$Json$Decode$bool)) : $elm$json$Json$Decode$succeed($elm$core$Maybe$Nothing)));
					},
					$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value)));
		},
		$elm$json$Json$Decode$list($elm$json$Json$Decode$value));
};
var $author$project$Settings$valuesDecoder = $elm$json$Json$Decode$oneOf(
	_List_fromArray(
		[$author$project$Settings$currentValues, $author$project$Settings$legacyValues]));
var $author$project$SurfaceRenderer$decode = function (raw) {
	var legacy = _Utils_eq(
		$elm$core$Maybe$Nothing,
		$elm$core$Result$toMaybe(
			A2(
				$elm$json$Json$Decode$decodeValue,
				A2($elm$json$Json$Decode$field, 'appearance', $elm$json$Json$Decode$value),
				raw)));
	var hasParent = !_Utils_eq(
		$elm$core$Maybe$Nothing,
		$elm$core$Result$toMaybe(
			A2(
				$elm$json$Json$Decode$decodeValue,
				A2($elm$json$Json$Decode$field, 'keyboardParent', $elm$json$Json$Decode$value),
				raw)));
	var parentDecoder = hasParent ? A2(
		$elm$json$Json$Decode$field,
		'keyboardParent',
		A2($elm$json$Json$Decode$map, $elm$core$Maybe$Just, $elm$json$Json$Decode$bool)) : $elm$json$Json$Decode$succeed($elm$core$Maybe$Nothing);
	var hasMotion = !_Utils_eq(
		$elm$core$Maybe$Nothing,
		$elm$core$Result$toMaybe(
			A2(
				$elm$json$Json$Decode$decodeValue,
				A2($elm$json$Json$Decode$field, 'motion', $elm$json$Json$Decode$value),
				raw)));
	var motionDecoder = hasMotion ? A2(
		$elm$json$Json$Decode$field,
		'motion',
		A2(
			$elm$json$Json$Decode$andThen,
			function (v) {
				return A2(
					$elm$core$List$member,
					v,
					_List_fromArray(
						['reduced', 'full'])) ? $elm$json$Json$Decode$succeed(v) : $elm$json$Json$Decode$fail('Motion profile');
			},
			$elm$json$Json$Decode$string)) : $elm$json$Json$Decode$succeed('reduced');
	var decoder = A2(
		$author$project$SurfaceRenderer$strict,
		_Utils_ap(
			_List_fromArray(
				['surfaceProtocol', 'publication', 'lease', 'mode', 'status', 'bar', 'popup']),
			_Utils_ap(
				legacy ? _List_Nil : _List_fromArray(
					['appearance']),
				_Utils_ap(
					hasMotion ? _List_fromArray(
						['motion']) : _List_Nil,
					hasParent ? _List_fromArray(
						['keyboardParent']) : _List_Nil))),
		A4(
			$elm$json$Json$Decode$map3,
			F3(
				function (motion, parent, record) {
					return _Utils_Tuple3(motion, parent, record);
				}),
			motionDecoder,
			parentDecoder,
			A9(
				$elm$json$Json$Decode$map8,
				F8(
					function (version, shown, scoped, current, notice, bar, popup, appearance) {
						return {al: appearance, ad: bar, bw: current, ft: notice, K: popup, eO: scoped, eP: shown, eU: version};
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
					$author$project$SurfaceRenderer$controls(300)),
				A2(
					$elm$json$Json$Decode$field,
					'popup',
					$author$project$SurfaceRenderer$controls(2150)),
				legacy ? $elm$json$Json$Decode$succeed($author$project$Settings$defaults) : A2($elm$json$Json$Decode$field, 'appearance', $author$project$Settings$valuesDecoder))));
	return A2(
		$elm$core$Result$andThen,
		function (_v0) {
			var motion = _v0.a;
			var parent = _v0.b;
			var record = _v0.c;
			var unique = function (names) {
				return _Utils_eq(
					$elm$core$List$length(names),
					$elm$core$Set$size(
						$elm$core$Set$fromList(names)));
			};
			var all = _Utils_ap(record.ad, record.K);
			var identities = A2(
				$elm$core$List$map,
				function ($) {
					return $.cU;
				},
				all);
			return ((record.eU !== 2) || (_Utils_eq(record.eP, $author$project$UInt64$zero) || ((!A2(
				$elm$core$List$member,
				record.bw,
				_List_fromArray(
					['closed', 'picker', 'applications', 'menu', 'overview', 'switcher', 'snap', 'settings', 'notifications', 'system', 'files', 'jump']))) || (((record.bw !== 'closed') && _Utils_eq(record.eO, $author$project$UInt64$zero)) || (((record.bw === 'closed') && (!$elm$core$List$isEmpty(record.K))) || ((!unique(identities)) || ((!unique(
				A2(
					$elm$core$List$map,
					function ($) {
						return $.g;
					},
					all))) || (A2(
				$elm$core$List$any,
				function (control) {
					return $elm$core$String$isEmpty(control.cU) || ($elm$core$String$isEmpty(control.g) || (control.aH && control.fd));
				},
				all) || (A2(
				$elm$core$List$any,
				function ($) {
					return $.aH;
				},
				record.ad) || ((A2(
				$elm$core$List$any,
				function ($) {
					return $.aH;
				},
				record.K) && (record.bw !== 'notifications')) || (($elm$core$List$length(
				A2(
					$elm$core$List$filter,
					function ($) {
						return $.aH;
					},
					record.K)) > 1) || (A2(
				$elm$core$List$any,
				function (control) {
					return !_Utils_eq(control.aU, $elm$core$Maybe$Nothing);
				},
				record.ad) || (A2(
				$elm$core$List$any,
				function (control) {
					return (!_Utils_eq(control.aU, $elm$core$Maybe$Nothing)) && ((record.bw !== 'menu') || (!A2($elm$core$String$startsWith, 'menu:', control.cU)));
				},
				record.K) || ($elm$core$List$length(
				A2(
					$elm$core$List$filter,
					function (control) {
						return !_Utils_eq(control.aU, $elm$core$Maybe$Nothing);
					},
					record.K)) > 1)))))))))))))) ? $elm$core$Result$Err('Invalid presentation scope/identities') : $elm$core$Result$Ok(
				{al: record.al, ad: record.ad, eh: parent, em: record.eO, l: record.bw, I: motion, K: record.K, eF: record.eP, W: record.ft});
		},
		A2(
			$elm$core$Result$mapError,
			$elm$json$Json$Decode$errorToString,
			A2($elm$json$Json$Decode$decodeValue, decoder, raw)));
};
var $author$project$Announcement$encodeMessage = function (message) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'interrupt',
				$elm$json$Json$Encode$bool(message.cm)),
				_Utils_Tuple2(
				'sequence',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(message.bN))),
				_Utils_Tuple2(
				'correlation',
				$elm$json$Json$Encode$string(message.cN)),
				_Utils_Tuple2(
				'text',
				$elm$json$Json$Encode$string(message.dd))
			]));
};
var $author$project$OutcomeAnnouncements$encode = function (_v0) {
	var current = _v0.b;
	return A2(
		$elm$core$Maybe$withDefault,
		$elm$json$Json$Encode$null,
		A2($elm$core$Maybe$map, $author$project$Announcement$encodeMessage, current));
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
		$author$project$SurfaceController$desktop(model.cM)) === 'closed') ? $elm$core$Maybe$Nothing : model.fN;
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
					$author$project$UInt64$string(model.c2))),
				_Utils_Tuple2(
				'views',
				A2($elm$json$Json$Encode$list, $author$project$OutputController$encodeScope, model.av)),
				_Utils_Tuple2(
				'focusOwner',
				A2(
					$elm$core$Maybe$withDefault,
					$elm$json$Json$Encode$null,
					A2($elm$core$Maybe$map, $author$project$OutputController$encodeScope, model.fN))),
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
				$author$project$SurfaceController$frame(model.cM)),
				_Utils_Tuple2(
				'announcer',
				A2(
					$elm$core$Maybe$withDefault,
					$elm$json$Json$Encode$null,
					A2(
						$elm$core$Maybe$map,
						function (scope) {
							return $elm$json$Json$Encode$object(
								_List_fromArray(
									[
										_Utils_Tuple2(
										'scope',
										$author$project$OutputController$encodeScope(scope)),
										_Utils_Tuple2(
										'surface',
										$elm$json$Json$Encode$string(
											(!_Utils_eq(
												$author$project$OutputController$owner(current),
												$elm$core$Maybe$Nothing)) ? 'popup' : 'bar'))
									]));
						},
						model.fN))),
				_Utils_Tuple2(
				'announcement',
				$author$project$OutcomeAnnouncements$encode(model.bS))
			]));
};
var $author$project$SurfaceRenderer$lease = function (_v0) {
	var snapshot = _v0;
	return snapshot.em;
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
	return snapshot.eF;
};
var $author$project$Desktop$CatalogUnsent = F2(
	function (a, b) {
		return {$: 64, a: a, b: b};
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
						A2($author$project$Desktop$CatalogUnsent, request.dk, request.c1)),
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
				return A3($author$project$Desktop$canProveCatalogUnsent, request.dk, request.c1, desktop);
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
				model.fN),
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
		var binding = $author$project$SurfaceController$desktop(model.cM).a.b.dk;
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
				if ((!A2($elm$core$List$member, scoped, model.av)) || (model.aE || (($elm$core$List$length(model.aw) >= 16) || (($elm$core$List$length(requests) > 16) || (($elm$core$String$length(text) > 131072) || ($author$project$OutputController$utf8Length(text) > 131072)))))) {
					var capacity = ($elm$core$List$length(model.aw) >= 16) && (A2($elm$core$List$member, scoped, model.av) && (($elm$core$List$length(requests) <= 16) && (($elm$core$String$length(text) <= 131072) && ($author$project$OutputController$utf8Length(text) <= 131072))));
					var belongs = function (slot) {
						return A2(
							$elm$core$List$member,
							_Utils_Tuple2('projection-request', slot.bg),
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
								slot.bd));
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
								aE: true,
								aF: model.aE ? model.aF : capacity
							}));
					var refused = _v0.a;
					var prepared = $author$project$MenuBridge$preparedSnapshot(
						$author$project$SurfaceController$desktop(
							$author$project$OutputController$controller(refused)).a.h);
					var _v1 = function () {
						if (!prepared.$) {
							var slot = prepared.a;
							return belongs(slot) ? A2(
								$author$project$OutputController$apply,
								$author$project$SurfaceController$Interaction(
									$author$project$Desktop$Window(
										$author$project$TaskbarShell$CancelPrepared(slot.bp))),
								refused) : _Utils_Tuple2(refused, _List_Nil);
						} else {
							return _Utils_Tuple2(refused, _List_Nil);
						}
					}();
					var settled = _v1.a;
					var _v3 = A3(
						$author$project$OutputController$refuseCatalogs,
						$author$project$OutputController$lease(model.cM),
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
							$author$project$SurfaceController$frame(model.cM)));
					if ((!_v5.a.$) && (!_v5.b.$)) {
						var authority = _v5.a.a;
						var snapshot = _v5.b.a;
						var batch = {
							dk: authority,
							cJ: catalogs,
							em: $author$project$SurfaceRenderer$lease(snapshot),
							cX: observations,
							ev: operations,
							eF: $author$project$SurfaceRenderer$publication(snapshot),
							c2: model.c2,
							c5: scoped,
							cD: text
						};
						return _Utils_Tuple2(
							_Utils_update(
								model,
								{
									aw: A2($elm$core$List$cons, batch, model.aw)
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
	return {$: 10, a: a};
};
var $author$project$OutputController$assignOwner = F2(
	function (scope, controllerModel) {
		var registered = A2(
			$elm$core$Maybe$map,
			function (_v0) {
				var outputId = _v0.a;
				var providerId = _v0.b;
				return {dC: outputId, dI: providerId};
			},
			scope);
		return A2(
			$author$project$SurfaceController$update,
			$author$project$SurfaceController$Interaction(
				$author$project$Desktop$PresentationOwner(registered)),
			controllerModel);
	});
var $author$project$Shortcuts$currentGeneration = F2(
	function (expected, snapshot) {
		return (!_Utils_eq(expected, $elm$core$Maybe$Nothing)) && _Utils_eq(
			A2(
				$elm$core$Maybe$andThen,
				function ($) {
					return $.fw;
				},
				$elm$core$List$head(
					$elm$core$List$reverse(snapshot.by))),
			expected);
	});
var $author$project$Shortcuts$destination = function (raw) {
	return A2(
		$elm$core$Maybe$andThen,
		$elm$core$Basics$identity,
		A2(
			$elm$core$Maybe$andThen,
			A2($elm$core$Basics$composeR, $elm$core$List$reverse, $elm$core$List$head),
			$elm$core$Result$toMaybe(
				A2(
					$elm$json$Json$Decode$decodeValue,
					A2(
						$elm$json$Json$Decode$field,
						'events',
						$elm$json$Json$Decode$list(
							A2(
								$elm$json$Json$Decode$field,
								'output',
								$elm$json$Json$Decode$nullable($author$project$Shortcuts$boxDecoder)))),
					raw))));
};
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
						return {dk: binding, ch: disposition, ec: header, em: token, eF: publication, c2: revision, c5: scope, cD: batch};
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
				return _Utils_eq(batch.c5, certificate.c5) && (_Utils_eq(batch.c2, certificate.c2) && (_Utils_eq(batch.eF, certificate.eF) && (_Utils_eq(batch.em, certificate.em) && (_Utils_eq(batch.dk, certificate.dk) && _Utils_eq(batch.cD, certificate.cD)))));
			};
			if ((!_Utils_eq(
				certificate.ec,
				_Utils_Tuple2(1, 'batch-disposition'))) || (!A2(
				$elm$core$List$member,
				certificate.ch,
				_List_fromArray(
					['preflight-unsent', 'admitted', 'uncertain'])))) {
				return _Utils_Tuple2(current, _List_Nil);
			} else {
				var _v1 = $elm$core$List$head(
					A2($elm$core$List$filter, matches, model.aw));
				if (_v1.$ === 1) {
					return _Utils_Tuple2(current, _List_Nil);
				} else {
					var batch = _v1.a;
					var remaining = A2(
						$elm$core$List$filter,
						A2($elm$core$Basics$composeR, matches, $elm$core$Basics$not),
						model.aw);
					var currentShell = $author$project$SurfaceController$desktop(model.cM).a.b;
					var catalogMatched = A2(
						$elm$core$List$any,
						function (request) {
							return A3(
								$author$project$Desktop$canProveCatalogUnsent,
								request.dk,
								request.c1,
								$author$project$SurfaceController$desktop(model.cM));
						},
						batch.cJ);
					var canRecover = model.aF && ($elm$core$List$length(remaining) < 16);
					var consumed = _Utils_update(
						model,
						{
							aE: canRecover ? false : model.aE,
							aw: remaining,
							aF: canRecover ? false : model.aF
						});
					var _v2 = ((certificate.ch === 'preflight-unsent') && _Utils_eq(
						currentShell.dk,
						$elm$core$Maybe$Just(batch.dk))) ? A2(
						$author$project$OutputController$apply,
						$author$project$SurfaceController$Interaction(
							$author$project$Desktop$Window(
								$author$project$TaskbarShell$Native(
									$author$project$Shell$UnsentOperations(batch.ev)))),
						consumed) : _Utils_Tuple2(consumed, _List_Nil);
					var settled = _v2.a;
					var operationEffects = _v2.b;
					var _v3 = ((certificate.ch === 'preflight-unsent') && _Utils_eq(
						currentShell.dk,
						$elm$core$Maybe$Just(batch.dk))) ? A3(
						$author$project$OutputController$refuseCatalogs,
						$elm$core$Maybe$Just(batch.em),
						batch.cJ,
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
					if ((certificate.ch !== 'preflight-unsent') || (((!A2($author$project$Shell$matchesUnsent, batch.cX, currentShell)) && (!catalogMatched)) || ((!_Utils_eq(
						currentShell.dk,
						$elm$core$Maybe$Just(batch.dk))) || (!_Utils_eq(
						$author$project$OutputController$lease(model.cM),
						$elm$core$Maybe$Just(batch.em)))))) {
						return _Utils_Tuple2(recovered, allEffects);
					} else {
						var _v5 = A2(
							$author$project$OutputController$apply,
							$author$project$SurfaceController$NativeDismiss(batch.em),
							recovered);
						var closed = _v5.a;
						var closeEffects = _v5.b;
						var prepared = $author$project$MenuBridge$preparedSnapshot(
							$author$project$SurfaceController$desktop(
								$author$project$OutputController$controller(closed)).a.h);
						var _v6 = function () {
							if (!prepared.$) {
								var selection = prepared.a;
								return A2(
									$author$project$OutputController$apply,
									$author$project$SurfaceController$Interaction(
										$author$project$Desktop$Window(
											$author$project$TaskbarShell$CancelPrepared(selection.bp))),
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
										$author$project$Shell$UnsentObservations(batch.cX)))),
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
var $author$project$OutputController$updateCore = F2(
	function (event, current) {
		var model = current;
		switch (event.$) {
			case 0:
				var raw = event.a;
				return A2($author$project$OutputController$receiveDisposition, raw, current);
			case 3:
				var message = event.a;
				if (message.$ === 11) {
					var raw = message.a;
					var desktop = $author$project$SurfaceController$desktop(model.cM);
					var _v2 = A2($elm$json$Json$Decode$decodeValue, $author$project$Shortcuts$decoder, raw);
					if (_v2.$ === 1) {
						return A2(
							$author$project$OutputController$apply,
							$author$project$SurfaceController$Interaction(message),
							current);
					} else {
						var snapshot = _v2.a;
						var nativeGeneration = A2(
							$elm$core$Maybe$map,
							A2(
								$elm$core$Basics$composeR,
								function ($) {
									return $.P;
								},
								function ($) {
									return $.y;
								}),
							desktop.a.b._.as);
						var reconciled = (desktop.a.b.j === 2) && A2($author$project$Shortcuts$currentGeneration, nativeGeneration, snapshot);
						var matches = A2(
							$elm$core$Maybe$withDefault,
							_List_Nil,
							A2(
								$elm$core$Maybe$map,
								function (box) {
									return A2(
										$elm$core$List$filter,
										function (entry) {
											return _Utils_eq(entry.dV, box) && A2($elm$core$List$member, entry.c5, model.av);
										},
										model.bE);
								},
								$author$project$Shortcuts$destination(raw)));
						var destination = function () {
							if (_Utils_eq(
								A2(
									$elm$json$Json$Decode$decodeValue,
									A2($elm$json$Json$Decode$field, 'shortcutProtocol', $elm$json$Json$Decode$int),
									raw),
								$elm$core$Result$Ok(1)) && ($elm$core$List$length(model.av) === 1)) {
								return $elm$core$List$head(model.av);
							} else {
								if (matches.b && (!matches.b.b)) {
									var entry = matches.a;
									return $elm$core$Maybe$Just(entry.c5);
								} else {
									return $elm$core$Maybe$Nothing;
								}
							}
						}();
						var _v3 = A3($author$project$Shortcuts$receive, desktop.a.b.dk, snapshot, desktop.b8);
						var route = _v3.b;
						if (_Utils_eq(route, $elm$core$Maybe$Nothing) || ((!desktop.a.b.j) || (desktop.a.b.j === 3))) {
							return A2(
								$author$project$OutputController$apply,
								$author$project$SurfaceController$Interaction(message),
								current);
						} else {
							if (!reconciled) {
								return A2(
									$author$project$OutputController$apply,
									$author$project$SurfaceController$Interaction(
										A2($author$project$Desktop$ScopedShortcut, snapshot, false)),
									current);
							} else {
								if (!destination.$) {
									var scope = destination.a;
									if (A2($author$project$PointerOwnership$blocked, desktop.a.b.dk, desktop.bH) || ((!_Utils_eq(
										model.fN,
										$elm$core$Maybe$Just(scope))) && (!$author$project$OutputController$freshRelocationPossible(model.cM)))) {
										return A2(
											$author$project$OutputController$apply,
											$author$project$SurfaceController$Interaction(
												A2($author$project$Desktop$ScopedShortcut, snapshot, false)),
											current);
									} else {
										var _v5 = A2(
											$author$project$OutputController$assignOwner,
											$elm$core$Maybe$Just(scope),
											model.cM);
										var assigned = _v5.a;
										var ownerEffects = _v5.b;
										var _v6 = A2(
											$author$project$OutputController$apply,
											$author$project$SurfaceController$Interaction(
												A2($author$project$Desktop$ScopedShortcut, snapshot, true)),
											_Utils_update(
												model,
												{
													cM: assigned,
													fN: $elm$core$Maybe$Just(scope)
												}));
										var next = _v6.a;
										var effects = _v6.b;
										return _Utils_Tuple2(
											next,
											_Utils_ap(ownerEffects, effects));
									}
								} else {
									return A2(
										$author$project$OutputController$apply,
										$author$project$SurfaceController$Interaction(
											A2($author$project$Desktop$ScopedShortcut, snapshot, false)),
										current);
								}
							}
						}
					}
				} else {
					return A2(
						$author$project$OutputController$apply,
						$author$project$SurfaceController$Interaction(message),
						current);
				}
			case 1:
				var raw = event.a;
				var locationDecoder = A2(
					$author$project$OutputController$strict,
					_List_fromArray(
						['scope', 'box']),
					A3(
						$elm$json$Json$Decode$map2,
						F2(
							function (scope, box) {
								return {dV: box, c5: scope};
							}),
						A2($elm$json$Json$Decode$field, 'scope', $author$project$OutputController$scopeDecoder),
						A2($elm$json$Json$Decode$field, 'box', $author$project$Shortcuts$boxDecoder)));
				var decoder = A2(
					$elm$json$Json$Decode$andThen,
					function (protocol) {
						return (protocol === 1) ? A2(
							$author$project$OutputController$strict,
							_List_fromArray(
								['viewProtocol', 'kind', 'revision', 'views']),
							A5(
								$elm$json$Json$Decode$map4,
								F4(
									function (version, kind, revision, scopes) {
										return {ej: kind, bE: _List_Nil, c2: revision, bn: scopes, eU: version};
									}),
								A2($elm$json$Json$Decode$field, 'viewProtocol', $elm$json$Json$Decode$int),
								A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
								A2($elm$json$Json$Decode$field, 'revision', $author$project$UInt64$decoder),
								A2(
									$elm$json$Json$Decode$field,
									'views',
									$elm$json$Json$Decode$list($author$project$OutputController$scopeDecoder)))) : A2(
							$author$project$OutputController$strict,
							_List_fromArray(
								['viewProtocol', 'kind', 'revision', 'views', 'locations']),
							A6(
								$elm$json$Json$Decode$map5,
								F5(
									function (version, kind, revision, scopes, locations) {
										return {ej: kind, bE: locations, c2: revision, bn: scopes, eU: version};
									}),
								A2($elm$json$Json$Decode$field, 'viewProtocol', $elm$json$Json$Decode$int),
								A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
								A2($elm$json$Json$Decode$field, 'revision', $author$project$UInt64$decoder),
								A2(
									$elm$json$Json$Decode$field,
									'views',
									$elm$json$Json$Decode$list($author$project$OutputController$scopeDecoder)),
								A2(
									$elm$json$Json$Decode$field,
									'locations',
									$elm$json$Json$Decode$list(locationDecoder))));
					},
					A2($elm$json$Json$Decode$field, 'viewProtocol', $elm$json$Json$Decode$int));
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
							var _v15 = $elm$core$List$head(
								A2(
									$elm$core$List$filter,
									function (prior) {
										return _Utils_eq(
											$author$project$OutputController$identity(prior),
											$author$project$OutputController$identity(scope));
									},
									model.av));
							if (!_v15.$) {
								var prior = _v15.a;
								return !(!A2(
									$author$project$UInt64$compare,
									$author$project$OutputController$generation(scope),
									$author$project$OutputController$generation(prior)));
							} else {
								return A2(
									$author$project$UInt64$compare,
									$author$project$OutputController$identity(scope),
									model.cS) === 2;
							}
						},
						scopes));
				};
				var _v8 = A2($elm$json$Json$Decode$decodeValue, decoder, raw);
				if (!_v8.$) {
					var table = _v8.a;
					if ((!A2(
						$elm$core$List$member,
						table.eU,
						_List_fromArray(
							[1, 2]))) || (((table.eU === 2) && (!_Utils_eq(
						A2(
							$elm$core$List$map,
							function ($) {
								return $.c5;
							},
							table.bE),
						table.bn))) || ((table.ej !== 'view-topology') || ((A2($author$project$UInt64$compare, table.c2, model.c2) !== 2) || (!admitted(table.bn)))))) {
						return _Utils_Tuple2(current, _List_Nil);
					} else {
						var survives = A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (priorSelected) {
									return A2($elm$core$List$member, priorSelected, table.bn);
								},
								model.fN));
						var selected = survives ? model.fN : $elm$core$List$head(table.bn);
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
							model.cS,
							table.bn);
						var _v9 = retired ? A2(
							$elm$core$Maybe$withDefault,
							_Utils_Tuple2(model.cM, _List_Nil),
							A2(
								$elm$core$Maybe$map,
								function (token) {
									return A2(
										$author$project$SurfaceController$update,
										$author$project$SurfaceController$NativeDismiss(token),
										model.cM);
								},
								$author$project$OutputController$lease(model.cM))) : _Utils_Tuple2(model.cM, _List_Nil);
						var next = _v9.a;
						var effects = _v9.b;
						var _v10 = A2($author$project$OutputController$assignOwner, selected, next);
						var assigned = _v10.a;
						var ownerEffects = _v10.b;
						var prepared = $author$project$MenuBridge$preparedSnapshot(
							$author$project$SurfaceController$desktop(assigned).a.h);
						var _v11 = function () {
							if (!prepared.$) {
								var slot = prepared.a;
								return A2(
									$author$project$SurfaceController$update,
									$author$project$SurfaceController$Interaction(
										$author$project$Desktop$Window(
											$author$project$TaskbarShell$CancelPrepared(slot.bp))),
									assigned);
							} else {
								return _Utils_Tuple2(assigned, _List_Nil);
							}
						}();
						var cancelled = _v11.a;
						var cancelEffects = _v11.b;
						var prior = A2(
							$elm$core$List$filter,
							A2($elm$core$Basics$composeL, $elm$core$Basics$not, $author$project$OutputController$observationEffect),
							_Utils_ap(
								effects,
								_Utils_ap(ownerEffects, cancelEffects)));
						var _v13 = model.aF ? _Utils_Tuple2(cancelled, _List_Nil) : A2(
							$author$project$SurfaceController$update,
							$author$project$SurfaceController$Interaction(
								$author$project$Desktop$Window(
									$author$project$TaskbarShell$Native(
										$author$project$Shell$RegistrationAvailable(false)))),
							cancelled);
						var unblocked = _v13.a;
						var _v14 = A2(
							$author$project$SurfaceController$update,
							$author$project$SurfaceController$Interaction(
								$author$project$Desktop$Window(
									$author$project$TaskbarShell$Native(
										$author$project$Shell$SupersedeObservations(
											!_Utils_eq(selected, $elm$core$Maybe$Nothing))))),
							unblocked);
						var refreshed = _v14.a;
						var readEffects = _v14.b;
						var result = _Utils_update(
							model,
							{
								aE: model.aF ? model.aE : false,
								cM: refreshed,
								cS: highest,
								bE: table.bE,
								c2: table.c2,
								fN: selected,
								av: table.bn
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
								return {e3: action, ej: kind, c5: scope, eU: version};
							}),
						A2($elm$json$Json$Decode$field, 'viewProtocol', $elm$json$Json$Decode$int),
						A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
						A2($elm$json$Json$Decode$field, 'scope', $author$project$OutputController$scopeDecoder),
						A2($elm$json$Json$Decode$field, 'action', $elm$json$Json$Decode$value)));
				var _v16 = _Utils_Tuple2(
					A2($elm$json$Json$Decode$decodeValue, decoder, raw),
					$author$project$SurfaceRenderer$decode(
						$author$project$SurfaceController$frame(model.cM)));
				if ((!_v16.a.$) && (!_v16.b.$)) {
					var callback = _v16.a.a;
					var snapshot = _v16.b.a;
					if ((callback.eU !== 1) || ((callback.ej !== 'view-action') || (!A2($elm$core$List$member, callback.c5, model.av)))) {
						return _Utils_Tuple2(current, _List_Nil);
					} else {
						var popup = _Utils_eq(
							A2(
								$elm$json$Json$Decode$decodeValue,
								A2($elm$json$Json$Decode$field, 'surface', $elm$json$Json$Decode$string),
								callback.e3),
							$elm$core$Result$Ok('popup'));
						var ownerChange = (!popup) && (!_Utils_eq(
							model.fN,
							$elm$core$Maybe$Just(callback.c5)));
						var canMove = (!ownerChange) || $author$project$OutputController$freshRelocationPossible(model.cM);
						if ((popup && (!_Utils_eq(
							$author$project$OutputController$owner(current),
							$elm$core$Maybe$Just(callback.c5)))) || (!canMove)) {
							return _Utils_Tuple2(current, _List_Nil);
						} else {
							var _v17 = A4(
								$author$project$Surface$resolve,
								$author$project$SurfaceRenderer$publication(snapshot),
								$author$project$SurfaceRenderer$lease(snapshot),
								callback.e3,
								$author$project$SurfaceController$desktop(model.cM));
							if (_v17.$ === 1) {
								return _Utils_Tuple2(current, _List_Nil);
							} else {
								var message = _v17.a;
								var _v18 = A2(
									$author$project$OutputController$assignOwner,
									$elm$core$Maybe$Just(callback.c5),
									model.cM);
								var assigned = _v18.a;
								var ownerEffects = _v18.b;
								var _v19 = A2(
									$author$project$SurfaceController$update,
									$author$project$SurfaceController$Interaction(message),
									assigned);
								var updated = _v19.a;
								var effects = _v19.b;
								var _v20 = ownerChange ? A2($author$project$SurfaceController$update, $author$project$SurfaceController$NativeRelocate, updated) : _Utils_Tuple2(updated, _List_Nil);
								var next = _v20.a;
								var relocation = _v20.b;
								return _Utils_Tuple2(
									_Utils_update(
										model,
										{
											cM: next,
											fN: $elm$core$Maybe$Just(callback.c5)
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
var $author$project$OutputController$update = F2(
	function (event, current) {
		var _v0 = A2($author$project$OutputController$updateCore, event, current);
		var next = _v0.a;
		var effects = _v0.b;
		return _Utils_Tuple2(
			A2($author$project$OutputController$track, current, next),
			effects);
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
			var _v1 = A2($author$project$OutputController$update, value, model.cM);
			var updated = _v1.a;
			var effects = _v1.b;
			var _v2 = A2($author$project$OutputController$register, effects, updated);
			var next = _v2.a;
			var packet = _v2.b;
			return _Utils_Tuple2(
				_Utils_update(
					model,
					{cM: next}),
				$elm$core$Platform$Cmd$batch(
					_List_fromArray(
						[
							A2($author$project$Main$commit, packet, effects),
							model.dJ ? $author$project$Main$inspections(
							$author$project$Inspection$packet(
								$author$project$OutputController$controller(next))) : $elm$core$Platform$Cmd$none
						])));
		}
	});
var $author$project$Main$main = $elm$browser$Browser$element(
	{
		fn: function (qa) {
			return _Utils_Tuple2(
				{cM: $author$project$OutputController$initial, dJ: qa},
				$elm$core$Platform$Cmd$none);
		},
		fP: function (_v0) {
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
		fT: $author$project$Main$update,
		fU: function (_v1) {
			return $elm$html$Html$text('');
		}
	});
_Platform_export({'Main':{'init':$author$project$Main$main($elm$json$Json$Decode$bool)(0)}});}(this));