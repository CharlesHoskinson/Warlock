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
	if (region.bw.aU === region.bG.aU)
	{
		return 'on line ' + region.bw.aU;
	}
	return 'on lines ' + region.bw.aU + ' through ' + region.bG.aU;
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
		impl.cz,
		impl.cR,
		impl.cO,
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
		U: func(record.U),
		by: record.by,
		bs: record.bs
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
		var message = !tag ? value : tag < 3 ? value.a : value.U;
		var stopPropagation = tag == 1 ? value.b : tag == 3 && value.by;
		var currentEventNode = (
			stopPropagation && event.stopPropagation(),
			(tag == 2 ? value.b : tag == 3 && value.bs) && event.preventDefault(),
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
		impl.cz,
		impl.cR,
		impl.cO,
		function(sendToApp, initialModel) {
			var view = impl.cS;
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
		impl.cz,
		impl.cR,
		impl.cO,
		function(sendToApp, initialModel) {
			var divertHrefToApp = impl.bu && impl.bu(sendToApp)
			var view = impl.cS;
			var title = _VirtualDom_doc.title;
			var bodyNode = _VirtualDom_doc.body;
			var currNode = _VirtualDom_virtualize(bodyNode);
			return _Browser_makeAnimator(initialModel, function(model)
			{
				_VirtualDom_divertHrefToApp = divertHrefToApp;
				var doc = view(model);
				var nextNode = _VirtualDom_node('body')(_List_Nil)(doc.cp);
				var patches = _VirtualDom_diff(currNode, nextNode);
				bodyNode = _VirtualDom_applyPatches(bodyNode, currNode, patches, sendToApp);
				currNode = nextNode;
				_VirtualDom_divertHrefToApp = 0;
				(title !== doc.cQ) && (_VirtualDom_doc.title = title = doc.cQ);
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
	var onUrlChange = impl.cC;
	var onUrlRequest = impl.cD;
	var key = function() { key.a(onUrlChange(_Browser_getUrl())); };

	return _Browser_document({
		bu: function(sendToApp)
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
							&& curr.b3 === next.b3
							&& curr.bL === next.bL
							&& curr.b0.a === next.b0.a
						)
							? $elm$browser$Browser$Internal(next)
							: $elm$browser$Browser$External(href)
					));
				}
			});
		},
		cz: function(flags)
		{
			return A3(impl.cz, flags, _Browser_getUrl(), key);
		},
		cS: impl.cS,
		cR: impl.cR,
		cO: impl.cO
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
		? { cw: 'hidden', cq: 'visibilitychange' }
		:
	(typeof _VirtualDom_doc.mozHidden !== 'undefined')
		? { cw: 'mozHidden', cq: 'mozvisibilitychange' }
		:
	(typeof _VirtualDom_doc.msHidden !== 'undefined')
		? { cw: 'msHidden', cq: 'msvisibilitychange' }
		:
	(typeof _VirtualDom_doc.webkitHidden !== 'undefined')
		? { cw: 'webkitHidden', cq: 'webkitvisibilitychange' }
		: { cw: 'hidden', cq: 'visibilitychange' };
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
		M: _Browser_getScene(),
		cd: {
			P: _Browser_window.pageXOffset,
			Q: _Browser_window.pageYOffset,
			O: _Browser_doc.documentElement.clientWidth,
			H: _Browser_doc.documentElement.clientHeight
		}
	};
}

function _Browser_getScene()
{
	var body = _Browser_doc.body;
	var elem = _Browser_doc.documentElement;
	return {
		O: Math.max(body.scrollWidth, body.offsetWidth, elem.scrollWidth, elem.offsetWidth, elem.clientWidth),
		H: Math.max(body.scrollHeight, body.offsetHeight, elem.scrollHeight, elem.offsetHeight, elem.clientHeight)
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
			M: {
				O: node.scrollWidth,
				H: node.scrollHeight
			},
			cd: {
				P: node.scrollLeft,
				Q: node.scrollTop,
				O: node.clientWidth,
				H: node.clientHeight
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
			M: _Browser_getScene(),
			cd: {
				P: x,
				Q: y,
				O: _Browser_doc.documentElement.clientWidth,
				H: _Browser_doc.documentElement.clientHeight
			},
			cs: {
				P: x + rect.left,
				Q: y + rect.top,
				O: rect.width,
				H: rect.height
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



var _Bitwise_and = F2(function(a, b)
{
	return a & b;
});

var _Bitwise_or = F2(function(a, b)
{
	return a | b;
});

var _Bitwise_xor = F2(function(a, b)
{
	return a ^ b;
});

function _Bitwise_complement(a)
{
	return ~a;
};

var _Bitwise_shiftLeftBy = F2(function(offset, a)
{
	return a << offset;
});

var _Bitwise_shiftRightBy = F2(function(offset, a)
{
	return a >> offset;
});

var _Bitwise_shiftRightZfBy = F2(function(offset, a)
{
	return a >>> offset;
});
var $elm$core$Basics$EQ = 1;
var $elm$core$Basics$LT = 0;
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
var $elm$core$Basics$GT = 2;
var $elm$core$Basics$identity = function (x) {
	return x;
};
var $author$project$DesignDemo$Input = $elm$core$Basics$identity;
var $elm$core$Basics$apR = F2(
	function (x, f) {
		return f(x);
	});
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
		if (!builder.f) {
			return A4(
				$elm$core$Array$Array_elm_builtin,
				$elm$core$Elm$JsArray$length(builder.i),
				$elm$core$Array$shiftStep,
				$elm$core$Elm$JsArray$empty,
				builder.i);
		} else {
			var treeLen = builder.f * $elm$core$Array$branchFactor;
			var depth = $elm$core$Basics$floor(
				A2($elm$core$Basics$logBase, $elm$core$Array$branchFactor, treeLen - 1));
			var correctNodeList = reverseNodeList ? $elm$core$List$reverse(builder.j) : builder.j;
			var tree = A2($elm$core$Array$treeFromBuilder, correctNodeList, builder.f);
			return A4(
				$elm$core$Array$Array_elm_builtin,
				$elm$core$Elm$JsArray$length(builder.i) + treeLen,
				A2($elm$core$Basics$max, 5, depth * $elm$core$Array$shiftStep),
				tree,
				builder.i);
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
					{j: nodeList, f: (len / $elm$core$Array$branchFactor) | 0, i: tail});
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
var $elm$json$Json$Decode$decodeValue = _Json_run;
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
var $elm$browser$Browser$Dom$NotFound = $elm$core$Basics$identity;
var $elm$url$Url$Http = 0;
var $elm$url$Url$Https = 1;
var $elm$url$Url$Url = F6(
	function (protocol, host, port_, path, query, fragment) {
		return {bJ: fragment, bL: host, b_: path, b0: port_, b3: protocol, b4: query};
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
var $elm$json$Json$Decode$field = _Json_decodeField;
var $elm$json$Json$Decode$value = _Json_decodeValue;
var $author$project$DesignDemo$fixtureInput = _Platform_incomingPort('fixtureInput', $elm$json$Json$Decode$value);
var $author$project$DesignDemo$fixtureObserved = _Platform_outgoingPort('fixtureObserved', $elm$core$Basics$identity);
var $author$project$Menu$Open = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$Menu$Window = function (a) {
	return {$: 0, a: a};
};
var $author$project$Menu$Binding = $elm$core$Basics$identity;
var $author$project$Menu$binding = $elm$core$Basics$identity;
var $author$project$Menu$OutputId = $elm$core$Basics$identity;
var $author$project$Menu$outputId = $elm$core$Basics$identity;
var $author$project$Menu$WindowId = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$Menu$windowId = $author$project$Menu$WindowId;
var $author$project$DesignDemo$fixtureBinding = $author$project$Menu$binding(
	{
		cn: 'fixture-authority',
		cG: $author$project$Menu$outputId('fixture-output'),
		cH: '1',
		cL: '1',
		cP: $author$project$Menu$Window(
			A2($author$project$Menu$windowId, 'fixture-lifetime', 'fixture-window'))
	});
var $author$project$Menu$Model = $elm$core$Basics$identity;
var $author$project$Menu$init = {z: false, I: _List_Nil, aT: $elm$core$Maybe$Nothing, d: $elm$core$Maybe$Nothing, aW: 1, aX: 1, bZ: _List_Nil, am: _List_Nil, L: _List_Nil};
var $author$project$PreviewLifecycle$Connected = 0;
var $author$project$PreviewLifecycle$Idle = {$: 0};
var $author$project$PreviewLifecycle$Model = $elm$core$Basics$identity;
var $author$project$PreviewIdentity$Identity = $elm$core$Basics$identity;
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
var $author$project$UInt64$Counter = $elm$core$Basics$identity;
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
var $author$project$PreviewIdentity$nextRequest = function (_v0) {
	var counter = _v0;
	return A2(
		$elm$core$Maybe$map,
		$elm$core$Basics$identity,
		$author$project$UInt64$next(counter));
};
var $author$project$UInt64$zero = '0';
var $author$project$PreviewIdentity$zeroRequest = $author$project$UInt64$zero;
var $author$project$PreviewLifecycle$init = function (_v0) {
	var scope = _v0;
	return {
		aa: $elm$core$Maybe$Nothing,
		x: _List_Nil,
		e: $author$project$PreviewLifecycle$Idle,
		ac: 0,
		D: false,
		bO: _List_Nil,
		av: $author$project$PreviewIdentity$nextRequest($author$project$PreviewIdentity$zeroRequest),
		r: _List_Nil,
		a: scope
	};
};
var $elm$json$Json$Encode$bool = _Json_wrap;
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
var $author$project$DesignDemo$context = $elm$json$Json$Encode$object(
	A2(
		$elm$core$List$map,
		function (_v0) {
			var key = _v0.a;
			var value = _v0.b;
			return _Utils_Tuple2(
				key,
				$elm$json$Json$Encode$string(value));
		},
		_List_fromArray(
			[
				_Utils_Tuple2('lifetime', '1'),
				_Utils_Tuple2('incarnation', '4'),
				_Utils_Tuple2('output', '5'),
				_Utils_Tuple2('privacy', '6'),
				_Utils_Tuple2('rendering', '7'),
				_Utils_Tuple2('scene', '8'),
				_Utils_Tuple2('content', '9')
			])));
var $author$project$DesignDemo$nativeBinding = $elm$json$Json$Encode$object(
	_List_fromArray(
		[
			_Utils_Tuple2(
			'lifetime',
			$elm$json$Json$Encode$string('1')),
			_Utils_Tuple2(
			'session',
			$elm$json$Json$Encode$string('2')),
			_Utils_Tuple2(
			'frontend',
			$elm$json$Json$Encode$string('3'))
		]));
var $elm$core$Basics$not = _Basics_not;
var $author$project$DesignDemo$scope = F2(
	function (live, locked) {
		return $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2('binding', $author$project$DesignDemo$nativeBinding),
					_Utils_Tuple2(
					'context',
					(live && (!locked)) ? $author$project$DesignDemo$context : $elm$json$Json$Encode$object(
						A2(
							$elm$core$List$map,
							function (_v0) {
								var key = _v0.a;
								var value = _v0.b;
								return _Utils_Tuple2(
									key,
									$elm$json$Json$Encode$string(value));
							},
							_List_fromArray(
								[
									_Utils_Tuple2('lifetime', '1'),
									_Utils_Tuple2('incarnation', '4'),
									_Utils_Tuple2('output', '5'),
									_Utils_Tuple2('privacy', '6'),
									_Utils_Tuple2('rendering', '7'),
									_Utils_Tuple2(
									'scene',
									locked ? '12' : '10'),
									_Utils_Tuple2('content', '9')
								])))),
					_Utils_Tuple2(
					'observation',
					$elm$json$Json$Encode$string(
						locked ? '3' : (live ? '1' : '2'))),
					_Utils_Tuple2(
					'clock',
					$elm$json$Json$Encode$string('10')),
					_Utils_Tuple2(
					'now',
					$elm$json$Json$Encode$string('11')),
					_Utils_Tuple2(
					'present',
					$elm$json$Json$Encode$bool(true)),
					_Utils_Tuple2(
					'sourceLive',
					$elm$json$Json$Encode$bool(live)),
					_Utils_Tuple2(
					'locked',
					$elm$json$Json$Encode$bool(locked)),
					_Utils_Tuple2(
					'gpuReady',
					$elm$json$Json$Encode$bool(true))
				]));
	});
var $author$project$PreviewLifecycle$Scope = $elm$core$Basics$identity;
var $elm$json$Json$Decode$andThen = _Json_andThen;
var $elm$json$Json$Decode$fail = _Json_fail;
var $author$project$PreviewLifecycle$NativeScope = F9(
	function (binding, context, observation, clock, now, present, sourceLive, locked, gpuReady) {
		return {co: binding, p: clock, h: context, aP: gpuReady, ag: locked, B: now, a8: observation, aY: present, aC: sourceLive};
	});
var $author$project$PreviewLifecycle$Binding = F3(
	function (lifetime, session, frontend) {
		return {bK: frontend, af: lifetime, b8: session};
	});
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
var $author$project$PreviewIdentity$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (counter) {
		return _Utils_eq(counter, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Positive native identity') : $elm$json$Json$Decode$succeed(counter);
	},
	$author$project$UInt64$decoder);
var $elm$json$Json$Decode$keyValuePairs = _Json_decodeKeyValuePairs;
var $elm$core$List$sortBy = _List_sortBy;
var $elm$core$List$sort = function (xs) {
	return A2($elm$core$List$sortBy, $elm$core$Basics$identity, xs);
};
var $author$project$PreviewLifecycle$strict = F2(
	function (fields, decoder) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? decoder : $elm$json$Json$Decode$fail('Preview lifecycle fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$PreviewLifecycle$bindingDecoder = A2(
	$author$project$PreviewLifecycle$strict,
	_List_fromArray(
		['lifetime', 'session', 'frontend']),
	A4(
		$elm$json$Json$Decode$map3,
		$author$project$PreviewLifecycle$Binding,
		A2($elm$json$Json$Decode$field, 'lifetime', $author$project$PreviewIdentity$positive),
		A2($elm$json$Json$Decode$field, 'session', $author$project$PreviewIdentity$positive),
		A2($elm$json$Json$Decode$field, 'frontend', $author$project$PreviewIdentity$positive)));
var $elm$json$Json$Decode$bool = _Json_decodeBool;
var $author$project$PreviewLifecycle$Context = F7(
	function (lifetime, incarnation, output, privacy, rendering, scene, content) {
		return {T: content, w: incarnation, af: lifetime, cG: output, aw: privacy, aA: rendering, M: scene};
	});
var $elm$json$Json$Decode$map7 = _Json_map7;
var $author$project$PreviewLifecycle$contextDecoder = A2(
	$author$project$PreviewLifecycle$strict,
	_List_fromArray(
		['lifetime', 'incarnation', 'output', 'privacy', 'rendering', 'scene', 'content']),
	A8(
		$elm$json$Json$Decode$map7,
		$author$project$PreviewLifecycle$Context,
		A2($elm$json$Json$Decode$field, 'lifetime', $author$project$PreviewIdentity$positive),
		A2($elm$json$Json$Decode$field, 'incarnation', $author$project$PreviewIdentity$positive),
		A2($elm$json$Json$Decode$field, 'output', $author$project$PreviewIdentity$positive),
		A2($elm$json$Json$Decode$field, 'privacy', $author$project$PreviewIdentity$positive),
		A2($elm$json$Json$Decode$field, 'rendering', $author$project$PreviewIdentity$positive),
		A2($elm$json$Json$Decode$field, 'scene', $author$project$PreviewIdentity$positive),
		A2($elm$json$Json$Decode$field, 'content', $author$project$PreviewIdentity$positive)));
var $elm$json$Json$Decode$map8 = _Json_map8;
var $author$project$PreviewLifecycle$nativeScopeDecoder = A2(
	$author$project$PreviewLifecycle$strict,
	_List_fromArray(
		['binding', 'context', 'observation', 'clock', 'now', 'present', 'sourceLive', 'locked', 'gpuReady']),
	A3(
		$elm$json$Json$Decode$map2,
		F2(
			function (constructor, gpu) {
				return constructor(gpu);
			}),
		A9(
			$elm$json$Json$Decode$map8,
			$author$project$PreviewLifecycle$NativeScope,
			A2($elm$json$Json$Decode$field, 'binding', $author$project$PreviewLifecycle$bindingDecoder),
			A2($elm$json$Json$Decode$field, 'context', $author$project$PreviewLifecycle$contextDecoder),
			A2($elm$json$Json$Decode$field, 'observation', $author$project$PreviewIdentity$positive),
			A2($elm$json$Json$Decode$field, 'clock', $author$project$PreviewIdentity$positive),
			A2($elm$json$Json$Decode$field, 'now', $author$project$PreviewIdentity$positive),
			A2($elm$json$Json$Decode$field, 'present', $elm$json$Json$Decode$bool),
			A2($elm$json$Json$Decode$field, 'sourceLive', $elm$json$Json$Decode$bool),
			A2($elm$json$Json$Decode$field, 'locked', $elm$json$Json$Decode$bool)),
		A2($elm$json$Json$Decode$field, 'gpuReady', $elm$json$Json$Decode$bool)));
var $author$project$PreviewLifecycle$scopeDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (scope) {
		return _Utils_eq(scope.h.af, scope.co.af) ? $elm$json$Json$Decode$succeed(scope) : $elm$json$Json$Decode$fail('Scope lifetime does not match binding');
	},
	$author$project$PreviewLifecycle$nativeScopeDecoder);
var $elm$core$Result$toMaybe = function (result) {
	if (!result.$) {
		var v = result.a;
		return $elm$core$Maybe$Just(v);
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$DesignDemo$initialPreview = A2(
	$elm$core$Maybe$map,
	$author$project$PreviewLifecycle$init,
	$elm$core$Result$toMaybe(
		A2(
			$elm$json$Json$Decode$decodeValue,
			$author$project$PreviewLifecycle$scopeDecoder,
			A2($author$project$DesignDemo$scope, true, false))));
var $author$project$Menu$AlwaysOnTop = function (a) {
	return {$: 8, a: a};
};
var $author$project$Menu$Close = {$: 6};
var $author$project$Menu$ExitFullscreen = {$: 7};
var $author$project$Menu$Launch = function (a) {
	return {$: 10, a: a};
};
var $author$project$Menu$Maximize = {$: 5};
var $author$project$Menu$Minimize = {$: 4};
var $author$project$Menu$Move = {$: 2};
var $author$project$Menu$PinToTaskbar = function (a) {
	return {$: 9, a: a};
};
var $author$project$Menu$ProviderCommand = function (a) {
	return {$: 11, a: a};
};
var $author$project$Menu$Restore = {$: 0};
var $author$project$Menu$RestoreGeometry = {$: 1};
var $author$project$Menu$Size = {$: 3};
var $author$project$Menu$DeclaredActionId = $elm$core$Basics$identity;
var $author$project$Menu$declaredActionId = $elm$core$Basics$identity;
var $author$project$DesignDemo$items = _List_fromArray(
	[
		{t: $author$project$Menu$Restore, q: true, bP: 'Restore'},
		{t: $author$project$Menu$RestoreGeometry, q: true, bP: 'Restore geometry'},
		{t: $author$project$Menu$Move, q: true, bP: 'Move'},
		{t: $author$project$Menu$Size, q: false, bP: 'Size'},
		{t: $author$project$Menu$Minimize, q: true, bP: 'Minimize'},
		{t: $author$project$Menu$Maximize, q: true, bP: 'Maximize'},
		{t: $author$project$Menu$Close, q: true, bP: 'Close window'},
		{t: $author$project$Menu$ExitFullscreen, q: true, bP: 'Exit fullscreen'},
		{
		t: $author$project$Menu$AlwaysOnTop(true),
		q: true,
		bP: 'Always on top'
	},
		{
		t: $author$project$Menu$PinToTaskbar(true),
		q: true,
		bP: 'Pin to taskbar'
	},
		{
		t: $author$project$Menu$Launch(
			$author$project$Menu$declaredActionId('fixture-application')),
		q: true,
		bP: 'Launch declared application'
	},
		{
		t: $author$project$Menu$ProviderCommand(
			$author$project$Menu$declaredActionId('fixture-action')),
		q: true,
		bP: 'Declared provider action'
	}
	]);
var $elm$json$Json$Encode$list = F2(
	function (func, entries) {
		return _Json_wrap(
			A3(
				$elm$core$List$foldl,
				_Json_addEntry(func),
				_Json_emptyArray(0),
				entries));
	});
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
var $author$project$Menu$Ready = {$: 0};
var $author$project$Menu$Refused = function (a) {
	return {$: 2, a: a};
};
var $author$project$Menu$Uncertain = {$: 3};
var $author$project$Menu$Unknown = function (a) {
	return {$: 4, a: a};
};
var $elm$core$Maybe$andThen = F2(
	function (callback, maybeValue) {
		if (!maybeValue.$) {
			var value = maybeValue.a;
			return callback(value);
		} else {
			return $elm$core$Maybe$Nothing;
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
var $elm$core$String$cons = _String_cons;
var $elm$core$String$fromChar = function (_char) {
	return A2($elm$core$String$cons, _char, '');
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
var $elm$core$Basics$composeR = F3(
	function (f, g, x) {
		return g(
			f(x));
	});
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
var $author$project$Menu$enabledIndices = function (items) {
	return A2(
		$elm$core$List$filterMap,
		$elm$core$Basics$identity,
		A2(
			$elm$core$List$indexedMap,
			F2(
				function (index, item) {
					return item.q ? $elm$core$Maybe$Just(index) : $elm$core$Maybe$Nothing;
				}),
			items));
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
var $elm$core$List$head = function (list) {
	if (list.b) {
		var x = list.a;
		var xs = list.b;
		return $elm$core$Maybe$Just(x);
	} else {
		return $elm$core$Maybe$Nothing;
	}
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
var $elm$core$List$member = F2(
	function (x, xs) {
		return A2(
			$elm$core$List$any,
			function (a) {
				return _Utils_eq(a, x);
			},
			xs);
	});
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
		var enabled = $author$project$Menu$enabledIndices(menu.ar);
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
					var _v1 = menu.cN;
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
					var _v2 = menu.cN;
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
			{cN: selected});
	});
var $elm$core$Basics$neq = _Utils_notEqual;
var $author$project$Menu$outputTuple = function (_v0) {
	var value = _v0;
	return _Utils_Tuple2(value.cG, value.cH);
};
var $author$project$Menu$sameTarget = F2(
	function (_v0, _v1) {
		var left = _v0;
		var right = _v1;
		return _Utils_eq(left.cP, right.cP);
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
var $elm$core$String$trim = _String_trim;
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
					if (A2($elm$core$List$member, item.t, seen)) {
						return false;
					} else {
						var $temp$remaining = rest,
							$temp$seen = A2($elm$core$List$cons, item.t, seen);
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
			return (!A2($elm$core$List$member, target, state.I)) && (!A2(
				$elm$core$List$member,
				$author$project$Menu$outputTuple(target),
				state.L));
		};
		var unchanged = _Utils_Tuple2(model, _List_Nil);
		var editMenu = F2(
			function (id, transform) {
				var _v8 = state.d;
				if (!_v8.$) {
					var menu = _v8.a;
					return _Utils_eq(menu.ae, id) ? _Utils_Tuple2(
						_Utils_update(
							state,
							{
								d: transform(menu)
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
				if (state.z || ((!valid(target)) || ((!$author$project$Menu$validItems(items)) || (state.aX > 2147483647)))) {
					return unchanged;
				} else {
					var status = function () {
						var _v1 = $elm$core$List$head(
							A2(
								$elm$core$List$filter,
								function (entry) {
									return A2($author$project$Menu$sameTarget, entry.co, target);
								},
								state.bZ));
						if (_v1.$ === 1) {
							return $author$project$Menu$Ready;
						} else {
							var entry = _v1.a;
							return entry.Z ? $author$project$Menu$Unknown(entry.ae) : $author$project$Menu$Pending(entry.ae);
						}
					}();
					var menu = {
						co: target,
						ae: state.aX,
						ar: items,
						cN: $elm$core$List$head(
							$author$project$Menu$enabledIndices(items)),
						bx: status
					};
					return _Utils_Tuple2(
						_Utils_update(
							state,
							{
								d: $elm$core$Maybe$Just(menu),
								aX: state.aX + 1
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
						if (_Utils_eq(menu.co, target) && valid(target)) {
							var _v2 = A2($author$project$Menu$itemAt, index, menu.ar);
							if (!_v2.$) {
								var item = _v2.a;
								return item.q ? $elm$core$Maybe$Just(
									_Utils_update(
										menu,
										{
											cN: $elm$core$Maybe$Just(index)
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
				var _v3 = state.d;
				if (_v3.$ === 1) {
					return unchanged;
				} else {
					var menu = _v3.a;
					if (state.z || ((!_Utils_eq(menu.ae, id)) || ((!_Utils_eq(menu.co, target)) || ((!valid(target)) || (state.aW > 2147483647))))) {
						return unchanged;
					} else {
						if (A2(
							$elm$core$List$any,
							function (entry) {
								return A2($author$project$Menu$sameTarget, entry.co, target);
							},
							state.bZ)) {
							return unchanged;
						} else {
							var _v4 = A2($author$project$Menu$itemAt, index, menu.ar);
							if (!_v4.$) {
								var item = _v4.a;
								if (item.q && (_Utils_cmp(
									$elm$core$List$length(state.bZ),
									$author$project$Menu$maxOutstanding) > -1)) {
									return _Utils_Tuple2(
										_Utils_update(
											state,
											{
												d: $elm$core$Maybe$Just(
													_Utils_update(
														menu,
														{
															bx: $author$project$Menu$Refused('Outstanding operation limit reached; reconcile existing requests.')
														}))
											}),
										_List_Nil);
								} else {
									if (item.q) {
										var intent = state.aW;
										var entry = {co: target, ae: intent, Z: false};
										return _Utils_Tuple2(
											_Utils_update(
												state,
												{
													d: $elm$core$Maybe$Just(
														_Utils_update(
															menu,
															{
																cN: $elm$core$Maybe$Just(index),
																bx: $author$project$Menu$Pending(intent)
															})),
													aW: state.aW + 1,
													bZ: A2($elm$core$List$cons, entry, state.bZ)
												}),
											_List_fromArray(
												[
													A3($author$project$Menu$Dispatch, intent, target, item.t)
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
							return _Utils_eq(entry.ae, intent) && _Utils_eq(entry.co, receiptBinding);
						},
						state.bZ));
				if (_v5.$ === 1) {
					return unchanged;
				} else {
					var entry = _v5.a;
					var outcome = $author$project$Menu$boundedOutcome(receivedOutcome);
					var outstanding = _Utils_eq(outcome, $author$project$Menu$Uncertain) ? A2(
						$elm$core$List$map,
						function (current) {
							return _Utils_eq(current.ae, intent) ? _Utils_update(
								current,
								{Z: true}) : current;
						},
						state.bZ) : A2(
						$elm$core$List$filter,
						function (current) {
							return !_Utils_eq(current.ae, intent);
						},
						state.bZ);
					var menu = A2(
						$elm$core$Maybe$andThen,
						function (current) {
							if (!A2($author$project$Menu$awaits, intent, current.bx)) {
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
													bx: $author$project$Menu$Refused(reason)
												}));
									case 2:
										return $elm$core$Maybe$Just(
											_Utils_update(
												current,
												{bx: $author$project$Menu$Cancelled}));
									default:
										return $elm$core$Maybe$Just(
											_Utils_update(
												current,
												{
													bx: $author$project$Menu$Unknown(intent)
												}));
								}
							}
						},
						state.d);
					return _Utils_Tuple2(
						_Utils_update(
							state,
							{
								aT: $elm$core$Maybe$Just(
									_Utils_Tuple2(intent, outcome)),
								d: menu,
								bZ: outstanding
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
				if (A2($elm$core$List$member, target, state.I) || state.z) {
					return unchanged;
				} else {
					if (_Utils_cmp(
						$elm$core$List$length(state.I) + $elm$core$List$length(state.L),
						$author$project$Menu$maxRetired) > -1) {
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{z: true, d: $elm$core$Maybe$Nothing}),
							_List_Nil);
					} else {
						var menu = A2(
							$elm$core$Maybe$andThen,
							function (current) {
								return _Utils_eq(current.co, target) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(current);
							},
							state.d);
						var invalidated = A2($elm$core$List$cons, target, state.I);
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{I: invalidated, d: menu}),
							_List_Nil);
					}
				}
			default:
				var output = message.a;
				var generation = message.b;
				var retired = _Utils_Tuple2(output, generation);
				if (A2($elm$core$List$member, retired, state.L) || state.z) {
					return unchanged;
				} else {
					if (_Utils_cmp(
						$elm$core$List$length(state.I) + $elm$core$List$length(state.L),
						$author$project$Menu$maxRetired) > -1) {
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{z: true, d: $elm$core$Maybe$Nothing}),
							_List_Nil);
					} else {
						var retiredOutputs = A2($elm$core$List$cons, retired, state.L);
						var menu = A2(
							$elm$core$Maybe$andThen,
							function (current) {
								return _Utils_eq(
									$author$project$Menu$outputTuple(current.co),
									retired) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(current);
							},
							state.d);
						return _Utils_Tuple2(
							_Utils_update(
								state,
								{d: menu, L: retiredOutputs}),
							_List_Nil);
					}
				}
		}
	});
var $author$project$DesignDemo$initial = function (topic) {
	return {
		aK: A2($elm$json$Json$Encode$list, $elm$core$Basics$identity, _List_Nil),
		a6: '',
		aR: $elm$core$Maybe$Nothing,
		d: A2(
			$author$project$Menu$update,
			A2($author$project$Menu$Open, $author$project$DesignDemo$fixtureBinding, $author$project$DesignDemo$items),
			$author$project$Menu$init).a,
		aj: $author$project$DesignDemo$initialPreview,
		ak: 'inactive',
		ba: 1,
		o: topic
	};
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
var $author$project$DesignDemo$family = function (profile) {
	return {
		cl: profile === 'active',
		bf: 'fixture-terminal',
		bg: profile !== 'unavailable',
		bP: 'Terminal',
		au: profile === 'minimized',
		cM: A2(
			$elm$core$Result$withDefault,
			$author$project$UInt64$zero,
			A2(
				$elm$json$Json$Decode$decodeValue,
				$author$project$UInt64$decoder,
				$elm$json$Json$Encode$string('4')))
	};
};
var $author$project$Effects$Activate = 2;
var $author$project$Taskbar$Apply = F2(
	function (a, b) {
		return {$: 2, a: a, b: b};
	});
var $author$project$Taskbar$Launch = {$: 0};
var $author$project$Effects$Minimize = 0;
var $author$project$Taskbar$Picker = {$: 1};
var $author$project$Effects$Restore = 1;
var $author$project$Taskbar$Unavailable = {$: 3};
var $author$project$Taskbar$primary = F2(
	function (pinned, families) {
		if (!families.b) {
			return pinned ? $author$project$Taskbar$Launch : $author$project$Taskbar$Unavailable;
		} else {
			if (!families.b.b) {
				var entry = families.a;
				return (!entry.bg) ? $author$project$Taskbar$Unavailable : (entry.au ? A2($author$project$Taskbar$Apply, 1, entry.cM) : (entry.cl ? A2($author$project$Taskbar$Apply, 0, entry.cM) : A2($author$project$Taskbar$Apply, 2, entry.cM)));
			} else {
				return $author$project$Taskbar$Picker;
			}
		}
	});
var $author$project$DesignDemo$decision = function (profile) {
	var families = (profile === 'empty') ? _List_Nil : ((profile === 'multiple') ? _List_fromArray(
		[
			$author$project$DesignDemo$family('active'),
			$author$project$DesignDemo$family('inactive')
		]) : _List_fromArray(
		[
			$author$project$DesignDemo$family(profile)
		]));
	var _v0 = A2($author$project$Taskbar$primary, false, families);
	switch (_v0.$) {
		case 0:
			return 'Launch (function-level; not reached by this call)';
		case 1:
			return 'Open window picker';
		case 3:
			return 'Unavailable';
		default:
			var operation = _v0.a;
			switch (operation) {
				case 1:
					return 'Request restore';
				case 0:
					return 'Request minimize';
				case 2:
					return 'Request activate';
				case 3:
					return 'Request maximize (not returned by primary)';
				default:
					return 'Request geometry restore (not returned by primary)';
			}
	}
};
var $elm$json$Json$Encode$int = _Json_wrap;
var $author$project$Menu$snapshot = function (_v0) {
	var state = _v0;
	return {
		z: state.z,
		bN: $elm$core$List$length(state.I),
		aT: state.aT,
		d: state.d,
		bZ: $elm$core$List$length(state.bZ),
		am: $elm$core$List$length(state.am),
		b6: $elm$core$List$length(state.L)
	};
};
var $author$project$DesignDemo$notice = function (model) {
	var _v0 = $author$project$Menu$snapshot(model.d).d;
	if (_v0.$ === 1) {
		return 'Menu closed. Outstanding requests: ' + $elm$core$String$fromInt(
			$author$project$Menu$snapshot(model.d).bZ);
	} else {
		var menu = _v0.a;
		var _v1 = menu.bx;
		switch (_v1.$) {
			case 0:
				return 'Ready';
			case 1:
				return 'Applying window change…';
			case 4:
				return 'Outcome unconfirmed. Reconcile before repeating.';
			case 2:
				var reason = _v1.a;
				return reason;
			default:
				return 'Cancelled';
		}
	}
};
var $elm$json$Json$Encode$null = _Json_encodeNull;
var $author$project$PreviewLifecycle$acceptedPacket = function (st) {
	return A2(
		$elm$core$Maybe$map,
		function (_v0) {
			var packet = _v0;
			return packet;
		},
		st.aa);
};
var $author$project$PreviewLifecycle$candidate = function (st) {
	var _v0 = st.e;
	if (_v0.$ === 2) {
		var frame = _v0.a;
		return $elm$core$Maybe$Just(frame);
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$PreviewLifecycle$drawablePacket = function (current) {
	switch (current.$) {
		case 0:
			var packet = current.a;
			return $elm$core$Maybe$Just(packet);
		case 1:
			var packet = current.a;
			return $elm$core$Maybe$Just(packet);
		default:
			return $elm$core$Maybe$Nothing;
	}
};
var $author$project$UInt64$string = function (_v0) {
	var value = _v0;
	return value;
};
var $author$project$PreviewIdentity$string = function (_v0) {
	var counter = _v0;
	return $author$project$UInt64$string(counter);
};
var $author$project$PreviewIdentity$encode = A2($elm$core$Basics$composeR, $author$project$PreviewIdentity$string, $elm$json$Json$Encode$string);
var $author$project$PreviewLifecycle$encodeBinding = function (binding) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'lifetime',
				$author$project$PreviewIdentity$encode(binding.af)),
				_Utils_Tuple2(
				'session',
				$author$project$PreviewIdentity$encode(binding.b8)),
				_Utils_Tuple2(
				'frontend',
				$author$project$PreviewIdentity$encode(binding.bK))
			]));
};
var $author$project$PreviewLifecycle$encodeContext = function (context) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'lifetime',
				$author$project$PreviewIdentity$encode(context.af)),
				_Utils_Tuple2(
				'incarnation',
				$author$project$PreviewIdentity$encode(context.w)),
				_Utils_Tuple2(
				'output',
				$author$project$PreviewIdentity$encode(context.cG)),
				_Utils_Tuple2(
				'privacy',
				$author$project$PreviewIdentity$encode(context.aw)),
				_Utils_Tuple2(
				'rendering',
				$author$project$PreviewIdentity$encode(context.aA)),
				_Utils_Tuple2(
				'scene',
				$author$project$PreviewIdentity$encode(context.M)),
				_Utils_Tuple2(
				'content',
				$author$project$PreviewIdentity$encode(context.T))
			]));
};
var $author$project$PreviewLifecycle$encodeJob = function (job) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'binding',
				$author$project$PreviewLifecycle$encodeBinding(job.co)),
				_Utils_Tuple2(
				'context',
				$author$project$PreviewLifecycle$encodeContext(job.h)),
				_Utils_Tuple2(
				'request',
				$author$project$PreviewIdentity$encode(job.m)),
				_Utils_Tuple2(
				'origin',
				$author$project$PreviewIdentity$encode(job.bq)),
				_Utils_Tuple2(
				'clock',
				$author$project$PreviewIdentity$encode(job.p)),
				_Utils_Tuple2(
				'deadline',
				$author$project$PreviewIdentity$encode(job.C))
			]));
};
var $author$project$PreviewLifecycle$ClientContent = 0;
var $author$project$PreviewLifecycle$handleString = function (_v0) {
	var value = _v0;
	return value;
};
var $author$project$PreviewLifecycle$encodePacket = function (packet) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'job',
				$author$project$PreviewLifecycle$encodeJob(packet.c)),
				_Utils_Tuple2(
				'handle',
				$elm$json$Json$Encode$string(
					$author$project$PreviewLifecycle$handleString(packet.E))),
				_Utils_Tuple2(
				'owned',
				$elm$json$Json$Encode$bool(packet.a9)),
				_Utils_Tuple2(
				'signaled',
				$elm$json$Json$Encode$bool(packet.bc)),
				_Utils_Tuple2(
				'fidelity',
				$elm$json$Json$Encode$string(
					(!packet.a7) ? 'client' : 'family')),
				_Utils_Tuple2(
				'coverage',
				A2(
					$elm$json$Json$Encode$list,
					$elm$json$Json$Encode$string,
					$elm$core$Set$toList(packet.a3))),
				_Utils_Tuple2(
				'expires',
				$author$project$PreviewIdentity$encode(packet.aL))
			]));
};
var $author$project$PreviewLifecycle$encodeScope = function (scope) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'binding',
				$author$project$PreviewLifecycle$encodeBinding(scope.co)),
				_Utils_Tuple2(
				'context',
				$author$project$PreviewLifecycle$encodeContext(scope.h)),
				_Utils_Tuple2(
				'observation',
				$author$project$PreviewIdentity$encode(scope.a8)),
				_Utils_Tuple2(
				'clock',
				$author$project$PreviewIdentity$encode(scope.p)),
				_Utils_Tuple2(
				'now',
				$author$project$PreviewIdentity$encode(scope.B)),
				_Utils_Tuple2(
				'present',
				$elm$json$Json$Encode$bool(scope.aY)),
				_Utils_Tuple2(
				'sourceLive',
				$elm$json$Json$Encode$bool(scope.aC)),
				_Utils_Tuple2(
				'locked',
				$elm$json$Json$Encode$bool(scope.ag)),
				_Utils_Tuple2(
				'gpuReady',
				$elm$json$Json$Encode$bool(scope.aP))
			]));
};
var $author$project$PreviewLifecycle$Historical = function (a) {
	return {$: 1, a: a};
};
var $author$project$PreviewLifecycle$Live = function (a) {
	return {$: 0, a: a};
};
var $elm$core$Basics$compare = _Utils_compare;
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
var $author$project$PreviewIdentity$compare = F2(
	function (_v0, _v1) {
		var a = _v0;
		var b = _v1;
		return A2($author$project$UInt64$compare, a, b);
	});
var $author$project$PreviewLifecycle$before = F2(
	function (a, b) {
		return !A2($author$project$PreviewIdentity$compare, a, b);
	});
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
var $author$project$PreviewLifecycle$generationMatches = F2(
	function (a, b) {
		return _Utils_eq(a.af, b.af) && (_Utils_eq(a.w, b.w) && (_Utils_eq(a.cG, b.cG) && (_Utils_eq(a.aw, b.aw) && _Utils_eq(a.aA, b.aA))));
	});
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
var $elm$core$Dict$member = F2(
	function (key, dict) {
		var _v0 = A2($elm$core$Dict$get, key, dict);
		if (!_v0.$) {
			return true;
		} else {
			return false;
		}
	});
var $elm$core$Set$member = F2(
	function (key, _v0) {
		var dict = _v0;
		return A2($elm$core$Dict$member, key, dict);
	});
var $author$project$PreviewLifecycle$notAfter = F2(
	function (a, b) {
		return A2($author$project$PreviewIdentity$compare, a, b) !== 2;
	});
var $author$project$PreviewLifecycle$authorized = F2(
	function (st, frame) {
		return (!st.ac) && (st.a.aY && ((!st.a.ag) && (st.a.aP && (frame.a9 && (_Utils_eq(frame.c.co, st.a.co) && (_Utils_eq(frame.c.p, st.a.p) && (A2($author$project$PreviewLifecycle$generationMatches, st.a.h, frame.c.h) && (A2($author$project$PreviewLifecycle$notAfter, frame.c.h.M, st.a.h.M) && (A2($author$project$PreviewLifecycle$notAfter, frame.c.h.T, st.a.h.T) && (A2($author$project$PreviewLifecycle$before, st.a.B, frame.aL) && (A2($elm$core$Set$member, 'client', frame.a3) && ((!frame.a7) || _Utils_eq(
			frame.a3,
			$elm$core$Set$fromList(
				_List_fromArray(
					['client', 'decoration', 'modal', 'popup'])))))))))))))));
	});
var $author$project$PreviewLifecycle$Loading = {$: 2};
var $author$project$PreviewLifecycle$Unavailable = {$: 3};
var $author$project$PreviewLifecycle$loadingStatus = function (st) {
	return (st.D && (!_Utils_eq(st.e, $author$project$PreviewLifecycle$Idle))) ? $author$project$PreviewLifecycle$Loading : $author$project$PreviewLifecycle$Unavailable;
};
var $author$project$PreviewLifecycle$status = function (st) {
	var _v0 = st.aa;
	if (!_v0.$) {
		var lease = _v0.a;
		var frame = lease;
		return (st.D && A2($author$project$PreviewLifecycle$authorized, st, frame)) ? ((st.a.aC && (_Utils_eq(frame.c.h.M, st.a.h.M) && _Utils_eq(frame.c.h.T, st.a.h.T))) ? $author$project$PreviewLifecycle$Live(lease) : $author$project$PreviewLifecycle$Historical(lease)) : $author$project$PreviewLifecycle$loadingStatus(st);
	} else {
		return $author$project$PreviewLifecycle$loadingStatus(st);
	}
};
var $author$project$PreviewLifecycle$statusName = function (current) {
	switch (current.$) {
		case 0:
			return 'live';
		case 1:
			return 'historical';
		case 2:
			return 'loading';
		default:
			return 'unavailable';
	}
};
var $elm$core$Maybe$withDefault = F2(
	function (_default, maybe) {
		if (!maybe.$) {
			var value = maybe.a;
			return value;
		} else {
			return _default;
		}
	});
var $author$project$PreviewLifecycle$observe = function (_v0) {
	var st = _v0;
	var maybe = F2(
		function (encode, value) {
			return A2(
				$elm$core$Maybe$withDefault,
				$elm$json$Json$Encode$null,
				A2($elm$core$Maybe$map, encode, value));
		});
	var job = function () {
		var _v1 = st.e;
		if (_v1.$ === 1) {
			var active = _v1.a;
			return $elm$core$Maybe$Just(active);
		} else {
			return $elm$core$Maybe$Nothing;
		}
	}();
	var current = $author$project$PreviewLifecycle$status(st);
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'scope',
				$author$project$PreviewLifecycle$encodeScope(st.a)),
				_Utils_Tuple2(
				'demand',
				$elm$json$Json$Encode$bool(st.D)),
				_Utils_Tuple2(
				'ready',
				$elm$json$Json$Encode$bool(!st.ac)),
				_Utils_Tuple2(
				'nextRequest',
				A2(maybe, $author$project$PreviewIdentity$encode, st.av)),
				_Utils_Tuple2(
				'job',
				A2(maybe, $author$project$PreviewLifecycle$encodeJob, job)),
				_Utils_Tuple2(
				'candidate',
				A2(
					maybe,
					$author$project$PreviewLifecycle$encodePacket,
					$author$project$PreviewLifecycle$candidate(st))),
				_Utils_Tuple2(
				'accepted',
				A2(
					maybe,
					$author$project$PreviewLifecycle$encodePacket,
					$author$project$PreviewLifecycle$acceptedPacket(st))),
				_Utils_Tuple2(
				'known',
				A2($elm$json$Json$Encode$list, $author$project$PreviewLifecycle$encodeJob, st.bO)),
				_Utils_Tuple2(
				'cancelling',
				A2($elm$json$Json$Encode$list, $author$project$PreviewLifecycle$encodeJob, st.x)),
				_Utils_Tuple2(
				'retiring',
				A2($elm$json$Json$Encode$list, $author$project$PreviewLifecycle$encodePacket, st.r)),
				_Utils_Tuple2(
				'state',
				$elm$json$Json$Encode$string(
					$author$project$PreviewLifecycle$statusName(current))),
				_Utils_Tuple2(
				'image',
				A2(
					maybe,
					A2(
						$elm$core$Basics$composeR,
						function ($) {
							return $.E;
						},
						A2(
							$elm$core$Basics$composeR,
							$author$project$PreviewLifecycle$handleString,
							A2(
								$elm$core$Basics$composeR,
								$elm$core$Basics$append('elm-shell://preview/'),
								$elm$json$Json$Encode$string))),
					$author$project$PreviewLifecycle$drawablePacket(current)))
			]));
};
var $author$project$DesignDemo$observe = function (model) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'topic',
				$elm$json$Json$Encode$string(model.o)),
				_Utils_Tuple2(
				'menuStatus',
				$elm$json$Json$Encode$string(
					$author$project$DesignDemo$notice(model))),
				_Utils_Tuple2(
				'outstanding',
				$elm$json$Json$Encode$int(
					$author$project$Menu$snapshot(model.d).bZ)),
				_Utils_Tuple2('effects', model.aK),
				_Utils_Tuple2(
				'decision',
				$elm$json$Json$Encode$string(
					$author$project$DesignDemo$decision(model.ak))),
				_Utils_Tuple2(
				'preview',
				A2(
					$elm$core$Maybe$withDefault,
					$elm$json$Json$Encode$null,
					A2($elm$core$Maybe$map, $author$project$PreviewLifecycle$observe, model.aj))),
				_Utils_Tuple2(
				'error',
				$elm$json$Json$Encode$string(model.a6))
			]));
};
var $author$project$Menu$Activate = F3(
	function (a, b, c) {
		return {$: 3, a: a, b: b, c: c};
	});
var $author$project$Menu$Cancellation = {$: 2};
var $author$project$Menu$Committed = {$: 0};
var $author$project$Menu$Dismiss = function (a) {
	return {$: 5, a: a};
};
var $author$project$Menu$Down = 1;
var $author$project$Menu$End = 3;
var $author$project$Menu$Home = 2;
var $author$project$Menu$Navigate = F2(
	function (a, b) {
		return {$: 2, a: a, b: b};
	});
var $author$project$Menu$ReceiveFor = F3(
	function (a, b, c) {
		return {$: 4, a: a, b: b, c: c};
	});
var $author$project$Menu$Up = 0;
var $author$project$CapturedAction$CapturedAction = $elm$core$Basics$identity;
var $elm$core$String$any = _String_any;
var $elm$json$Json$Decode$int = _Json_decodeInt;
var $elm$json$Json$Decode$map6 = _Json_map6;
var $author$project$CapturedAction$decode = function (raw) {
	var fields = _List_fromArray(
		['id', 'kind', 'lease', 'publication', 'surface', 'surfaceProtocol']);
	var decoder = A2(
		$elm$json$Json$Decode$andThen,
		function (pairs) {
			return (!_Utils_eq(
				$elm$core$List$sort(
					A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
				fields)) ? $elm$json$Json$Decode$fail('Action fields') : A2(
				$elm$json$Json$Decode$andThen,
				function (_v0) {
					var version = _v0.a;
					var kind = _v0.b;
					var value = _v0.c;
					return ((version === 2) && ((kind === 'surface-action') && ((!_Utils_eq(value.ba, $author$project$UInt64$zero)) && (A2(
						$elm$core$List$member,
						value.be,
						_List_fromArray(
							['bar', 'popup'])) && ((!$elm$core$String$isEmpty(value.aq)) && (($elm$core$String$length(value.aq) <= 512) && (!A2(
						$elm$core$String$any,
						function (c) {
							return $elm$core$Char$toCode(c) < 32;
						},
						value.aq)))))))) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Action scope');
				},
				A7(
					$elm$json$Json$Decode$map6,
					F6(
						function (version, kind, shown, scoped, role, name) {
							return _Utils_Tuple3(
								version,
								kind,
								{aq: name, bn: scoped, ba: shown, be: role});
						}),
					A2($elm$json$Json$Decode$field, 'surfaceProtocol', $elm$json$Json$Decode$int),
					A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
					A2($elm$json$Json$Decode$field, 'publication', $author$project$UInt64$decoder),
					A2($elm$json$Json$Decode$field, 'lease', $author$project$UInt64$decoder),
					A2($elm$json$Json$Decode$field, 'surface', $elm$json$Json$Decode$string),
					A2($elm$json$Json$Decode$field, 'id', $elm$json$Json$Decode$string)));
		},
		$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	return A2($elm$json$Json$Decode$decodeValue, decoder, raw);
};
var $author$project$SurfaceRenderer$enabled = F3(
	function (popup, identity, _v0) {
		var snapshot = _v0;
		return A2(
			$elm$core$List$any,
			function (control) {
				return _Utils_eq(control.aq, identity) && control.q;
			},
			popup ? snapshot.Y : snapshot.ab);
	});
var $author$project$CapturedAction$identity = function (_v0) {
	var value = _v0;
	return value.aq;
};
var $author$project$CapturedAction$lease = function (_v0) {
	var value = _v0;
	return value.bn;
};
var $author$project$SurfaceRenderer$lease = function (_v0) {
	var snapshot = _v0;
	return snapshot.bn;
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
var $author$project$DesignDemo$menuUpdate = F2(
	function (message, model) {
		var _v0 = A2($author$project$Menu$update, message, model.d);
		var next = _v0.a;
		var effects = _v0.b;
		var pending = A2(
			$elm$core$Maybe$map,
			function (effect) {
				var intent = effect.a;
				var binding = effect.b;
				return _Utils_Tuple2(intent, binding);
			},
			$elm$core$List$head(effects));
		return _Utils_update(
			model,
			{
				aK: $elm$json$Json$Encode$object(
					_List_fromArray(
						[
							_Utils_Tuple2(
							'dispatches',
							$elm$json$Json$Encode$int(
								$elm$core$List$length(effects)))
						])),
				aR: _Utils_eq(pending, $elm$core$Maybe$Nothing) ? model.aR : pending,
				d: next
			});
	});
var $author$project$PreviewLifecycle$encodeCommands = function (commands) {
	return A2(
		$elm$json$Json$Encode$list,
		function (command) {
			switch (command.$) {
				case 4:
					var job = command.a;
					var sequence = command.b;
					return $elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'kind',
								$elm$json$Json$Encode$string('acknowledge')),
								_Utils_Tuple2(
								'job',
								$author$project$PreviewLifecycle$encodeJob(job)),
								_Utils_Tuple2(
								'sequence',
								$author$project$PreviewIdentity$encode(sequence))
							]));
				case 0:
					var job = command.a;
					return $elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'kind',
								$elm$json$Json$Encode$string('acquire')),
								_Utils_Tuple2(
								'job',
								$author$project$PreviewLifecycle$encodeJob(job))
							]));
				case 1:
					var job = command.a;
					return $elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'kind',
								$elm$json$Json$Encode$string('cancel')),
								_Utils_Tuple2(
								'job',
								$author$project$PreviewLifecycle$encodeJob(job))
							]));
				case 2:
					var packet = command.a;
					return $elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'kind',
								$elm$json$Json$Encode$string('release')),
								_Utils_Tuple2(
								'frame',
								$author$project$PreviewLifecycle$encodePacket(packet))
							]));
				default:
					var binding = command.a;
					return $elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'kind',
								$elm$json$Json$Encode$string('reconcile')),
								_Utils_Tuple2(
								'binding',
								$author$project$PreviewLifecycle$encodeBinding(binding))
							]));
			}
		},
		commands);
};
var $author$project$PreviewLifecycle$Receipt = F2(
	function (a, b) {
		return {$: 13, a: a, b: b};
	});
var $author$project$PreviewLifecycle$Attach = F2(
	function (a, b) {
		return {$: 6, a: a, b: b};
	});
var $author$project$PreviewLifecycle$Cancelled = function (a) {
	return {$: 8, a: a};
};
var $author$project$PreviewLifecycle$Clock = F3(
	function (a, b, c) {
		return {$: 7, a: a, b: b, c: c};
	});
var $author$project$PreviewLifecycle$Close = {$: 1};
var $author$project$PreviewLifecycle$Exhausted = function (a) {
	return {$: 11, a: a};
};
var $author$project$PreviewLifecycle$Expired = function (a) {
	return {$: 10, a: a};
};
var $author$project$PreviewLifecycle$Fence = function (a) {
	return {$: 4, a: a};
};
var $author$project$PreviewLifecycle$Observe = function (a) {
	return {$: 5, a: a};
};
var $author$project$PreviewLifecycle$Offer = function (a) {
	return {$: 3, a: a};
};
var $author$project$PreviewLifecycle$Open = {$: 0};
var $author$project$PreviewLifecycle$Refused = function (a) {
	return {$: 12, a: a};
};
var $author$project$PreviewLifecycle$Released = function (a) {
	return {$: 9, a: a};
};
var $author$project$PreviewLifecycle$Request = function (a) {
	return {$: 2, a: a};
};
var $author$project$PreviewLifecycle$Job = F6(
	function (binding, context, request, origin, clock, deadline) {
		return {co: binding, p: clock, h: context, C: deadline, bq: origin, m: request};
	});
var $author$project$PreviewLifecycle$jobDecoder = A2(
	$author$project$PreviewLifecycle$strict,
	_List_fromArray(
		['binding', 'context', 'request', 'origin', 'clock', 'deadline']),
	A7(
		$elm$json$Json$Decode$map6,
		$author$project$PreviewLifecycle$Job,
		A2($elm$json$Json$Decode$field, 'binding', $author$project$PreviewLifecycle$bindingDecoder),
		A2($elm$json$Json$Decode$field, 'context', $author$project$PreviewLifecycle$contextDecoder),
		A2($elm$json$Json$Decode$field, 'request', $author$project$PreviewIdentity$positive),
		A2($elm$json$Json$Decode$field, 'origin', $author$project$PreviewIdentity$positive),
		A2($elm$json$Json$Decode$field, 'clock', $author$project$PreviewIdentity$positive),
		A2($elm$json$Json$Decode$field, 'deadline', $author$project$PreviewIdentity$positive)));
var $author$project$PreviewLifecycle$ComposedFamily = 1;
var $author$project$PreviewLifecycle$LeaseHandle = $elm$core$Basics$identity;
var $author$project$PreviewLifecycle$Packet = F7(
	function (job, handle, owned, signaled, fidelity, coverage, expires) {
		return {a3: coverage, aL: expires, a7: fidelity, E: handle, c: job, a9: owned, bc: signaled};
	});
var $elm$core$Dict$foldl = F3(
	function (func, acc, dict) {
		foldl:
		while (true) {
			if (dict.$ === -2) {
				return acc;
			} else {
				var key = dict.b;
				var value = dict.c;
				var left = dict.d;
				var right = dict.e;
				var $temp$func = func,
					$temp$acc = A3(
					func,
					key,
					value,
					A3($elm$core$Dict$foldl, func, acc, left)),
					$temp$dict = right;
				func = $temp$func;
				acc = $temp$acc;
				dict = $temp$dict;
				continue foldl;
			}
		}
	});
var $elm$core$Dict$getMin = function (dict) {
	getMin:
	while (true) {
		if ((dict.$ === -1) && (dict.d.$ === -1)) {
			var left = dict.d;
			var $temp$dict = left;
			dict = $temp$dict;
			continue getMin;
		} else {
			return dict;
		}
	}
};
var $elm$core$Dict$moveRedLeft = function (dict) {
	if (((dict.$ === -1) && (dict.d.$ === -1)) && (dict.e.$ === -1)) {
		if ((dict.e.d.$ === -1) && (!dict.e.d.a)) {
			var clr = dict.a;
			var k = dict.b;
			var v = dict.c;
			var _v1 = dict.d;
			var lClr = _v1.a;
			var lK = _v1.b;
			var lV = _v1.c;
			var lLeft = _v1.d;
			var lRight = _v1.e;
			var _v2 = dict.e;
			var rClr = _v2.a;
			var rK = _v2.b;
			var rV = _v2.c;
			var rLeft = _v2.d;
			var _v3 = rLeft.a;
			var rlK = rLeft.b;
			var rlV = rLeft.c;
			var rlL = rLeft.d;
			var rlR = rLeft.e;
			var rRight = _v2.e;
			return A5(
				$elm$core$Dict$RBNode_elm_builtin,
				0,
				rlK,
				rlV,
				A5(
					$elm$core$Dict$RBNode_elm_builtin,
					1,
					k,
					v,
					A5($elm$core$Dict$RBNode_elm_builtin, 0, lK, lV, lLeft, lRight),
					rlL),
				A5($elm$core$Dict$RBNode_elm_builtin, 1, rK, rV, rlR, rRight));
		} else {
			var clr = dict.a;
			var k = dict.b;
			var v = dict.c;
			var _v4 = dict.d;
			var lClr = _v4.a;
			var lK = _v4.b;
			var lV = _v4.c;
			var lLeft = _v4.d;
			var lRight = _v4.e;
			var _v5 = dict.e;
			var rClr = _v5.a;
			var rK = _v5.b;
			var rV = _v5.c;
			var rLeft = _v5.d;
			var rRight = _v5.e;
			if (clr === 1) {
				return A5(
					$elm$core$Dict$RBNode_elm_builtin,
					1,
					k,
					v,
					A5($elm$core$Dict$RBNode_elm_builtin, 0, lK, lV, lLeft, lRight),
					A5($elm$core$Dict$RBNode_elm_builtin, 0, rK, rV, rLeft, rRight));
			} else {
				return A5(
					$elm$core$Dict$RBNode_elm_builtin,
					1,
					k,
					v,
					A5($elm$core$Dict$RBNode_elm_builtin, 0, lK, lV, lLeft, lRight),
					A5($elm$core$Dict$RBNode_elm_builtin, 0, rK, rV, rLeft, rRight));
			}
		}
	} else {
		return dict;
	}
};
var $elm$core$Dict$moveRedRight = function (dict) {
	if (((dict.$ === -1) && (dict.d.$ === -1)) && (dict.e.$ === -1)) {
		if ((dict.d.d.$ === -1) && (!dict.d.d.a)) {
			var clr = dict.a;
			var k = dict.b;
			var v = dict.c;
			var _v1 = dict.d;
			var lClr = _v1.a;
			var lK = _v1.b;
			var lV = _v1.c;
			var _v2 = _v1.d;
			var _v3 = _v2.a;
			var llK = _v2.b;
			var llV = _v2.c;
			var llLeft = _v2.d;
			var llRight = _v2.e;
			var lRight = _v1.e;
			var _v4 = dict.e;
			var rClr = _v4.a;
			var rK = _v4.b;
			var rV = _v4.c;
			var rLeft = _v4.d;
			var rRight = _v4.e;
			return A5(
				$elm$core$Dict$RBNode_elm_builtin,
				0,
				lK,
				lV,
				A5($elm$core$Dict$RBNode_elm_builtin, 1, llK, llV, llLeft, llRight),
				A5(
					$elm$core$Dict$RBNode_elm_builtin,
					1,
					k,
					v,
					lRight,
					A5($elm$core$Dict$RBNode_elm_builtin, 0, rK, rV, rLeft, rRight)));
		} else {
			var clr = dict.a;
			var k = dict.b;
			var v = dict.c;
			var _v5 = dict.d;
			var lClr = _v5.a;
			var lK = _v5.b;
			var lV = _v5.c;
			var lLeft = _v5.d;
			var lRight = _v5.e;
			var _v6 = dict.e;
			var rClr = _v6.a;
			var rK = _v6.b;
			var rV = _v6.c;
			var rLeft = _v6.d;
			var rRight = _v6.e;
			if (clr === 1) {
				return A5(
					$elm$core$Dict$RBNode_elm_builtin,
					1,
					k,
					v,
					A5($elm$core$Dict$RBNode_elm_builtin, 0, lK, lV, lLeft, lRight),
					A5($elm$core$Dict$RBNode_elm_builtin, 0, rK, rV, rLeft, rRight));
			} else {
				return A5(
					$elm$core$Dict$RBNode_elm_builtin,
					1,
					k,
					v,
					A5($elm$core$Dict$RBNode_elm_builtin, 0, lK, lV, lLeft, lRight),
					A5($elm$core$Dict$RBNode_elm_builtin, 0, rK, rV, rLeft, rRight));
			}
		}
	} else {
		return dict;
	}
};
var $elm$core$Dict$removeHelpPrepEQGT = F7(
	function (targetKey, dict, color, key, value, left, right) {
		if ((left.$ === -1) && (!left.a)) {
			var _v1 = left.a;
			var lK = left.b;
			var lV = left.c;
			var lLeft = left.d;
			var lRight = left.e;
			return A5(
				$elm$core$Dict$RBNode_elm_builtin,
				color,
				lK,
				lV,
				lLeft,
				A5($elm$core$Dict$RBNode_elm_builtin, 0, key, value, lRight, right));
		} else {
			_v2$2:
			while (true) {
				if ((right.$ === -1) && (right.a === 1)) {
					if (right.d.$ === -1) {
						if (right.d.a === 1) {
							var _v3 = right.a;
							var _v4 = right.d;
							var _v5 = _v4.a;
							return $elm$core$Dict$moveRedRight(dict);
						} else {
							break _v2$2;
						}
					} else {
						var _v6 = right.a;
						var _v7 = right.d;
						return $elm$core$Dict$moveRedRight(dict);
					}
				} else {
					break _v2$2;
				}
			}
			return dict;
		}
	});
var $elm$core$Dict$removeMin = function (dict) {
	if ((dict.$ === -1) && (dict.d.$ === -1)) {
		var color = dict.a;
		var key = dict.b;
		var value = dict.c;
		var left = dict.d;
		var lColor = left.a;
		var lLeft = left.d;
		var right = dict.e;
		if (lColor === 1) {
			if ((lLeft.$ === -1) && (!lLeft.a)) {
				var _v3 = lLeft.a;
				return A5(
					$elm$core$Dict$RBNode_elm_builtin,
					color,
					key,
					value,
					$elm$core$Dict$removeMin(left),
					right);
			} else {
				var _v4 = $elm$core$Dict$moveRedLeft(dict);
				if (_v4.$ === -1) {
					var nColor = _v4.a;
					var nKey = _v4.b;
					var nValue = _v4.c;
					var nLeft = _v4.d;
					var nRight = _v4.e;
					return A5(
						$elm$core$Dict$balance,
						nColor,
						nKey,
						nValue,
						$elm$core$Dict$removeMin(nLeft),
						nRight);
				} else {
					return $elm$core$Dict$RBEmpty_elm_builtin;
				}
			}
		} else {
			return A5(
				$elm$core$Dict$RBNode_elm_builtin,
				color,
				key,
				value,
				$elm$core$Dict$removeMin(left),
				right);
		}
	} else {
		return $elm$core$Dict$RBEmpty_elm_builtin;
	}
};
var $elm$core$Dict$removeHelp = F2(
	function (targetKey, dict) {
		if (dict.$ === -2) {
			return $elm$core$Dict$RBEmpty_elm_builtin;
		} else {
			var color = dict.a;
			var key = dict.b;
			var value = dict.c;
			var left = dict.d;
			var right = dict.e;
			if (_Utils_cmp(targetKey, key) < 0) {
				if ((left.$ === -1) && (left.a === 1)) {
					var _v4 = left.a;
					var lLeft = left.d;
					if ((lLeft.$ === -1) && (!lLeft.a)) {
						var _v6 = lLeft.a;
						return A5(
							$elm$core$Dict$RBNode_elm_builtin,
							color,
							key,
							value,
							A2($elm$core$Dict$removeHelp, targetKey, left),
							right);
					} else {
						var _v7 = $elm$core$Dict$moveRedLeft(dict);
						if (_v7.$ === -1) {
							var nColor = _v7.a;
							var nKey = _v7.b;
							var nValue = _v7.c;
							var nLeft = _v7.d;
							var nRight = _v7.e;
							return A5(
								$elm$core$Dict$balance,
								nColor,
								nKey,
								nValue,
								A2($elm$core$Dict$removeHelp, targetKey, nLeft),
								nRight);
						} else {
							return $elm$core$Dict$RBEmpty_elm_builtin;
						}
					}
				} else {
					return A5(
						$elm$core$Dict$RBNode_elm_builtin,
						color,
						key,
						value,
						A2($elm$core$Dict$removeHelp, targetKey, left),
						right);
				}
			} else {
				return A2(
					$elm$core$Dict$removeHelpEQGT,
					targetKey,
					A7($elm$core$Dict$removeHelpPrepEQGT, targetKey, dict, color, key, value, left, right));
			}
		}
	});
var $elm$core$Dict$removeHelpEQGT = F2(
	function (targetKey, dict) {
		if (dict.$ === -1) {
			var color = dict.a;
			var key = dict.b;
			var value = dict.c;
			var left = dict.d;
			var right = dict.e;
			if (_Utils_eq(targetKey, key)) {
				var _v1 = $elm$core$Dict$getMin(right);
				if (_v1.$ === -1) {
					var minKey = _v1.b;
					var minValue = _v1.c;
					return A5(
						$elm$core$Dict$balance,
						color,
						minKey,
						minValue,
						left,
						$elm$core$Dict$removeMin(right));
				} else {
					return $elm$core$Dict$RBEmpty_elm_builtin;
				}
			} else {
				return A5(
					$elm$core$Dict$balance,
					color,
					key,
					value,
					left,
					A2($elm$core$Dict$removeHelp, targetKey, right));
			}
		} else {
			return $elm$core$Dict$RBEmpty_elm_builtin;
		}
	});
var $elm$core$Dict$remove = F2(
	function (key, dict) {
		var _v0 = A2($elm$core$Dict$removeHelp, key, dict);
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
var $elm$core$Dict$diff = F2(
	function (t1, t2) {
		return A3(
			$elm$core$Dict$foldl,
			F3(
				function (k, v, t) {
					return A2($elm$core$Dict$remove, k, t);
				}),
			t1,
			t2);
	});
var $elm$core$Set$diff = F2(
	function (_v0, _v1) {
		var dict1 = _v0;
		var dict2 = _v1;
		return A2($elm$core$Dict$diff, dict1, dict2);
	});
var $elm$core$Dict$isEmpty = function (dict) {
	if (dict.$ === -2) {
		return true;
	} else {
		return false;
	}
};
var $elm$core$Set$isEmpty = function (_v0) {
	var dict = _v0;
	return $elm$core$Dict$isEmpty(dict);
};
var $elm$json$Json$Decode$list = _Json_decodeList;
var $elm$core$Bitwise$and = _Bitwise_and;
var $elm$core$Bitwise$shiftRightBy = _Bitwise_shiftRightBy;
var $elm$core$String$repeatHelp = F3(
	function (n, chunk, result) {
		return (n <= 0) ? result : A3(
			$elm$core$String$repeatHelp,
			n >> 1,
			_Utils_ap(chunk, chunk),
			(!(n & 1)) ? result : _Utils_ap(result, chunk));
	});
var $elm$core$String$repeat = F2(
	function (n, chunk) {
		return A3($elm$core$String$repeatHelp, n, chunk, '');
	});
var $author$project$PreviewLifecycle$opaqueDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (($elm$core$String$length(value) === 64) && ((!_Utils_eq(
			value,
			A2($elm$core$String$repeat, 64, '0'))) && A2(
			$elm$core$String$all,
			function (c) {
				return ((c >= '0') && (c <= '9')) || ((c >= 'a') && (c <= 'f'));
			},
			value))) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Opaque native resource token');
	},
	$elm$json$Json$Decode$string);
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
var $author$project$PreviewLifecycle$packetDecoder = function () {
	var fidelity = A2(
		$elm$json$Json$Decode$andThen,
		function (value) {
			switch (value) {
				case 'client':
					return $elm$json$Json$Decode$succeed(0);
				case 'family':
					return $elm$json$Json$Decode$succeed(1);
				default:
					return $elm$json$Json$Decode$fail('Preview fidelity');
			}
		},
		$elm$json$Json$Decode$string);
	var coverage = A2(
		$elm$json$Json$Decode$andThen,
		function (values) {
			var unique = $elm$core$Set$fromList(values);
			return (($elm$core$List$length(values) <= 4) && (_Utils_eq(
				$elm$core$List$length(values),
				$elm$core$Set$size(unique)) && $elm$core$Set$isEmpty(
				A2(
					$elm$core$Set$diff,
					unique,
					$elm$core$Set$fromList(
						_List_fromArray(
							['client', 'decoration', 'modal', 'popup'])))))) ? $elm$json$Json$Decode$succeed(unique) : $elm$json$Json$Decode$fail('Preview coverage');
		},
		$elm$json$Json$Decode$list($elm$json$Json$Decode$string));
	return A2(
		$author$project$PreviewLifecycle$strict,
		_List_fromArray(
			['job', 'handle', 'owned', 'signaled', 'fidelity', 'coverage', 'expires']),
		A8(
			$elm$json$Json$Decode$map7,
			$author$project$PreviewLifecycle$Packet,
			A2($elm$json$Json$Decode$field, 'job', $author$project$PreviewLifecycle$jobDecoder),
			A2(
				$elm$json$Json$Decode$field,
				'handle',
				A2($elm$json$Json$Decode$map, $elm$core$Basics$identity, $author$project$PreviewLifecycle$opaqueDecoder)),
			A2($elm$json$Json$Decode$field, 'owned', $elm$json$Json$Decode$bool),
			A2($elm$json$Json$Decode$field, 'signaled', $elm$json$Json$Decode$bool),
			A2($elm$json$Json$Decode$field, 'fidelity', fidelity),
			A2($elm$json$Json$Decode$field, 'coverage', coverage),
			A2($elm$json$Json$Decode$field, 'expires', $author$project$PreviewIdentity$positive)));
}();
var $author$project$PreviewLifecycle$Trigger = F5(
	function (binding, context, origin, clock, deadline) {
		return {co: binding, p: clock, h: context, C: deadline, bq: origin};
	});
var $elm$json$Json$Decode$map5 = _Json_map5;
var $author$project$PreviewLifecycle$triggerDecoder = A2(
	$author$project$PreviewLifecycle$strict,
	_List_fromArray(
		['binding', 'context', 'origin', 'clock', 'deadline']),
	A6(
		$elm$json$Json$Decode$map5,
		$author$project$PreviewLifecycle$Trigger,
		A2($elm$json$Json$Decode$field, 'binding', $author$project$PreviewLifecycle$bindingDecoder),
		A2($elm$json$Json$Decode$field, 'context', $author$project$PreviewLifecycle$contextDecoder),
		A2($elm$json$Json$Decode$field, 'origin', $author$project$PreviewIdentity$positive),
		A2($elm$json$Json$Decode$field, 'clock', $author$project$PreviewIdentity$positive),
		A2($elm$json$Json$Decode$field, 'deadline', $author$project$PreviewIdentity$positive)));
var $author$project$PreviewLifecycle$basicDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (kind) {
		switch (kind) {
			case 'open':
				return A2(
					$author$project$PreviewLifecycle$strict,
					_List_fromArray(
						['kind']),
					$elm$json$Json$Decode$succeed($author$project$PreviewLifecycle$Open));
			case 'close':
				return A2(
					$author$project$PreviewLifecycle$strict,
					_List_fromArray(
						['kind']),
					$elm$json$Json$Decode$succeed($author$project$PreviewLifecycle$Close));
			case 'request':
				return A2(
					$author$project$PreviewLifecycle$strict,
					_List_fromArray(
						['kind', 'trigger']),
					A2(
						$elm$json$Json$Decode$map,
						$author$project$PreviewLifecycle$Request,
						A2($elm$json$Json$Decode$field, 'trigger', $author$project$PreviewLifecycle$triggerDecoder)));
			case 'offer':
				return A2(
					$author$project$PreviewLifecycle$strict,
					_List_fromArray(
						['kind', 'frame']),
					A2(
						$elm$json$Json$Decode$map,
						$author$project$PreviewLifecycle$Offer,
						A2($elm$json$Json$Decode$field, 'frame', $author$project$PreviewLifecycle$packetDecoder)));
			case 'fence':
				return A2(
					$author$project$PreviewLifecycle$strict,
					_List_fromArray(
						['kind', 'frame']),
					A2(
						$elm$json$Json$Decode$map,
						$author$project$PreviewLifecycle$Fence,
						A2($elm$json$Json$Decode$field, 'frame', $author$project$PreviewLifecycle$packetDecoder)));
			case 'observe':
				return A2(
					$author$project$PreviewLifecycle$strict,
					_List_fromArray(
						['kind', 'scope']),
					A2(
						$elm$json$Json$Decode$map,
						$author$project$PreviewLifecycle$Observe,
						A2($elm$json$Json$Decode$field, 'scope', $author$project$PreviewLifecycle$nativeScopeDecoder)));
			case 'attach':
				return A2(
					$author$project$PreviewLifecycle$strict,
					_List_fromArray(
						['kind', 'previous', 'scope']),
					A3(
						$elm$json$Json$Decode$map2,
						$author$project$PreviewLifecycle$Attach,
						A2($elm$json$Json$Decode$field, 'previous', $author$project$PreviewLifecycle$bindingDecoder),
						A2($elm$json$Json$Decode$field, 'scope', $author$project$PreviewLifecycle$nativeScopeDecoder)));
			case 'clock':
				return A2(
					$author$project$PreviewLifecycle$strict,
					_List_fromArray(
						['kind', 'binding', 'clock', 'now']),
					A4(
						$elm$json$Json$Decode$map3,
						$author$project$PreviewLifecycle$Clock,
						A2($elm$json$Json$Decode$field, 'binding', $author$project$PreviewLifecycle$bindingDecoder),
						A2($elm$json$Json$Decode$field, 'clock', $author$project$PreviewIdentity$positive),
						A2($elm$json$Json$Decode$field, 'now', $author$project$PreviewIdentity$positive)));
			case 'cancelled':
				return A2(
					$author$project$PreviewLifecycle$strict,
					_List_fromArray(
						['kind', 'job']),
					A2(
						$elm$json$Json$Decode$map,
						$author$project$PreviewLifecycle$Cancelled,
						A2($elm$json$Json$Decode$field, 'job', $author$project$PreviewLifecycle$jobDecoder)));
			case 'released':
				return A2(
					$author$project$PreviewLifecycle$strict,
					_List_fromArray(
						['kind', 'frame']),
					A2(
						$elm$json$Json$Decode$map,
						$author$project$PreviewLifecycle$Released,
						A2($elm$json$Json$Decode$field, 'frame', $author$project$PreviewLifecycle$packetDecoder)));
			case 'expired':
				return A2(
					$author$project$PreviewLifecycle$strict,
					_List_fromArray(
						['kind', 'frame']),
					A2(
						$elm$json$Json$Decode$map,
						$author$project$PreviewLifecycle$Expired,
						A2($elm$json$Json$Decode$field, 'frame', $author$project$PreviewLifecycle$packetDecoder)));
			case 'exhausted':
				return A2(
					$author$project$PreviewLifecycle$strict,
					_List_fromArray(
						['kind', 'binding']),
					A2(
						$elm$json$Json$Decode$map,
						$author$project$PreviewLifecycle$Exhausted,
						A2($elm$json$Json$Decode$field, 'binding', $author$project$PreviewLifecycle$bindingDecoder)));
			case 'refused':
				return A2(
					$author$project$PreviewLifecycle$strict,
					_List_fromArray(
						['kind', 'job']),
					A2(
						$elm$json$Json$Decode$map,
						$author$project$PreviewLifecycle$Refused,
						A2($elm$json$Json$Decode$field, 'job', $author$project$PreviewLifecycle$jobDecoder)));
			default:
				return $elm$json$Json$Decode$fail('Preview lifecycle event');
		}
	},
	A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string));
var $author$project$PreviewLifecycle$terminalJob = function (event) {
	switch (event.$) {
		case 8:
			var job = event.a;
			return $elm$core$Maybe$Just(job);
		case 9:
			var frame = event.a;
			return $elm$core$Maybe$Just(frame.c);
		case 12:
			var job = event.a;
			return $elm$core$Maybe$Just(job);
		default:
			return $elm$core$Maybe$Nothing;
	}
};
var $author$project$PreviewLifecycle$eventDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (kind) {
		if (kind === 'receipt') {
			var terminal = A2(
				$elm$json$Json$Decode$andThen,
				function (event) {
					return (!_Utils_eq(
						$author$project$PreviewLifecycle$terminalJob(event),
						$elm$core$Maybe$Nothing)) ? $elm$json$Json$Decode$succeed(event) : $elm$json$Json$Decode$fail('Terminal native receipt body');
				},
				$author$project$PreviewLifecycle$basicDecoder);
			return A2(
				$author$project$PreviewLifecycle$strict,
				_List_fromArray(
					['kind', 'sequence', 'event']),
				A3(
					$elm$json$Json$Decode$map2,
					$author$project$PreviewLifecycle$Receipt,
					A2($elm$json$Json$Decode$field, 'sequence', $author$project$PreviewIdentity$positive),
					A2($elm$json$Json$Decode$field, 'event', terminal)));
		} else {
			return A2(
				$elm$json$Json$Decode$andThen,
				function (event) {
					return _Utils_eq(
						$author$project$PreviewLifecycle$terminalJob(event),
						$elm$core$Maybe$Nothing) ? $elm$json$Json$Decode$succeed(event) : $elm$json$Json$Decode$fail('Native cleanup receipt identity required');
				},
				$author$project$PreviewLifecycle$basicDecoder);
		}
	},
	A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string));
var $author$project$PreviewLifecycle$Acknowledge = F2(
	function (a, b) {
		return {$: 4, a: a, b: b};
	});
var $author$project$PreviewLifecycle$Accepted = $elm$core$Basics$identity;
var $author$project$PreviewLifecycle$Acquire = function (a) {
	return {$: 0, a: a};
};
var $author$project$PreviewLifecycle$Capturing = function (a) {
	return {$: 1, a: a};
};
var $author$project$PreviewLifecycle$Cancel = function (a) {
	return {$: 1, a: a};
};
var $author$project$PreviewLifecycle$emit = F2(
	function (command, work) {
		return _Utils_update(
			work,
			{
				aK: _Utils_ap(
					work.aK,
					_List_fromArray(
						[command]))
			});
	});
var $author$project$PreviewLifecycle$mapState = F2(
	function (f, work) {
		return _Utils_update(
			work,
			{
				k: f(work.k)
			});
	});
var $author$project$PreviewLifecycle$cancelCurrent = function (work) {
	var _v0 = work.k.e;
	if (_v0.$ === 1) {
		var job = _v0.a;
		var cleared = A2(
			$author$project$PreviewLifecycle$mapState,
			function (st) {
				return _Utils_update(
					st,
					{e: $author$project$PreviewLifecycle$Idle});
			},
			work);
		return A2($elm$core$List$member, job, work.k.x) ? cleared : A2(
			$author$project$PreviewLifecycle$emit,
			$author$project$PreviewLifecycle$Cancel(job),
			A2(
				$author$project$PreviewLifecycle$mapState,
				function (st) {
					return _Utils_update(
						st,
						{
							x: A2($elm$core$List$cons, job, st.x)
						});
				},
				cleared));
	} else {
		return work;
	}
};
var $author$project$PreviewLifecycle$Release = function (a) {
	return {$: 2, a: a};
};
var $author$project$PreviewLifecycle$sameLease = F2(
	function (a, b) {
		return _Utils_eq(a.c, b.c) && _Utils_eq(a.E, b.E);
	});
var $author$project$PreviewLifecycle$retirePacket = F2(
	function (frame, work) {
		return A2(
			$elm$core$List$any,
			$author$project$PreviewLifecycle$sameLease(frame),
			work.k.r) ? work : A2(
			$author$project$PreviewLifecycle$emit,
			$author$project$PreviewLifecycle$Release(frame),
			A2(
				$author$project$PreviewLifecycle$mapState,
				function (st) {
					return _Utils_update(
						st,
						{
							r: A2($elm$core$List$cons, frame, st.r)
						});
				},
				work));
	});
var $author$project$PreviewLifecycle$retireAccepted = function (work) {
	var _v0 = $author$project$PreviewLifecycle$acceptedPacket(work.k);
	if (!_v0.$) {
		var frame = _v0.a;
		return A2(
			$author$project$PreviewLifecycle$retirePacket,
			frame,
			A2(
				$author$project$PreviewLifecycle$mapState,
				function (st) {
					return _Utils_update(
						st,
						{aa: $elm$core$Maybe$Nothing});
				},
				work));
	} else {
		return work;
	}
};
var $author$project$PreviewLifecycle$retireCandidate = function (work) {
	var _v0 = $author$project$PreviewLifecycle$candidate(work.k);
	if (!_v0.$) {
		var frame = _v0.a;
		return A2(
			$author$project$PreviewLifecycle$retirePacket,
			frame,
			A2(
				$author$project$PreviewLifecycle$mapState,
				function (st) {
					return _Utils_update(
						st,
						{e: $author$project$PreviewLifecycle$Idle});
				},
				work));
	} else {
		return work;
	}
};
var $author$project$PreviewLifecycle$advanceClock = F2(
	function (now, work) {
		var timed = A2(
			$author$project$PreviewLifecycle$mapState,
			function (st) {
				var sc = st.a;
				return _Utils_update(
					st,
					{
						a: _Utils_update(
							sc,
							{B: now})
					});
			},
			work);
		var jobTimed = function () {
			var _v2 = timed.k.e;
			if (_v2.$ === 1) {
				var job = _v2.a;
				return A2($author$project$PreviewLifecycle$notAfter, job.C, now) ? $author$project$PreviewLifecycle$cancelCurrent(timed) : timed;
			} else {
				return timed;
			}
		}();
		var candidateTimed = function () {
			var _v1 = $author$project$PreviewLifecycle$candidate(jobTimed.k);
			if (!_v1.$) {
				var frame = _v1.a;
				return (A2($author$project$PreviewLifecycle$notAfter, frame.c.C, now) || A2($author$project$PreviewLifecycle$notAfter, frame.aL, now)) ? $author$project$PreviewLifecycle$retireCandidate(jobTimed) : jobTimed;
			} else {
				return jobTimed;
			}
		}();
		var _v0 = $author$project$PreviewLifecycle$acceptedPacket(candidateTimed.k);
		if (!_v0.$) {
			var frame = _v0.a;
			return A2($author$project$PreviewLifecycle$notAfter, frame.aL, now) ? $author$project$PreviewLifecycle$retireAccepted(candidateTimed) : candidateTimed;
		} else {
			return candidateTimed;
		}
	});
var $author$project$PreviewLifecycle$finishKnown = F2(
	function (job, work) {
		var st = work.k;
		var captureMatches = function () {
			var _v0 = st.e;
			switch (_v0.$) {
				case 1:
					var current = _v0.a;
					return _Utils_eq(current, job);
				case 2:
					var current = _v0.a;
					return _Utils_eq(current.c, job);
				default:
					return false;
			}
		}();
		var stillHeld = captureMatches || (A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (f) {
					return _Utils_eq(f.c, job);
				},
				$author$project$PreviewLifecycle$acceptedPacket(st))) || (A2($elm$core$List$member, job, st.x) || A2(
			$elm$core$List$any,
			function (f) {
				return _Utils_eq(f.c, job);
			},
			st.r)));
		return stillHeld ? work : A2(
			$author$project$PreviewLifecycle$mapState,
			function (state) {
				return _Utils_update(
					state,
					{
						bO: A2(
							$elm$core$List$filter,
							$elm$core$Basics$neq(job),
							state.bO)
					});
			},
			work);
	});
var $elm$core$List$isEmpty = function (xs) {
	if (!xs.b) {
		return true;
	} else {
		return false;
	}
};
var $author$project$PreviewLifecycle$Candidate = $elm$core$Basics$identity;
var $author$project$PreviewLifecycle$WaitingFence = function (a) {
	return {$: 2, a: a};
};
var $author$project$PreviewLifecycle$heldHandle = F2(
	function (st, handle) {
		return A2(
			$elm$core$List$any,
			function (packet) {
				return _Utils_eq(packet.E, handle);
			},
			_Utils_ap(
				A2(
					$elm$core$List$filterMap,
					$elm$core$Basics$identity,
					_List_fromArray(
						[
							$author$project$PreviewLifecycle$candidate(st),
							$author$project$PreviewLifecycle$acceptedPacket(st)
						])),
				st.r));
	});
var $author$project$PreviewLifecycle$offer = F2(
	function (frame, work) {
		var st = work.k;
		var matches = function () {
			var _v1 = st.e;
			if (_v1.$ === 1) {
				var job = _v1.a;
				return st.D && (_Utils_eq(job, frame.c) && (A2($author$project$PreviewLifecycle$authorized, st, frame) && (A2($author$project$PreviewLifecycle$before, st.a.B, frame.c.C) && (!A2($author$project$PreviewLifecycle$heldHandle, st, frame.E)))));
			} else {
				return false;
			}
		}();
		if (matches) {
			return frame.bc ? A2(
				$author$project$PreviewLifecycle$mapState,
				function (state) {
					return _Utils_update(
						state,
						{
							aa: $elm$core$Maybe$Just(frame),
							e: $author$project$PreviewLifecycle$Idle
						});
				},
				$author$project$PreviewLifecycle$retireAccepted(work)) : A2(
				$author$project$PreviewLifecycle$mapState,
				function (state) {
					return _Utils_update(
						state,
						{
							e: $author$project$PreviewLifecycle$WaitingFence(frame)
						});
				},
				work);
		} else {
			if (A2($elm$core$List$member, frame.c, st.bO) && (frame.a9 && (!A2($author$project$PreviewLifecycle$heldHandle, st, frame.E)))) {
				var cleanup = A2($author$project$PreviewLifecycle$retirePacket, frame, work);
				var _v0 = cleanup.k.e;
				if (_v0.$ === 1) {
					var job = _v0.a;
					return _Utils_eq(job, frame.c) ? $author$project$PreviewLifecycle$cancelCurrent(cleanup) : cleanup;
				} else {
					return cleanup;
				}
			} else {
				return work;
			}
		}
	});
var $author$project$PreviewLifecycle$NeedsReconciliation = 1;
var $author$project$PreviewLifecycle$Reconcile = function (a) {
	return {$: 3, a: a};
};
var $author$project$PreviewLifecycle$revoke = A2(
	$elm$core$Basics$composeR,
	$author$project$PreviewLifecycle$cancelCurrent,
	A2($elm$core$Basics$composeR, $author$project$PreviewLifecycle$retireCandidate, $author$project$PreviewLifecycle$retireAccepted));
var $author$project$PreviewLifecycle$reconcile = function (work) {
	return A2(
		$author$project$PreviewLifecycle$emit,
		$author$project$PreviewLifecycle$Reconcile(work.k.a.co),
		A2(
			$author$project$PreviewLifecycle$mapState,
			function (st) {
				return _Utils_update(
					st,
					{ac: 1});
			},
			$author$project$PreviewLifecycle$revoke(work)));
};
var $author$project$PreviewLifecycle$scopeCoherent = F2(
	function (previous, incoming) {
		return A2($author$project$PreviewLifecycle$notAfter, previous.h.cG, incoming.h.cG) && (A2($author$project$PreviewLifecycle$notAfter, previous.h.aw, incoming.h.aw) && (A2($author$project$PreviewLifecycle$notAfter, previous.h.aA, incoming.h.aA) && ((!_Utils_eq(incoming.h.w, previous.h.w)) || (A2($author$project$PreviewLifecycle$notAfter, previous.h.M, incoming.h.M) && (A2($author$project$PreviewLifecycle$notAfter, previous.h.T, incoming.h.T) && (_Utils_eq(incoming.aC, previous.aC) || A2($author$project$PreviewLifecycle$before, previous.h.M, incoming.h.M)))))));
	});
var $author$project$PreviewLifecycle$scopeValid = F2(
	function (previous, incoming) {
		return _Utils_eq(incoming.co, previous.co) && (_Utils_eq(incoming.p, previous.p) && (_Utils_eq(incoming.h.af, incoming.co.af) && (A2($author$project$PreviewLifecycle$notAfter, previous.B, incoming.B) && A2($author$project$PreviewLifecycle$before, previous.a8, incoming.a8))));
	});
var $author$project$PreviewLifecycle$updatePlain = F2(
	function (event, _v0) {
		var initial = _v0;
		var base = {aK: _List_Nil, k: initial};
		var _final = function () {
			switch (event.$) {
				case 0:
					return A2(
						$author$project$PreviewLifecycle$mapState,
						function (st) {
							return _Utils_update(
								st,
								{D: true});
						},
						base);
				case 1:
					return A2(
						$author$project$PreviewLifecycle$mapState,
						function (st) {
							return _Utils_update(
								st,
								{D: false});
						},
						$author$project$PreviewLifecycle$retireCandidate(
							$author$project$PreviewLifecycle$cancelCurrent(base)));
				case 2:
					var trigger = event.a;
					if ((!initial.ac) && (initial.D && (initial.a.aY && (initial.a.aC && ((!initial.a.ag) && (initial.a.aP && (_Utils_eq(initial.e, $author$project$PreviewLifecycle$Idle) && ($elm$core$List$isEmpty(initial.x) && ($elm$core$List$isEmpty(initial.r) && (_Utils_eq(trigger.co, initial.a.co) && (_Utils_eq(trigger.h, initial.a.h) && (_Utils_eq(trigger.p, initial.a.p) && A2($author$project$PreviewLifecycle$before, initial.a.B, trigger.C))))))))))))) {
						var _v2 = initial.av;
						if (!_v2.$) {
							var request = _v2.a;
							var job = {co: initial.a.co, p: initial.a.p, h: initial.a.h, C: trigger.C, bq: trigger.bq, m: request};
							return A2(
								$author$project$PreviewLifecycle$emit,
								$author$project$PreviewLifecycle$Acquire(job),
								A2(
									$author$project$PreviewLifecycle$mapState,
									function (st) {
										return _Utils_update(
											st,
											{
												e: $author$project$PreviewLifecycle$Capturing(job),
												bO: A2($elm$core$List$cons, job, st.bO),
												av: $author$project$PreviewIdentity$nextRequest(request)
											});
									},
									base));
						} else {
							return base;
						}
					} else {
						return base;
					}
				case 3:
					var frame = event.a;
					return A2($author$project$PreviewLifecycle$offer, frame, base);
				case 4:
					var incoming = event.a;
					var _v3 = $author$project$PreviewLifecycle$candidate(initial);
					if (!_v3.$) {
						var frame = _v3.a;
						return (A2($author$project$PreviewLifecycle$sameLease, frame, incoming) && (initial.D && (A2($author$project$PreviewLifecycle$authorized, initial, frame) && A2($author$project$PreviewLifecycle$before, initial.a.B, frame.c.C)))) ? A2(
							$author$project$PreviewLifecycle$mapState,
							function (st) {
								return _Utils_update(
									st,
									{
										aa: $elm$core$Maybe$Just(
											_Utils_update(
												frame,
												{bc: true})),
										e: $author$project$PreviewLifecycle$Idle
									});
							},
							$author$project$PreviewLifecycle$retireAccepted(base)) : base;
					} else {
						return base;
					}
				case 5:
					var incoming = event.a;
					if (!A2($author$project$PreviewLifecycle$scopeValid, initial.a, incoming)) {
						return base;
					} else {
						if (!A2($author$project$PreviewLifecycle$scopeCoherent, initial.a, incoming)) {
							return $author$project$PreviewLifecycle$reconcile(base);
						} else {
							var changed = ((!A2($author$project$PreviewLifecycle$generationMatches, initial.a.h, incoming.h)) || ((!incoming.aY) || (incoming.ag || (!incoming.aP)))) ? $author$project$PreviewLifecycle$revoke(base) : base;
							return A2(
								$author$project$PreviewLifecycle$advanceClock,
								incoming.B,
								A2(
									$author$project$PreviewLifecycle$mapState,
									function (st) {
										return _Utils_update(
											st,
											{a: incoming});
									},
									changed));
						}
					}
				case 6:
					var previous = event.a;
					var incoming = event.b;
					return (_Utils_eq(previous, initial.a.co) && ((!_Utils_eq(incoming.co, previous)) && _Utils_eq(incoming.h.af, incoming.co.af))) ? A2(
						$author$project$PreviewLifecycle$mapState,
						function (st) {
							return _Utils_update(
								st,
								{
									ac: 0,
									av: $author$project$PreviewIdentity$nextRequest($author$project$PreviewIdentity$zeroRequest),
									a: incoming
								});
						},
						$author$project$PreviewLifecycle$revoke(base)) : base;
				case 7:
					var binding = event.a;
					var clock = event.b;
					var now = event.c;
					return (_Utils_eq(binding, initial.a.co) && (_Utils_eq(clock, initial.a.p) && A2($author$project$PreviewLifecycle$before, initial.a.B, now))) ? A2($author$project$PreviewLifecycle$advanceClock, now, base) : base;
				case 8:
					var job = event.a;
					return A2($elm$core$List$member, job, initial.x) ? A2(
						$author$project$PreviewLifecycle$finishKnown,
						job,
						A2(
							$author$project$PreviewLifecycle$mapState,
							function (st) {
								return _Utils_update(
									st,
									{
										x: A2(
											$elm$core$List$filter,
											$elm$core$Basics$neq(job),
											st.x),
										r: A2(
											$elm$core$List$filter,
											function (f) {
												return !_Utils_eq(f.c, job);
											},
											st.r)
									});
							},
							base)) : base;
				case 9:
					var frame = event.a;
					return A2(
						$elm$core$List$any,
						$author$project$PreviewLifecycle$sameLease(frame),
						initial.r) ? A2(
						$author$project$PreviewLifecycle$finishKnown,
						frame.c,
						A2(
							$author$project$PreviewLifecycle$mapState,
							function (st) {
								return _Utils_update(
									st,
									{
										r: A2(
											$elm$core$List$filter,
											A2(
												$elm$core$Basics$composeR,
												$author$project$PreviewLifecycle$sameLease(frame),
												$elm$core$Basics$not),
											st.r)
									});
							},
							base)) : base;
				case 10:
					var frame = event.a;
					return A2(
						$elm$core$Maybe$withDefault,
						false,
						A2(
							$elm$core$Maybe$map,
							$author$project$PreviewLifecycle$sameLease(frame),
							$author$project$PreviewLifecycle$candidate(initial))) ? $author$project$PreviewLifecycle$retireCandidate(base) : (A2(
						$elm$core$Maybe$withDefault,
						false,
						A2(
							$elm$core$Maybe$map,
							$author$project$PreviewLifecycle$sameLease(frame),
							$author$project$PreviewLifecycle$acceptedPacket(initial))) ? $author$project$PreviewLifecycle$retireAccepted(base) : base);
				case 11:
					var binding = event.a;
					return _Utils_eq(binding, initial.a.co) ? $author$project$PreviewLifecycle$reconcile(base) : base;
				case 13:
					return base;
				default:
					var job = event.a;
					var _v4 = initial.e;
					if (_v4.$ === 1) {
						var current = _v4.a;
						return _Utils_eq(current, job) ? A2(
							$author$project$PreviewLifecycle$finishKnown,
							job,
							A2(
								$author$project$PreviewLifecycle$mapState,
								function (st) {
									return _Utils_update(
										st,
										{e: $author$project$PreviewLifecycle$Idle});
								},
								base)) : base;
					} else {
						return base;
					}
			}
		}();
		return _Utils_Tuple2(_final.k, _final.aK);
	});
var $author$project$PreviewLifecycle$update = F2(
	function (event, model) {
		if (event.$ === 13) {
			var sequence = event.a;
			var terminal = event.b;
			var _v1 = A2($author$project$PreviewLifecycle$updatePlain, terminal, model);
			var next = _v1.a;
			var commands = _v1.b;
			var _v2 = next;
			var state = _v2;
			var _v3 = $author$project$PreviewLifecycle$terminalJob(terminal);
			if (!_v3.$) {
				var job = _v3.a;
				return A2($elm$core$List$member, job, state.bO) ? _Utils_Tuple2(next, commands) : _Utils_Tuple2(
					next,
					_Utils_ap(
						commands,
						_List_fromArray(
							[
								A2($author$project$PreviewLifecycle$Acknowledge, job, sequence)
							])));
			} else {
				return _Utils_Tuple2(next, commands);
			}
		} else {
			return A2($author$project$PreviewLifecycle$updatePlain, event, model);
		}
	});
var $author$project$DesignDemo$previewUpdate = F2(
	function (raw, model) {
		var _v0 = _Utils_Tuple2(
			model.aj,
			A2($elm$json$Json$Decode$decodeValue, $author$project$PreviewLifecycle$eventDecoder, raw));
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var before = _v0.a.a;
			var event = _v0.b.a;
			var _v1 = A2($author$project$PreviewLifecycle$update, event, before);
			var after = _v1.a;
			var effects = _v1.b;
			return _Utils_update(
				model,
				{
					aK: $author$project$PreviewLifecycle$encodeCommands(effects),
					aj: $elm$core$Maybe$Just(after)
				});
		} else {
			return _Utils_update(
				model,
				{a6: 'Fixture event was rejected by the shipped preview decoder.'});
		}
	});
var $author$project$DesignDemo$previewAction = F2(
	function (action, model) {
		switch (action) {
			case 'load':
				return A2(
					$author$project$DesignDemo$previewUpdate,
					$elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'kind',
								$elm$json$Json$Encode$string('request')),
								_Utils_Tuple2(
								'trigger',
								$elm$json$Json$Encode$object(
									_List_fromArray(
										[
											_Utils_Tuple2('binding', $author$project$DesignDemo$nativeBinding),
											_Utils_Tuple2('context', $author$project$DesignDemo$context),
											_Utils_Tuple2(
											'origin',
											$elm$json$Json$Encode$string('12')),
											_Utils_Tuple2(
											'clock',
											$elm$json$Json$Encode$string('10')),
											_Utils_Tuple2(
											'deadline',
											$elm$json$Json$Encode$string('80'))
										])))
							])),
					A2(
						$author$project$DesignDemo$previewUpdate,
						$elm$json$Json$Encode$object(
							_List_fromArray(
								[
									_Utils_Tuple2(
									'kind',
									$elm$json$Json$Encode$string('open'))
								])),
						model));
			case 'frame':
				var _v1 = A2(
					$elm$core$Maybe$andThen,
					A2(
						$elm$core$Basics$composeR,
						$author$project$PreviewLifecycle$observe,
						A2(
							$elm$core$Basics$composeR,
							$elm$json$Json$Decode$decodeValue(
								A2($elm$json$Json$Decode$field, 'job', $elm$json$Json$Decode$value)),
							$elm$core$Result$toMaybe)),
					model.aj);
				if (!_v1.$) {
					var job = _v1.a;
					return A2(
						$author$project$DesignDemo$previewUpdate,
						$elm$json$Json$Encode$object(
							_List_fromArray(
								[
									_Utils_Tuple2(
									'kind',
									$elm$json$Json$Encode$string('offer')),
									_Utils_Tuple2(
									'frame',
									$elm$json$Json$Encode$object(
										_List_fromArray(
											[
												_Utils_Tuple2('job', job),
												_Utils_Tuple2(
												'handle',
												$elm$json$Json$Encode$string(
													A2($elm$core$String$repeat, 64, '1'))),
												_Utils_Tuple2(
												'owned',
												$elm$json$Json$Encode$bool(true)),
												_Utils_Tuple2(
												'signaled',
												$elm$json$Json$Encode$bool(true)),
												_Utils_Tuple2(
												'fidelity',
												$elm$json$Json$Encode$string('family')),
												_Utils_Tuple2(
												'coverage',
												A2(
													$elm$json$Json$Encode$list,
													$elm$json$Json$Encode$string,
													_List_fromArray(
														['client', 'decoration', 'modal', 'popup']))),
												_Utils_Tuple2(
												'expires',
												$elm$json$Json$Encode$string('90'))
											])))
								])),
						model);
				} else {
					return model;
				}
			case 'historical':
				return A2(
					$author$project$DesignDemo$previewUpdate,
					$elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'kind',
								$elm$json$Json$Encode$string('observe')),
								_Utils_Tuple2(
								'scope',
								A2($author$project$DesignDemo$scope, false, false))
							])),
					model);
			case 'lock':
				return A2(
					$author$project$DesignDemo$previewUpdate,
					$elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'kind',
								$elm$json$Json$Encode$string('observe')),
								_Utils_Tuple2(
								'scope',
								A2($author$project$DesignDemo$scope, true, true))
							])),
					model);
			case 'expire':
				return A2(
					$author$project$DesignDemo$previewUpdate,
					$elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'kind',
								$elm$json$Json$Encode$string('clock')),
								_Utils_Tuple2('binding', $author$project$DesignDemo$nativeBinding),
								_Utils_Tuple2(
								'clock',
								$elm$json$Json$Encode$string('10')),
								_Utils_Tuple2(
								'now',
								$elm$json$Json$Encode$string('100'))
							])),
					model);
			case 'close':
				return A2(
					$author$project$DesignDemo$previewUpdate,
					$elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'kind',
								$elm$json$Json$Encode$string('close'))
							])),
					model);
			default:
				return model;
		}
	});
var $author$project$DesignDemo$blocked = function (model) {
	var _v0 = A2(
		$elm$core$Maybe$map,
		function ($) {
			return $.bx;
		},
		$author$project$Menu$snapshot(model.d).d);
	if (!_v0.$) {
		switch (_v0.a.$) {
			case 1:
				return true;
			case 4:
				return true;
			case 0:
				var _v1 = _v0.a;
				return false;
			default:
				return true;
		}
	} else {
		return false;
	}
};
var $author$project$DesignDemo$control = F4(
	function (identity, label, detail, enabled) {
		return $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'id',
					$elm$json$Json$Encode$string(identity)),
					_Utils_Tuple2(
					'domId',
					$elm$json$Json$Encode$string('fixture-' + identity)),
					_Utils_Tuple2(
					'label',
					$elm$json$Json$Encode$string(label)),
					_Utils_Tuple2(
					'ariaLabel',
					$elm$json$Json$Encode$string(label)),
					_Utils_Tuple2(
					'detail',
					$elm$json$Json$Encode$string(detail)),
					_Utils_Tuple2(
					'enabled',
					$elm$json$Json$Encode$bool(enabled))
				]));
	});
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
		return {bB: ariaLabel, bl: detail, a4: domId, q: enabled, aq: identity, bP: label};
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
var $author$project$SurfaceRenderer$decode = function (raw) {
	var decoder = A2(
		$author$project$SurfaceRenderer$strict,
		_List_fromArray(
			['surfaceProtocol', 'publication', 'lease', 'mode', 'status', 'bar', 'popup']),
		A8(
			$elm$json$Json$Decode$map7,
			F7(
				function (version, shown, scoped, current, notice, bar, popup) {
					return {ab: bar, aJ: current, bW: notice, Y: popup, bt: scoped, bv: shown, cc: version};
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
				$author$project$SurfaceRenderer$controls(259)),
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
			var all = _Utils_ap(record.ab, record.Y);
			var identities = A2(
				$elm$core$List$map,
				function ($) {
					return $.aq;
				},
				all);
			return ((record.cc !== 2) || (_Utils_eq(record.bv, $author$project$UInt64$zero) || ((!A2(
				$elm$core$List$member,
				record.aJ,
				_List_fromArray(
					['closed', 'picker', 'applications', 'menu']))) || (((record.aJ !== 'closed') && _Utils_eq(record.bt, $author$project$UInt64$zero)) || (((record.aJ === 'closed') && (!$elm$core$List$isEmpty(record.Y))) || ((!unique(identities)) || ((!unique(
				A2(
					$elm$core$List$map,
					function ($) {
						return $.a4;
					},
					all))) || A2(
				$elm$core$List$any,
				function (control) {
					return $elm$core$String$isEmpty(control.aq) || $elm$core$String$isEmpty(control.a4);
				},
				all)))))))) ? $elm$core$Result$Err('Invalid presentation scope/identities') : $elm$core$Result$Ok(
				{ab: record.ab, bn: record.bt, V: record.aJ, Y: record.Y, ba: record.bv, bx: record.bW});
		},
		A2(
			$elm$core$Result$mapError,
			$elm$json$Json$Decode$errorToString,
			A2($elm$json$Json$Decode$decodeValue, decoder, raw)));
};
var $author$project$DesignDemo$outcomeDetail = function (model) {
	var _v0 = A2(
		$elm$core$Maybe$map,
		function ($) {
			return $.bx;
		},
		$author$project$Menu$snapshot(model.d).d);
	_v0$4:
	while (true) {
		if (!_v0.$) {
			switch (_v0.a.$) {
				case 4:
					return 'Blocked until reconciled';
				case 1:
					return 'Awaiting confirmation';
				case 2:
					return 'Change refused';
				case 3:
					var _v1 = _v0.a;
					return 'Cancelled';
				default:
					break _v0$4;
			}
		} else {
			break _v0$4;
		}
	}
	return '';
};
var $author$project$DesignDemo$projection = function (model) {
	var menu = $author$project$Menu$snapshot(model.d).d;
	var mode = (model.o === 'menu') ? (_Utils_eq(menu, $elm$core$Maybe$Nothing) ? 'closed' : 'menu') : ((model.o === 'applications') ? 'applications' : ((model.o === 'picker') ? 'picker' : 'closed'));
	var popup = (mode === 'menu') ? A2(
		$elm$core$List$cons,
		A4($author$project$DesignDemo$control, 'control:menu-close', 'Close', 'Close window actions', true),
		A2(
			$elm$core$List$indexedMap,
			F2(
				function (index, item) {
					return A4(
						$author$project$DesignDemo$control,
						'demo-menu:' + $elm$core$String$fromInt(index),
						item.bP,
						(!item.q) ? 'Unavailable in this fixture' : ($author$project$DesignDemo$blocked(model) ? $author$project$DesignDemo$outcomeDetail(model) : (_Utils_eq(
							$elm$core$Maybe$Just(index),
							A2(
								$elm$core$Maybe$andThen,
								function ($) {
									return $.cN;
								},
								menu)) ? 'Selected' : '')),
						item.q && (!$author$project$DesignDemo$blocked(model)));
				}),
			$author$project$DesignDemo$items)) : ((mode === 'applications') ? _List_fromArray(
		[
			A4($author$project$DesignDemo$control, 'demo-app:editor', 'Text editor', 'Declared application', true),
			A4($author$project$DesignDemo$control, 'demo-app:terminal', 'Terminal', 'Declared application', true)
		]) : ((mode === 'picker') ? _List_fromArray(
		[
			A4($author$project$DesignDemo$control, 'demo-picker:document', 'Restore design notes', 'Text editor', true),
			A4($author$project$DesignDemo$control, 'demo-picker:terminal', 'Activate build session', 'Terminal', true)
		]) : _List_Nil));
	var bar = (model.o === 'utility') ? _List_fromArray(
		[
			A4($author$project$DesignDemo$control, 'bar:applications', 'Applications', '', true),
			A4($author$project$DesignDemo$control, 'bar:close', 'Close', '', true),
			A4($author$project$DesignDemo$control, 'bar:refresh', 'Refresh', '', true),
			A4($author$project$DesignDemo$control, 'bar:reconnect', 'Reconnect', '', true)
		]) : (((model.o === 'bar') || (model.o === 'status')) ? _List_fromArray(
		[
			A4($author$project$DesignDemo$control, 'bar:applications', 'Applications', '', true),
			A4(
			$author$project$DesignDemo$control,
			'bar:group:terminal',
			'Terminal',
			$author$project$DesignDemo$decision(model.ak),
			model.ak !== 'unavailable'),
			A4($author$project$DesignDemo$control, 'bar:recovery-refresh', 'Refresh windows', '', true)
		]) : _List_Nil);
	return $author$project$SurfaceRenderer$decode(
		$elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'surfaceProtocol',
					$elm$json$Json$Encode$int(2)),
					_Utils_Tuple2(
					'publication',
					$elm$json$Json$Encode$string(
						$elm$core$String$fromInt(model.ba))),
					_Utils_Tuple2(
					'lease',
					$elm$json$Json$Encode$string('1')),
					_Utils_Tuple2(
					'mode',
					$elm$json$Json$Encode$string(mode)),
					_Utils_Tuple2(
					'status',
					$elm$json$Json$Encode$string(
						(model.o === 'menu') ? $author$project$DesignDemo$notice(model) : 'Simulated fixture; no native effect')),
					_Utils_Tuple2(
					'bar',
					A2($elm$json$Json$Encode$list, $elm$core$Basics$identity, bar)),
					_Utils_Tuple2(
					'popup',
					A2($elm$json$Json$Encode$list, $elm$core$Basics$identity, popup))
				])));
};
var $author$project$CapturedAction$publication = function (_v0) {
	var value = _v0;
	return value.ba;
};
var $author$project$SurfaceRenderer$publication = function (_v0) {
	var snapshot = _v0;
	return snapshot.ba;
};
var $author$project$CapturedAction$surface = function (_v0) {
	var value = _v0;
	return value.be;
};
var $author$project$DesignDemo$apply = F2(
	function (raw, model) {
		var _v0 = A2(
			$elm$json$Json$Decode$decodeValue,
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			raw);
		_v0$7:
		while (true) {
			if (!_v0.$) {
				switch (_v0.a) {
					case 'reset':
						return $author$project$DesignDemo$initial(model.o);
					case 'profile':
						var _v1 = A2(
							$elm$json$Json$Decode$decodeValue,
							A2($elm$json$Json$Decode$field, 'value', $elm$json$Json$Decode$string),
							raw);
						if (!_v1.$) {
							var value = _v1.a;
							return A2(
								$elm$core$List$member,
								value,
								_List_fromArray(
									['empty', 'inactive', 'active', 'minimized', 'unavailable', 'multiple'])) ? _Utils_update(
								model,
								{ak: value}) : model;
						} else {
							return model;
						}
					case 'preview':
						return A2(
							$elm$core$Result$withDefault,
							model,
							A2(
								$elm$core$Result$map,
								function (action) {
									return A2($author$project$DesignDemo$previewAction, action, model);
								},
								A2(
									$elm$json$Json$Decode$decodeValue,
									A2($elm$json$Json$Decode$field, 'action', $elm$json$Json$Decode$string),
									raw)));
					case 'dismiss':
						var _v2 = $author$project$Menu$snapshot(model.d).d;
						if (!_v2.$) {
							var menu = _v2.a;
							return A2(
								$author$project$DesignDemo$menuUpdate,
								$author$project$Menu$Dismiss(menu.ae),
								model);
						} else {
							return model;
						}
					case 'navigate':
						var _v3 = _Utils_Tuple2(
							$author$project$Menu$snapshot(model.d).d,
							A2(
								$elm$json$Json$Decode$decodeValue,
								A2($elm$json$Json$Decode$field, 'key', $elm$json$Json$Decode$string),
								raw));
						if ((!_v3.a.$) && (!_v3.b.$)) {
							var menu = _v3.a.a;
							var key = _v3.b.a;
							switch (key) {
								case 'ArrowUp':
									return A2(
										$author$project$DesignDemo$menuUpdate,
										A2($author$project$Menu$Navigate, menu.ae, 0),
										model);
								case 'ArrowDown':
									return A2(
										$author$project$DesignDemo$menuUpdate,
										A2($author$project$Menu$Navigate, menu.ae, 1),
										model);
								case 'Home':
									return A2(
										$author$project$DesignDemo$menuUpdate,
										A2($author$project$Menu$Navigate, menu.ae, 2),
										model);
								case 'End':
									return A2(
										$author$project$DesignDemo$menuUpdate,
										A2($author$project$Menu$Navigate, menu.ae, 3),
										model);
								default:
									return model;
							}
						} else {
							return model;
						}
					case 'authority':
						var _v5 = _Utils_Tuple2(
							model.aR,
							A2(
								$elm$json$Json$Decode$decodeValue,
								A2($elm$json$Json$Decode$field, 'outcome', $elm$json$Json$Decode$string),
								raw));
						if ((!_v5.a.$) && (!_v5.b.$)) {
							var _v6 = _v5.a.a;
							var intent = _v6.a;
							var binding = _v6.b;
							var outcome = _v5.b.a;
							switch (outcome) {
								case 'committed':
									return A2(
										$author$project$DesignDemo$menuUpdate,
										A3($author$project$Menu$ReceiveFor, intent, binding, $author$project$Menu$Committed),
										model);
								case 'refused':
									return A2(
										$author$project$DesignDemo$menuUpdate,
										A3(
											$author$project$Menu$ReceiveFor,
											intent,
											binding,
											$author$project$Menu$Refusal('Change refused by simulated authority.')),
										model);
								case 'cancelled':
									return A2(
										$author$project$DesignDemo$menuUpdate,
										A3($author$project$Menu$ReceiveFor, intent, binding, $author$project$Menu$Cancellation),
										model);
								case 'unknown':
									return A2(
										$author$project$DesignDemo$menuUpdate,
										A3($author$project$Menu$ReceiveFor, intent, binding, $author$project$Menu$Uncertain),
										model);
								default:
									return model;
							}
						} else {
							return model;
						}
					case 'surface-action':
						var _v8 = _Utils_Tuple3(
							$author$project$DesignDemo$projection(model),
							$author$project$CapturedAction$decode(raw),
							$author$project$Menu$snapshot(model.d).d);
						if (((!_v8.a.$) && (!_v8.b.$)) && (!_v8.c.$)) {
							var shown = _v8.a.a;
							var captured = _v8.b.a;
							var menu = _v8.c.a;
							if ((!_Utils_eq(
								$author$project$CapturedAction$publication(captured),
								$author$project$SurfaceRenderer$publication(shown))) || ((!_Utils_eq(
								$author$project$CapturedAction$lease(captured),
								$author$project$SurfaceRenderer$lease(shown))) || (($author$project$CapturedAction$surface(captured) !== 'popup') || (!A3(
								$author$project$SurfaceRenderer$enabled,
								true,
								$author$project$CapturedAction$identity(captured),
								shown))))) {
								return model;
							} else {
								if ($author$project$CapturedAction$identity(captured) === 'control:menu-close') {
									return A2(
										$author$project$DesignDemo$menuUpdate,
										$author$project$Menu$Dismiss(menu.ae),
										model);
								} else {
									var _v9 = $elm$core$String$toInt(
										A2(
											$elm$core$String$dropLeft,
											10,
											$author$project$CapturedAction$identity(captured)));
									if (!_v9.$) {
										var index = _v9.a;
										return A2(
											$author$project$DesignDemo$menuUpdate,
											A3($author$project$Menu$Activate, menu.ae, menu.co, index),
											model);
									} else {
										return model;
									}
								}
							}
						} else {
							return model;
						}
					default:
						break _v0$7;
				}
			} else {
				break _v0$7;
			}
		}
		return model;
	});
var $author$project$DesignDemo$update = F2(
	function (_v0, model) {
		var raw = _v0;
		var result = A2($author$project$DesignDemo$apply, raw, model);
		var next = _Utils_update(
			result,
			{ba: model.ba + 1});
		return _Utils_Tuple2(
			next,
			$author$project$DesignDemo$fixtureObserved(
				$author$project$DesignDemo$observe(next)));
	});
var $elm$virtual_dom$VirtualDom$attribute = F2(
	function (key, value) {
		return A2(
			_VirtualDom_attribute,
			_VirtualDom_noOnOrFormAction(key),
			_VirtualDom_noJavaScriptOrHtmlUri(value));
	});
var $elm$html$Html$Attributes$attribute = $elm$virtual_dom$VirtualDom$attribute;
var $elm$html$Html$Attributes$stringProperty = F2(
	function (key, string) {
		return A2(
			_VirtualDom_property,
			key,
			$elm$json$Json$Encode$string(string));
	});
var $elm$html$Html$Attributes$class = $elm$html$Html$Attributes$stringProperty('className');
var $elm$html$Html$div = _VirtualDom_node('div');
var $elm$html$Html$p = _VirtualDom_node('p');
var $elm$virtual_dom$VirtualDom$text = _VirtualDom_text;
var $elm$html$Html$text = $elm$virtual_dom$VirtualDom$text;
var $elm$html$Html$Attributes$alt = $elm$html$Html$Attributes$stringProperty('alt');
var $elm$html$Html$img = _VirtualDom_node('img');
var $elm$virtual_dom$VirtualDom$node = function (tag) {
	return _VirtualDom_node(
		_VirtualDom_noScript(tag));
};
var $elm$html$Html$node = $elm$virtual_dom$VirtualDom$node;
var $elm$virtual_dom$VirtualDom$keyedNode = function (tag) {
	return _VirtualDom_keyedNode(
		_VirtualDom_noScript(tag));
};
var $elm$html$Html$Keyed$node = $elm$virtual_dom$VirtualDom$keyedNode;
var $elm$html$Html$span = _VirtualDom_node('span');
var $elm$html$Html$Attributes$src = function (url) {
	return A2(
		$elm$html$Html$Attributes$stringProperty,
		'src',
		_VirtualDom_noJavaScriptOrHtmlUri(url));
};
var $author$project$PreviewLifecycle$render = F4(
	function (root, caption, info, _v0) {
		var st = _v0;
		var title = st.a.ag ? 'Preview unavailable' : info.cQ;
		var current = $author$project$PreviewLifecycle$status(st);
		var fidelity = A2(
			$elm$core$Maybe$withDefault,
			'',
			A2(
				$elm$core$Maybe$map,
				function (packet) {
					return (packet.a7 === 1) ? 'Window family' : 'Client content';
				},
				$author$project$PreviewLifecycle$drawablePacket(current)));
		var label = function () {
			switch (current.$) {
				case 0:
					return 'Live preview';
				case 1:
					return 'Historical preview';
				case 2:
					return 'Preview loading';
				default:
					return 'Preview unavailable';
			}
		}();
		var contents = function () {
			var _v1 = $author$project$PreviewLifecycle$drawablePacket(current);
			if (!_v1.$) {
				var packet = _v1.a;
				return _List_fromArray(
					[
						_Utils_Tuple2(
						'frame:' + $author$project$PreviewLifecycle$handleString(packet.E),
						A2(
							$elm$html$Html$img,
							_List_fromArray(
								[
									$elm$html$Html$Attributes$class('preview-image'),
									$elm$html$Html$Attributes$src(
									'elm-shell://preview/' + $author$project$PreviewLifecycle$handleString(packet.E)),
									$elm$html$Html$Attributes$alt(''),
									A2($elm$html$Html$Attributes$attribute, 'aria-hidden', 'true')
								]),
							_List_Nil))
					]);
			} else {
				return _Utils_ap(
					st.a.ag ? _List_Nil : A2(
						$elm$core$Maybe$withDefault,
						_List_Nil,
						A2(
							$elm$core$Maybe$map,
							function (_v2) {
								var token = _v2;
								return _List_fromArray(
									[
										_Utils_Tuple2(
										'icon:' + token,
										A2(
											$elm$html$Html$img,
											_List_fromArray(
												[
													$elm$html$Html$Attributes$class('preview-icon'),
													$elm$html$Html$Attributes$src('elm-shell://icon/' + token),
													$elm$html$Html$Attributes$alt(''),
													A2($elm$html$Html$Attributes$attribute, 'aria-hidden', 'true')
												]),
											_List_Nil))
									]);
							},
							info.cx)),
					_List_fromArray(
						[
							_Utils_Tuple2(
							'title',
							A2(
								$elm$html$Html$span,
								_List_fromArray(
									[
										$elm$html$Html$Attributes$class('preview-title')
									]),
								_List_fromArray(
									[
										$elm$html$Html$text(title)
									])))
						]));
			}
		}();
		return A3(
			$elm$html$Html$Keyed$node,
			root,
			_List_fromArray(
				[
					$elm$html$Html$Attributes$class('window-preview'),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-preview-state',
					$author$project$PreviewLifecycle$statusName(current))
				]),
			_Utils_ap(
				contents,
				_List_fromArray(
					[
						_Utils_Tuple2(
						'status',
						A3(
							$elm$html$Html$node,
							caption,
							_List_Nil,
							_List_fromArray(
								[
									A2(
									$elm$html$Html$span,
									_List_fromArray(
										[
											$elm$html$Html$Attributes$class('preview-state')
										]),
									_List_fromArray(
										[
											$elm$html$Html$text(label)
										])),
									A2(
									$elm$html$Html$span,
									_List_fromArray(
										[
											$elm$html$Html$Attributes$class('preview-fidelity')
										]),
									_List_fromArray(
										[
											$elm$html$Html$text(fidelity)
										]))
								])))
					])));
	});
var $author$project$PreviewLifecycle$view = A2($author$project$PreviewLifecycle$render, 'figure', 'figcaption');
var $elm$html$Html$button = _VirtualDom_node('button');
var $elm$html$Html$Attributes$boolProperty = F2(
	function (key, bool) {
		return A2(
			_VirtualDom_property,
			key,
			$elm$json$Json$Encode$bool(bool));
	});
var $elm$html$Html$Attributes$disabled = $elm$html$Html$Attributes$boolProperty('disabled');
var $elm$html$Html$h1 = _VirtualDom_node('h1');
var $elm$html$Html$Attributes$id = $elm$html$Html$Attributes$stringProperty('id');
var $author$project$SurfaceRenderer$viewWithPreview = F4(
	function (preview, popup, send, current) {
		var snapshot = current;
		var control = function (item) {
			var kind = A2($elm$core$String$startsWith, 'bar:group:', item.aq) ? 'control-group' : ((item.aq === 'bar:recovery-refresh') ? 'control-recovery' : 'control-utility');
			return A2(
				$elm$html$Html$button,
				_List_fromArray(
					[
						$elm$html$Html$Attributes$class(kind),
						$elm$html$Html$Attributes$id(item.a4),
						A2($elm$html$Html$Attributes$attribute, 'aria-label', item.bB),
						$elm$html$Html$Attributes$disabled(!item.q),
						A2($elm$html$Html$Attributes$attribute, 'data-surface-control', item.aq),
						A2(
						$elm$html$Html$Attributes$attribute,
						'role',
						(popup && (snapshot.V === 'menu')) ? 'menuitem' : 'button'),
						A2(
						$elm$html$Html$Attributes$attribute,
						'aria-current',
						(popup && ((snapshot.V === 'menu') && (item.bl === 'Selected'))) ? 'true' : 'false')
					]),
				_List_fromArray(
					[
						preview(item.aq),
						A2(
						$elm$html$Html$span,
						_List_fromArray(
							[
								$elm$html$Html$Attributes$class('control-label')
							]),
						_List_fromArray(
							[
								$elm$html$Html$text(item.bP)
							])),
						A2(
						$elm$html$Html$span,
						_List_fromArray(
							[
								$elm$html$Html$Attributes$class('control-detail')
							]),
						_List_fromArray(
							[
								$elm$html$Html$text(item.bl)
							]))
					]));
		};
		return popup ? A2(
			$elm$html$Html$div,
			_List_fromArray(
				[
					$elm$html$Html$Attributes$class('surface-popup'),
					A2($elm$html$Html$Attributes$attribute, 'data-mode', snapshot.V),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-publication',
					$author$project$UInt64$string(snapshot.ba)),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-lease',
					$author$project$UInt64$string(snapshot.bn))
				]),
			_List_fromArray(
				[
					A2(
					$elm$html$Html$h1,
					_List_Nil,
					_List_fromArray(
						[
							$elm$html$Html$text(
							(snapshot.V === 'applications') ? 'Applications' : ((snapshot.V === 'menu') ? 'Window actions' : 'Choose a window'))
						])),
					A2(
					$elm$html$Html$p,
					_List_fromArray(
						[
							A2($elm$html$Html$Attributes$attribute, 'role', 'status'),
							A2($elm$html$Html$Attributes$attribute, 'aria-live', 'polite')
						]),
					_List_fromArray(
						[
							$elm$html$Html$text(snapshot.bx)
						])),
					A2(
					$elm$html$Html$div,
					_List_fromArray(
						[
							$elm$html$Html$Attributes$class('surface-controls'),
							A2(
							$elm$html$Html$Attributes$attribute,
							'role',
							(snapshot.V === 'menu') ? 'menu' : 'group')
						]),
					A2($elm$core$List$map, control, snapshot.Y))
				])) : A3(
			$elm$html$Html$Keyed$node,
			'div',
			_List_fromArray(
				[
					$elm$html$Html$Attributes$class('surface-bar'),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-publication',
					$author$project$UInt64$string(snapshot.ba)),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-lease',
					$author$project$UInt64$string(snapshot.bn))
				]),
			_Utils_ap(
				A2(
					$elm$core$List$map,
					function (item) {
						return _Utils_Tuple2(
							'control:' + item.aq,
							control(item));
					},
					snapshot.ab),
				_List_fromArray(
					[
						_Utils_Tuple2(
						'status',
						A2(
							$elm$html$Html$span,
							_List_fromArray(
								[
									$elm$html$Html$Attributes$class('surface-status'),
									A2($elm$html$Html$Attributes$attribute, 'role', 'status'),
									A2($elm$html$Html$Attributes$attribute, 'aria-live', 'polite')
								]),
							_List_fromArray(
								[
									$elm$html$Html$text(snapshot.bx)
								])))
					])));
	});
var $author$project$SurfaceRenderer$view = F3(
	function (popup, send, current) {
		return A4(
			$author$project$SurfaceRenderer$viewWithPreview,
			function (_v0) {
				return $elm$html$Html$text('');
			},
			popup,
			send,
			current);
	});
var $author$project$DesignDemo$view = function (model) {
	if (model.o === 'preview') {
		return A2(
			$elm$core$Maybe$withDefault,
			$elm$html$Html$text('Preview fixture unavailable'),
			A2(
				$elm$core$Maybe$map,
				$author$project$PreviewLifecycle$view(
					{bf: 'Text editor', cx: $elm$core$Maybe$Nothing, cQ: 'Design notes'}),
				model.aj));
	} else {
		var _v0 = $author$project$DesignDemo$projection(model);
		if (!_v0.$) {
			var shown = _v0.a;
			return A2(
				$elm$html$Html$div,
				_List_fromArray(
					[
						$elm$html$Html$Attributes$class('elm-specimen'),
						A2(
						$elm$html$Html$Attributes$attribute,
						'data-fixture-publication',
						$elm$core$String$fromInt(model.ba))
					]),
				_List_fromArray(
					[
						A3(
						$author$project$SurfaceRenderer$view,
						!A2(
							$elm$core$List$member,
							model.o,
							_List_fromArray(
								['bar', 'status', 'utility'])),
						function (_v1) {
							return $elm$json$Json$Encode$null;
						},
						shown),
						A2(
						$elm$html$Html$p,
						_List_fromArray(
							[
								$elm$html$Html$Attributes$class('fixture-summary')
							]),
						_List_fromArray(
							[
								$elm$html$Html$text(
								(model.o === 'menu') ? $author$project$DesignDemo$notice(model) : ((model.o === 'bar') ? $author$project$DesignDemo$decision(model.ak) : 'Read-only presentation fixture. No native action is issued.'))
							]))
					]));
		} else {
			var error = _v0.a;
			return $elm$html$Html$text(error);
		}
	}
};
var $author$project$DesignDemo$main = $elm$browser$Browser$element(
	{
		cz: function (flags) {
			var model = $author$project$DesignDemo$initial(
				A2(
					$elm$core$Result$withDefault,
					'menu',
					A2(
						$elm$json$Json$Decode$decodeValue,
						A2($elm$json$Json$Decode$field, 'topic', $elm$json$Json$Decode$string),
						flags)));
			return _Utils_Tuple2(
				model,
				$author$project$DesignDemo$fixtureObserved(
					$author$project$DesignDemo$observe(model)));
		},
		cO: function (_v0) {
			return $author$project$DesignDemo$fixtureInput($elm$core$Basics$identity);
		},
		cR: $author$project$DesignDemo$update,
		cS: $author$project$DesignDemo$view
	});
_Platform_export({'DesignDemo':{'init':$author$project$DesignDemo$main($elm$json$Json$Decode$value)(0)}});}(this));