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
	if (region.bB.aW === region.bM.aW)
	{
		return 'on line ' + region.bB.aW;
	}
	return 'on lines ' + region.bB.aW + ' through ' + region.bM.aW;
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
		impl.cD,
		impl.cM,
		impl.cL,
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
		ae: func(record.ae),
		bC: record.bC,
		bx: record.bx
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
		var message = !tag ? value : tag < 3 ? value.a : value.ae;
		var stopPropagation = tag == 1 ? value.b : tag == 3 && value.bC;
		var currentEventNode = (
			stopPropagation && event.stopPropagation(),
			(tag == 2 ? value.b : tag == 3 && value.bx) && event.preventDefault(),
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
		impl.cD,
		impl.cM,
		impl.cL,
		function(sendToApp, initialModel) {
			var view = impl.cN;
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
		impl.cD,
		impl.cM,
		impl.cL,
		function(sendToApp, initialModel) {
			var divertHrefToApp = impl.bz && impl.bz(sendToApp)
			var view = impl.cN;
			var title = _VirtualDom_doc.title;
			var bodyNode = _VirtualDom_doc.body;
			var currNode = _VirtualDom_virtualize(bodyNode);
			return _Browser_makeAnimator(initialModel, function(model)
			{
				_VirtualDom_divertHrefToApp = divertHrefToApp;
				var doc = view(model);
				var nextNode = _VirtualDom_node('body')(_List_Nil)(doc.cr);
				var patches = _VirtualDom_diff(currNode, nextNode);
				bodyNode = _VirtualDom_applyPatches(bodyNode, currNode, patches, sendToApp);
				currNode = nextNode;
				_VirtualDom_divertHrefToApp = 0;
				(title !== doc.bD) && (_VirtualDom_doc.title = title = doc.bD);
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
	var onUrlChange = impl.cF;
	var onUrlRequest = impl.cG;
	var key = function() { key.a(onUrlChange(_Browser_getUrl())); };

	return _Browser_document({
		bz: function(sendToApp)
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
							&& curr.aL === next.aL
							&& curr.bU === next.bU
							&& curr.b5.a === next.b5.a
						)
							? $elm$browser$Browser$Internal(next)
							: $elm$browser$Browser$External(href)
					));
				}
			});
		},
		cD: function(flags)
		{
			return A3(impl.cD, flags, _Browser_getUrl(), key);
		},
		cN: impl.cN,
		cM: impl.cM,
		cL: impl.cL
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
		? { cB: 'hidden', cs: 'visibilitychange' }
		:
	(typeof _VirtualDom_doc.mozHidden !== 'undefined')
		? { cB: 'mozHidden', cs: 'mozvisibilitychange' }
		:
	(typeof _VirtualDom_doc.msHidden !== 'undefined')
		? { cB: 'msHidden', cs: 'msvisibilitychange' }
		:
	(typeof _VirtualDom_doc.webkitHidden !== 'undefined')
		? { cB: 'webkitHidden', cs: 'webkitvisibilitychange' }
		: { cB: 'hidden', cs: 'visibilitychange' };
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
		S: _Browser_getScene(),
		cj: {
			cl: _Browser_window.pageXOffset,
			cm: _Browser_window.pageYOffset,
			ck: _Browser_doc.documentElement.clientWidth,
			bT: _Browser_doc.documentElement.clientHeight
		}
	};
}

function _Browser_getScene()
{
	var body = _Browser_doc.body;
	var elem = _Browser_doc.documentElement;
	return {
		ck: Math.max(body.scrollWidth, body.offsetWidth, elem.scrollWidth, elem.offsetWidth, elem.clientWidth),
		bT: Math.max(body.scrollHeight, body.offsetHeight, elem.scrollHeight, elem.offsetHeight, elem.clientHeight)
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
			S: {
				ck: node.scrollWidth,
				bT: node.scrollHeight
			},
			cj: {
				cl: node.scrollLeft,
				cm: node.scrollTop,
				ck: node.clientWidth,
				bT: node.clientHeight
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
			S: _Browser_getScene(),
			cj: {
				cl: x,
				cm: y,
				ck: _Browser_doc.documentElement.clientWidth,
				bT: _Browser_doc.documentElement.clientHeight
			},
			cx: {
				cl: x + rect.left,
				cm: y + rect.top,
				ck: rect.width,
				bT: rect.height
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
var $author$project$Popup$Action = function (a) {
	return {$: 1, a: a};
};
var $author$project$Popup$NativeClosed = function (a) {
	return {$: 5, a: a};
};
var $author$project$Popup$NativeGrant = function (a) {
	return {$: 3, a: a};
};
var $author$project$Popup$NativeIssued = function (a) {
	return {$: 6, a: a};
};
var $author$project$Popup$NativePreview = function (a) {
	return {$: 2, a: a};
};
var $author$project$Popup$NativeQuarantine = function (a) {
	return {$: 4, a: a};
};
var $author$project$Popup$NativeRetirement = function (a) {
	return {$: 8, a: a};
};
var $author$project$Popup$NativeRetry = function (a) {
	return {$: 7, a: a};
};
var $author$project$Popup$Present = function (a) {
	return {$: 0, a: a};
};
var $elm$core$Basics$True = 0;
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
		if (!builder.l) {
			return A4(
				$elm$core$Array$Array_elm_builtin,
				$elm$core$Elm$JsArray$length(builder.o),
				$elm$core$Array$shiftStep,
				$elm$core$Elm$JsArray$empty,
				builder.o);
		} else {
			var treeLen = builder.l * $elm$core$Array$branchFactor;
			var depth = $elm$core$Basics$floor(
				A2($elm$core$Basics$logBase, $elm$core$Array$branchFactor, treeLen - 1));
			var correctNodeList = reverseNodeList ? $elm$core$List$reverse(builder.s) : builder.s;
			var tree = A2($elm$core$Array$treeFromBuilder, correctNodeList, builder.l);
			return A4(
				$elm$core$Array$Array_elm_builtin,
				$elm$core$Elm$JsArray$length(builder.o) + treeLen,
				A2($elm$core$Basics$max, 5, depth * $elm$core$Array$shiftStep),
				tree,
				builder.o);
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
					{s: nodeList, l: (len / $elm$core$Array$branchFactor) | 0, o: tail});
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
var $elm$virtual_dom$VirtualDom$attribute = F2(
	function (key, value) {
		return A2(
			_VirtualDom_attribute,
			_VirtualDom_noOnOrFormAction(key),
			_VirtualDom_noJavaScriptOrHtmlUri(value));
	});
var $elm$html$Html$Attributes$attribute = $elm$virtual_dom$VirtualDom$attribute;
var $elm$core$Platform$Sub$batch = _Platform_batch;
var $author$project$Presentation$current = function (_v0) {
	var model = _v0;
	return model.ah;
};
var $elm$html$Html$div = _VirtualDom_node('div');
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
		return {bR: fragment, bU: host, b3: path, b5: port_, aL: protocol, b9: query};
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
var $author$project$Popup$Idle = {$: 0};
var $author$project$Presentation$Model = $elm$core$Basics$identity;
var $author$project$UInt64$Counter = $elm$core$Basics$identity;
var $author$project$UInt64$zero = '0';
var $author$project$Presentation$initial = {br: $author$project$UInt64$zero, bs: $author$project$UInt64$zero, ah: $elm$core$Maybe$Nothing};
var $author$project$RetainedPreviewPresenter$Model = F4(
	function (a, b, c, d) {
		return {$: 0, a: a, b: b, c: c, d: d};
	});
var $author$project$PreviewPresenter$Model = F4(
	function (a, b, c, d) {
		return {$: 0, a: a, b: b, c: c, d: d};
	});
var $elm$core$Dict$RBEmpty_elm_builtin = {$: -2};
var $elm$core$Dict$empty = $elm$core$Dict$RBEmpty_elm_builtin;
var $author$project$NativeActorRetirement$empty = {bJ: $elm$core$Maybe$Nothing, bd: $elm$core$Maybe$Nothing, b7: $author$project$UInt64$zero, aN: $elm$core$Maybe$Nothing};
var $author$project$PreviewPresenter$emptyScoped = {N: false, u: false, W: $elm$core$Dict$empty, r: $elm$core$Maybe$Nothing, b7: $author$project$UInt64$zero};
var $author$project$PreviewPresenter$initial = A4($author$project$PreviewPresenter$Model, $elm$core$Dict$empty, $elm$core$Maybe$Nothing, $author$project$NativeActorRetirement$empty, $author$project$PreviewPresenter$emptyScoped);
var $author$project$RetainedPreviewPresenter$initial = A4($author$project$RetainedPreviewPresenter$Model, $author$project$PreviewPresenter$initial, $elm$core$Maybe$Nothing, $elm$core$Maybe$Nothing, _List_Nil);
var $author$project$Popup$initial = {L: $author$project$Popup$Idle, as: $elm$core$Maybe$Nothing, y: $elm$core$Maybe$Nothing, z: $author$project$Presentation$initial, f: $author$project$RetainedPreviewPresenter$initial};
var $elm$core$Basics$neq = _Utils_notEqual;
var $author$project$Popup$isComposing = function (model) {
	return !_Utils_eq(model.L, $author$project$Popup$Idle);
};
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
var $elm$json$Json$Decode$value = _Json_decodeValue;
var $author$project$Popup$nativePreviewClosed = _Platform_incomingPort('nativePreviewClosed', $elm$json$Json$Decode$value);
var $author$project$Popup$nativePreviewGrants = _Platform_incomingPort('nativePreviewGrants', $elm$json$Json$Decode$value);
var $author$project$Popup$nativePreviewIssued = _Platform_incomingPort('nativePreviewIssued', $elm$json$Json$Decode$value);
var $author$project$Popup$nativePreviewQuarantine = _Platform_incomingPort('nativePreviewQuarantine', $elm$json$Json$Decode$value);
var $author$project$Popup$nativePreviewRetirement = _Platform_incomingPort('nativePreviewRetirement', $elm$json$Json$Decode$value);
var $author$project$Popup$nativePreviewRetry = _Platform_incomingPort('nativePreviewRetry', $elm$json$Json$Decode$value);
var $author$project$Popup$nativePreviews = _Platform_incomingPort('nativePreviews', $elm$json$Json$Decode$value);
var $elm$core$Platform$Cmd$batch = _Platform_batch;
var $elm$core$Platform$Cmd$none = $elm$core$Platform$Cmd$batch(_List_Nil);
var $author$project$SurfaceRenderer$Snapshot = $elm$core$Basics$identity;
var $author$project$SurfaceRenderer$fieldIdentity = function (_v0) {
	var snapshot = _v0;
	return (snapshot.c === 'files') ? 'control:files-path' : 'control:search';
};
var $author$project$SurfaceRenderer$pendingQuery = F2(
	function (query, current) {
		var snapshot = current;
		return _Utils_update(
			snapshot,
			{
				n: A2(
					$elm$core$List$map,
					function (item) {
						return _Utils_eq(
							item.aG,
							$author$project$SurfaceRenderer$fieldIdentity(current)) ? _Utils_update(
							item,
							{bY: query}) : ((A2($elm$core$String$startsWith, 'entry:', item.aG) || ((item.aG === 'files:open-path') || (A2($elm$core$String$startsWith, 'files:collection:', item.aG) || (item.aG === 'files:home')))) ? _Utils_update(
							item,
							{an: false}) : item);
					},
					snapshot.n)
			});
	});
var $author$project$Popup$presentation = _Platform_incomingPort('presentation', $elm$json$Json$Decode$value);
var $author$project$Popup$requestAction = _Platform_incomingPort('requestAction', $elm$json$Json$Decode$value);
var $elm$virtual_dom$VirtualDom$text = _VirtualDom_text;
var $elm$html$Html$text = $elm$virtual_dom$VirtualDom$text;
var $author$project$Popup$Preediting = function (a) {
	return {$: 1, a: a};
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
var $elm$json$Json$Decode$andThen = _Json_andThen;
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
var $elm$core$String$any = _String_any;
var $elm$json$Json$Decode$fail = _Json_fail;
var $elm$core$Basics$not = _Basics_not;
var $elm$json$Json$Decode$string = _Json_decodeString;
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
		return {a4: ariaLabel, q: detail, C: domId, an: enabled, aG: identity, bY: label};
	});
var $elm$json$Json$Decode$bool = _Json_decodeBool;
var $elm$json$Json$Decode$field = _Json_decodeField;
var $elm$json$Json$Decode$list = _Json_decodeList;
var $elm$json$Json$Decode$map6 = _Json_map6;
var $elm$json$Json$Decode$keyValuePairs = _Json_decodeKeyValuePairs;
var $elm$core$List$sortBy = _List_sortBy;
var $elm$core$List$sort = function (xs) {
	return A2($elm$core$List$sortBy, $elm$core$Basics$identity, xs);
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
var $elm$core$Basics$ge = _Utils_ge;
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
var $author$project$Settings$Night = 0;
var $author$project$Settings$defaults = {a7: false, bg: false, a0: 100, bn: 0};
var $elm$core$Set$Set_elm_builtin = $elm$core$Basics$identity;
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
var $elm$json$Json$Decode$int = _Json_decodeInt;
var $elm$core$List$isEmpty = function (xs) {
	if (!xs.b) {
		return true;
	} else {
		return false;
	}
};
var $elm$json$Json$Decode$map8 = _Json_map8;
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
var $elm$core$Tuple$pair = F2(
	function (a, b) {
		return _Utils_Tuple2(a, b);
	});
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
var $elm$core$Result$toMaybe = function (result) {
	if (!result.$) {
		var v = result.a;
		return $elm$core$Maybe$Just(v);
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$Settings$Values = F4(
	function (theme, textScale, effectsOff, reducedTransparency) {
		return {a7: effectsOff, bg: reducedTransparency, a0: textScale, bn: theme};
	});
var $elm$json$Json$Decode$map4 = _Json_map4;
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
var $author$project$Settings$Dawn = 1;
var $author$project$Settings$HighContrast = 2;
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
				return {a7: false, bg: false, a0: scale, bn: theme};
			}),
		A2($elm$json$Json$Decode$field, 'theme', $author$project$Settings$themeDecoder),
		A2($elm$json$Json$Decode$field, 'textScale', $author$project$Settings$scaleDecoder)));
var $elm$json$Json$Decode$oneOf = _Json_oneOf;
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
				hasMotion ? _List_fromArray(
					['motion']) : _List_Nil)),
		A3(
			$elm$json$Json$Decode$map2,
			$elm$core$Tuple$pair,
			motionDecoder,
			A9(
				$elm$json$Json$Decode$map8,
				F8(
					function (version, shown, scoped, current, notice, bar, popup, appearance) {
						return {G: appearance, K: bar, aS: current, _: notice, n: popup, by: scoped, bA: shown, ci: version};
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
			var record = _v0.b;
			var unique = function (names) {
				return _Utils_eq(
					$elm$core$List$length(names),
					$elm$core$Set$size(
						$elm$core$Set$fromList(names)));
			};
			var all = _Utils_ap(record.K, record.n);
			var identities = A2(
				$elm$core$List$map,
				function ($) {
					return $.aG;
				},
				all);
			return ((record.ci !== 2) || (_Utils_eq(record.bA, $author$project$UInt64$zero) || ((!A2(
				$elm$core$List$member,
				record.aS,
				_List_fromArray(
					['closed', 'picker', 'applications', 'menu', 'overview', 'switcher', 'snap', 'settings', 'notifications', 'system', 'files', 'jump']))) || (((record.aS !== 'closed') && _Utils_eq(record.by, $author$project$UInt64$zero)) || (((record.aS === 'closed') && (!$elm$core$List$isEmpty(record.n))) || ((!unique(identities)) || ((!unique(
				A2(
					$elm$core$List$map,
					function ($) {
						return $.C;
					},
					all))) || A2(
				$elm$core$List$any,
				function (control) {
					return $elm$core$String$isEmpty(control.aG) || $elm$core$String$isEmpty(control.C);
				},
				all)))))))) ? $elm$core$Result$Err('Invalid presentation scope/identities') : $elm$core$Result$Ok(
				{G: record.G, K: record.K, bs: record.by, c: record.aS, bb: motion, n: record.n, bf: record.bA, ai: record._});
		},
		A2(
			$elm$core$Result$mapError,
			$elm$json$Json$Decode$errorToString,
			A2($elm$json$Json$Decode$decodeValue, decoder, raw)));
};
var $author$project$SurfaceRenderer$lease = function (_v0) {
	var snapshot = _v0;
	return snapshot.bs;
};
var $author$project$SurfaceRenderer$publication = function (_v0) {
	var snapshot = _v0;
	return snapshot.bf;
};
var $author$project$Presentation$accept = F2(
	function (raw, prior) {
		var model = prior;
		var _v0 = $author$project$SurfaceRenderer$decode(raw);
		if (_v0.$ === 1) {
			return _Utils_update(
				model,
				{ah: $elm$core$Maybe$Nothing});
		} else {
			var snapshot = _v0.a;
			return ((A2(
				$author$project$UInt64$compare,
				$author$project$SurfaceRenderer$publication(snapshot),
				model.br) !== 2) || (!A2(
				$author$project$UInt64$compare,
				$author$project$SurfaceRenderer$lease(snapshot),
				model.bs))) ? prior : {
				br: $author$project$SurfaceRenderer$publication(snapshot),
				bs: $author$project$SurfaceRenderer$lease(snapshot),
				ah: $elm$core$Maybe$Just(snapshot)
			};
		}
	});
var $author$project$Popup$actions = _Platform_outgoingPort('actions', $elm$core$Basics$identity);
var $elm$core$Maybe$andThen = F2(
	function (callback, maybeValue) {
		if (!maybeValue.$) {
			var value = maybeValue.a;
			return callback(value);
		} else {
			return $elm$core$Maybe$Nothing;
		}
	});
var $elm$core$Dict$isEmpty = function (dict) {
	if (dict.$ === -2) {
		return true;
	} else {
		return false;
	}
};
var $author$project$NativePreviewRealm$same = F2(
	function (left, right) {
		return _Utils_eq(left, right);
	});
var $elm$core$Maybe$withDefault = F2(
	function (_default, maybe) {
		if (!maybe.$) {
			var value = maybe.a;
			return value;
		} else {
			return _default;
		}
	});
var $author$project$PreviewPresenter$closeRealm = F2(
	function (domain, _v0) {
		var entries = _v0.a;
		var catalog = _v0.b;
		var ledger = _v0.c;
		var scoped = _v0.d;
		return ($elm$core$Dict$isEmpty(entries) && A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (grant) {
					return A2($author$project$NativePreviewRealm$same, grant.aT, domain);
				},
				scoped.r))) ? $elm$core$Maybe$Just(
			A4(
				$author$project$PreviewPresenter$Model,
				entries,
				catalog,
				ledger,
				_Utils_update(
					scoped,
					{N: true, u: true}))) : $elm$core$Maybe$Nothing;
	});
var $elm$core$Basics$composeR = F3(
	function (f, g, x) {
		return g(
			f(x));
	});
var $author$project$NativePreviewProposalIngress$pending = function (_v0) {
	var rows = _v0.b;
	return rows;
};
var $author$project$RetainedPreviewPresenter$closeRealm = F2(
	function (domain, _v0) {
		var policy = _v0.a;
		var grant = _v0.b;
		var ingress = _v0.c;
		var deferred = _v0.d;
		return ((!$elm$core$List$isEmpty(deferred)) || A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				A2(
					$elm$core$Basics$composeR,
					$author$project$NativePreviewProposalIngress$pending,
					A2($elm$core$Basics$composeR, $elm$core$List$isEmpty, $elm$core$Basics$not)),
				ingress))) ? $elm$core$Maybe$Nothing : A2(
			$elm$core$Maybe$map,
			function (next) {
				return A4($author$project$RetainedPreviewPresenter$Model, next, grant, ingress, deferred);
			},
			A2($author$project$PreviewPresenter$closeRealm, domain, policy));
	});
var $author$project$CapturedAction$CapturedAction = $elm$core$Basics$identity;
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
					return ((version === 2) && ((kind === 'surface-action') && ((!_Utils_eq(value.bf, $author$project$UInt64$zero)) && (A2(
						$elm$core$List$member,
						value.bm,
						_List_fromArray(
							['bar', 'popup'])) && ((!$elm$core$String$isEmpty(value.aG)) && (($elm$core$String$length(value.aG) <= 512) && (!A2(
						$elm$core$String$any,
						function (c) {
							return $elm$core$Char$toCode(c) < 32;
						},
						value.aG)))))))) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Action scope');
				},
				A7(
					$elm$json$Json$Decode$map6,
					F6(
						function (version, kind, shown, scoped, role, name) {
							return _Utils_Tuple3(
								version,
								kind,
								{aG: name, bs: scoped, bf: shown, bm: role});
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
				return _Utils_eq(control.aG, identity) && control.an;
			},
			popup ? snapshot.n : snapshot.K);
	});
var $elm$json$Json$Encode$int = _Json_wrap;
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
var $author$project$UInt64$string = function (_v0) {
	var value = _v0;
	return value;
};
var $author$project$CapturedAction$encode = function (_v0) {
	var value = _v0;
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'surface',
				$elm$json$Json$Encode$string(value.bm)),
				_Utils_Tuple2(
				'surfaceProtocol',
				$elm$json$Json$Encode$int(2)),
				_Utils_Tuple2(
				'kind',
				$elm$json$Json$Encode$string('surface-action')),
				_Utils_Tuple2(
				'publication',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(value.bf))),
				_Utils_Tuple2(
				'lease',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(value.bs))),
				_Utils_Tuple2(
				'id',
				$elm$json$Json$Encode$string(value.aG))
			]));
};
var $author$project$CapturedAction$identity = function (_v0) {
	var value = _v0;
	return value.aG;
};
var $author$project$CapturedAction$lease = function (_v0) {
	var value = _v0;
	return value.bs;
};
var $author$project$CapturedAction$publication = function (_v0) {
	var value = _v0;
	return value.bf;
};
var $author$project$CapturedAction$surface = function (_v0) {
	var value = _v0;
	return value.bm;
};
var $author$project$Presentation$dispatch = F3(
	function (popup, raw, _v0) {
		var model = _v0;
		var _v1 = _Utils_Tuple2(
			model.ah,
			$author$project$CapturedAction$decode(raw));
		if ((!_v1.a.$) && (!_v1.b.$)) {
			var snapshot = _v1.a.a;
			var event = _v1.b.a;
			return (_Utils_eq(
				$author$project$CapturedAction$publication(event),
				$author$project$SurfaceRenderer$publication(snapshot)) && (_Utils_eq(
				$author$project$CapturedAction$lease(event),
				$author$project$SurfaceRenderer$lease(snapshot)) && (_Utils_eq(
				$author$project$CapturedAction$surface(event),
				popup ? 'popup' : 'bar') && A3(
				$author$project$SurfaceRenderer$enabled,
				popup,
				$author$project$CapturedAction$identity(event),
				snapshot)))) ? $elm$core$Maybe$Just(
				$author$project$CapturedAction$encode(event)) : $elm$core$Maybe$Nothing;
		} else {
			return $elm$core$Maybe$Nothing;
		}
	});
var $author$project$NativePreviewRealm$Domain = F4(
	function (lifetime, session, frontend, receiverEpoch) {
		return {a9: frontend, aV: lifetime, ca: receiverEpoch, bk: session};
	});
var $elm$json$Json$Decode$map3 = _Json_map3;
var $author$project$NativePreviewRealm$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (n) {
		return (!_Utils_eq(n, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(n) : $elm$json$Json$Decode$fail('Positive native realm identity');
	},
	$author$project$UInt64$decoder);
var $author$project$NativePreviewRealm$strict = F2(
	function (fields, decoder) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? decoder : $elm$json$Json$Decode$fail('Exact native preview realm fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$NativePreviewRealm$domainDecoder = A3(
	$elm$json$Json$Decode$map2,
	F2(
		function (_v0, epoch) {
			var lifetime = _v0.a;
			var session = _v0.b;
			var frontend = _v0.c;
			return A4($author$project$NativePreviewRealm$Domain, lifetime, session, frontend, epoch);
		}),
	A2(
		$elm$json$Json$Decode$field,
		'binding',
		A2(
			$author$project$NativePreviewRealm$strict,
			_List_fromArray(
				['lifetime', 'session', 'frontend']),
			A4(
				$elm$json$Json$Decode$map3,
				F3(
					function (a, b, c) {
						return _Utils_Tuple3(a, b, c);
					}),
				A2($elm$json$Json$Decode$field, 'lifetime', $author$project$NativePreviewRealm$positive),
				A2($elm$json$Json$Decode$field, 'session', $author$project$NativePreviewRealm$positive),
				A2($elm$json$Json$Decode$field, 'frontend', $author$project$NativePreviewRealm$positive)))),
	A2($elm$json$Json$Decode$field, 'receiverEpoch', $author$project$NativePreviewRealm$positive));
var $elm$json$Json$Decode$map5 = _Json_map5;
var $author$project$SurfaceRenderer$mode = function (_v0) {
	var snapshot = _v0;
	return snapshot.c;
};
var $author$project$Presentation$query = F2(
	function (value, _v0) {
		var model = _v0;
		return ((_Utils_cmp(
			$elm$core$String$length(value),
			A2(
				$elm$core$Maybe$withDefault,
				256,
				A2(
					$elm$core$Maybe$map,
					function (snapshot) {
						return ($author$project$SurfaceRenderer$mode(snapshot) === 'files') ? 512 : 256;
					},
					model.ah))) > 0) || A2(
			$elm$core$String$any,
			function (c) {
				return ($elm$core$Char$toCode(c) < 32) || ($elm$core$Char$toCode(c) === 127);
			},
			value)) ? $elm$core$Maybe$Nothing : A2(
			$elm$core$Maybe$andThen,
			function (snapshot) {
				return ((!A2(
					$elm$core$List$member,
					$author$project$SurfaceRenderer$mode(snapshot),
					_List_fromArray(
						['applications', 'files']))) || (!A3(
					$author$project$SurfaceRenderer$enabled,
					true,
					$author$project$SurfaceRenderer$fieldIdentity(snapshot),
					snapshot))) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(
					$elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'surfaceProtocol',
								$elm$json$Json$Encode$int(2)),
								_Utils_Tuple2(
								'kind',
								$elm$json$Json$Encode$string('surface-query')),
								_Utils_Tuple2(
								'surface',
								$elm$json$Json$Encode$string('popup')),
								_Utils_Tuple2(
								'publication',
								$elm$json$Json$Encode$string(
									$author$project$UInt64$string(
										$author$project$SurfaceRenderer$publication(snapshot)))),
								_Utils_Tuple2(
								'lease',
								$elm$json$Json$Encode$string(
									$author$project$UInt64$string(
										$author$project$SurfaceRenderer$lease(snapshot)))),
								_Utils_Tuple2(
								'id',
								$elm$json$Json$Encode$string(
									$author$project$SurfaceRenderer$fieldIdentity(snapshot))),
								_Utils_Tuple2(
								'query',
								$elm$json$Json$Encode$string(value))
							])));
			},
			model.ah);
	});
var $author$project$Presentation$editQuery = F2(
	function (raw, currentModel) {
		var model = currentModel;
		var decoder = A6(
			$elm$json$Json$Decode$map5,
			F5(
				function (version, surface, publication, lease, value) {
					return {bs: lease, bf: publication, bm: surface, bE: value, ci: version};
				}),
			A2($elm$json$Json$Decode$field, 'surfaceProtocol', $elm$json$Json$Decode$int),
			A2($elm$json$Json$Decode$field, 'surface', $elm$json$Json$Decode$string),
			A2($elm$json$Json$Decode$field, 'publication', $author$project$UInt64$decoder),
			A2($elm$json$Json$Decode$field, 'lease', $author$project$UInt64$decoder),
			A2($elm$json$Json$Decode$field, 'query', $elm$json$Json$Decode$string));
		var _v0 = _Utils_Tuple2(
			A2($elm$json$Json$Decode$decodeValue, decoder, raw),
			model.ah);
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var event = _v0.a.a;
			var snapshot = _v0.b.a;
			return ((event.ci !== 2) || ((event.bm !== 'popup') || ((!_Utils_eq(
				event.bf,
				$author$project$SurfaceRenderer$publication(snapshot))) || ((!_Utils_eq(
				event.bs,
				$author$project$SurfaceRenderer$lease(snapshot))) || (!_Utils_eq(
				A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$field, 'id', $elm$json$Json$Decode$string),
					raw),
				$elm$core$Result$Ok(
					$author$project$SurfaceRenderer$fieldIdentity(snapshot)))))))) ? $elm$core$Maybe$Nothing : A2(
				$elm$core$Maybe$map,
				function (wire) {
					return _Utils_Tuple2(event.bE, wire);
				},
				A2($author$project$Presentation$query, event.bE, currentModel));
		} else {
			return $elm$core$Maybe$Nothing;
		}
	});
var $author$project$NativePreviewProposalIngress$Model = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$NativePreviewProposalIngress$empty = function (grant) {
	return A2($author$project$NativePreviewProposalIngress$Model, grant, _List_Nil);
};
var $author$project$NativePreviewRealm$owner = function (domain) {
	return A2(
		$elm$core$String$join,
		':',
		A2(
			$elm$core$List$map,
			$author$project$UInt64$string,
			_List_fromArray(
				[domain.aV, domain.bk, domain.a9])));
};
var $author$project$PreviewPresenter$enrollRealm = F2(
	function (grant, prior) {
		var entries = prior.a;
		var catalog = prior.b;
		var ledger = prior.c;
		var scoped = prior.d;
		var _v0 = scoped.r;
		if (_v0.$ === 1) {
			return ($elm$core$Dict$isEmpty(entries) && (_Utils_eq(catalog, $elm$core$Maybe$Nothing) && _Utils_eq(ledger, $author$project$NativeActorRetirement$empty))) ? $elm$core$Maybe$Just(
				A4(
					$author$project$PreviewPresenter$Model,
					entries,
					catalog,
					_Utils_update(
						ledger,
						{
							bJ: $elm$core$Maybe$Just(
								$author$project$NativePreviewRealm$owner(grant.aT))
						}),
					_Utils_update(
						$author$project$PreviewPresenter$emptyScoped,
						{
							r: $elm$core$Maybe$Just(grant)
						}))) : $elm$core$Maybe$Nothing;
		} else {
			var old = _v0.a;
			return (_Utils_eq(old, grant) && (!scoped.N)) ? $elm$core$Maybe$Just(prior) : ((scoped.N && ($elm$core$Dict$isEmpty(entries) && (_Utils_eq(
				$author$project$NativePreviewRealm$owner(old.aT),
				$author$project$NativePreviewRealm$owner(grant.aT)) && (A2($author$project$UInt64$compare, grant.aT.ca, old.aT.ca) === 2)))) ? $elm$core$Maybe$Just(
				A4(
					$author$project$PreviewPresenter$Model,
					entries,
					catalog,
					_Utils_update(
						ledger,
						{
							bJ: $elm$core$Maybe$Just(
								$author$project$NativePreviewRealm$owner(grant.aT)),
							b7: $author$project$UInt64$zero
						}),
					_Utils_update(
						$author$project$PreviewPresenter$emptyScoped,
						{
							r: $elm$core$Maybe$Just(grant)
						}))) : $elm$core$Maybe$Nothing);
		}
	});
var $author$project$RetainedPreviewPresenter$enrollRealm = F2(
	function (grant, prior) {
		var policy = prior.a;
		var old = prior.b;
		var ingress = prior.c;
		var deferred = prior.d;
		return ((!$elm$core$List$isEmpty(deferred)) || A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				A2(
					$elm$core$Basics$composeR,
					$author$project$NativePreviewProposalIngress$pending,
					A2($elm$core$Basics$composeR, $elm$core$List$isEmpty, $elm$core$Basics$not)),
				ingress))) ? (_Utils_eq(
			old,
			$elm$core$Maybe$Just(grant)) ? $elm$core$Maybe$Just(prior) : $elm$core$Maybe$Nothing) : A2(
			$elm$core$Maybe$map,
			function (next) {
				return A4(
					$author$project$RetainedPreviewPresenter$Model,
					next,
					$elm$core$Maybe$Just(grant),
					$elm$core$Maybe$Just(
						$author$project$NativePreviewProposalIngress$empty(grant)),
					_List_Nil);
			},
			A2($author$project$PreviewPresenter$enrollRealm, grant, policy));
	});
var $author$project$NativePreviewRealm$Envelope = F2(
	function (a, b) {
		return {$: 0, a: a, b: b};
	});
var $author$project$NativePreviewRealm$envelopeDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (_v0) {
		var protocol = _v0.a;
		var kind = _v0.b;
		var envelope = _v0.c;
		return ((protocol === 3) && (kind === 'native-preview-realm-event')) ? $elm$json$Json$Decode$succeed(envelope) : $elm$json$Json$Decode$fail('Typed native preview event envelope');
	},
	A2(
		$author$project$NativePreviewRealm$strict,
		_List_fromArray(
			['previewProtocol', 'kind', 'binding', 'receiverEpoch', 'event']),
		A5(
			$elm$json$Json$Decode$map4,
			F4(
				function (protocol, kind, domain, event) {
					return _Utils_Tuple3(
						protocol,
						kind,
						A2($author$project$NativePreviewRealm$Envelope, domain, event));
				}),
			A2($elm$json$Json$Decode$field, 'previewProtocol', $elm$json$Json$Decode$int),
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			$author$project$NativePreviewRealm$domainDecoder,
			A2($elm$json$Json$Decode$field, 'event', $elm$json$Json$Decode$value))));
var $author$project$NativePreviewRealm$Grant = F2(
	function (domain, capacity) {
		return {bH: capacity, aT: domain};
	});
var $author$project$NativePreviewRealm$grantDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (grant) {
		return ((grant.bH > 0) && (grant.bH <= 1065)) ? $elm$json$Json$Decode$succeed(grant) : $elm$json$Json$Decode$fail('Original bounded native reservation grant');
	},
	A2(
		$author$project$NativePreviewRealm$strict,
		_List_fromArray(
			['binding', 'receiverEpoch', 'capacity']),
		A3(
			$elm$json$Json$Decode$map2,
			$author$project$NativePreviewRealm$Grant,
			$author$project$NativePreviewRealm$domainDecoder,
			A2($elm$json$Json$Decode$field, 'capacity', $elm$json$Json$Decode$int))));
var $author$project$NativePreviewProposalIngress$Packet = F5(
	function (protocol, kind, domain, ordinal, intents) {
		return {aT: domain, bV: intents, bX: kind, b0: ordinal, aL: protocol};
	});
var $author$project$NativePreviewProposalIngress$Ticket = F6(
	function (protocol, kind, domain, ordinal, advisory, wire) {
		return {co: advisory, aT: domain, bX: kind, b0: ordinal, aL: protocol, bF: wire};
	});
var $elm$core$String$foldl = _String_foldl;
var $author$project$NativePreviewProposalIngress$bytes = A2(
	$elm$core$String$foldl,
	F2(
		function (c, n) {
			return n + (($elm$core$Char$toCode(c) < 128) ? 1 : (($elm$core$Char$toCode(c) < 2048) ? 2 : (($elm$core$Char$toCode(c) < 65536) ? 3 : 4)));
		}),
	0);
var $elm$json$Json$Decode$decodeString = _Json_runOnString;
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
var $author$project$NativePreviewProposalIngress$Intent = F2(
	function (identity, command) {
		return {a5: command, aG: identity};
	});
var $author$project$NativePreviewProposalIngress$strict = F2(
	function (fields, decoder) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? decoder : $elm$json$Json$Decode$fail('Exact proposal intent fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$NativePreviewProposalIngress$intentDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (_v0) {
		var name = _v0.a;
		var commands = _v0.b;
		if (commands.b && (!commands.b.b)) {
			var command = commands.a;
			if ((name !== '') && ($author$project$NativePreviewProposalIngress$bytes(name) <= 512)) {
				var _v2 = A2(
					$elm$json$Json$Decode$decodeValue,
					$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value),
					command);
				if (!_v2.$) {
					return $elm$json$Json$Decode$succeed(
						A2($author$project$NativePreviewProposalIngress$Intent, name, command));
				} else {
					return $elm$json$Json$Decode$fail('Object policy command');
				}
			} else {
				return $elm$json$Json$Decode$fail('Bounded original identity');
			}
		} else {
			return $elm$json$Json$Decode$fail('Singleton original policy command');
		}
	},
	A2(
		$author$project$NativePreviewProposalIngress$strict,
		_List_fromArray(
			['identity', 'commands']),
		A3(
			$elm$json$Json$Decode$map2,
			$elm$core$Tuple$pair,
			A2($elm$json$Json$Decode$field, 'identity', $elm$json$Json$Decode$string),
			A2(
				$elm$json$Json$Decode$field,
				'commands',
				$elm$json$Json$Decode$list($elm$json$Json$Decode$value)))));
var $author$project$NativePreviewProposalIngress$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (n) {
		return (!_Utils_eq(n, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(n) : $elm$json$Json$Decode$fail('Positive native ticket ordinal');
	},
	$author$project$UInt64$decoder);
var $author$project$NativePreviewProposalIngress$sameIntent = F2(
	function (a, b) {
		return _Utils_eq(a.aG, b.aG) && _Utils_eq(a.a5, b.a5);
	});
var $author$project$NativePreviewProposalIngress$issued = F2(
	function (raw, _v0) {
		var grant = _v0.a;
		var rows = _v0.b;
		var ticket = A2(
			$author$project$NativePreviewProposalIngress$strict,
			_List_fromArray(
				['previewProtocol', 'kind', 'binding', 'receiverEpoch', 'controlOrdinal', 'alreadyDelivered', 'wire']),
			A7(
				$elm$json$Json$Decode$map6,
				$author$project$NativePreviewProposalIngress$Ticket,
				A2($elm$json$Json$Decode$field, 'previewProtocol', $elm$json$Json$Decode$int),
				A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
				$author$project$NativePreviewRealm$domainDecoder,
				A2($elm$json$Json$Decode$field, 'controlOrdinal', $author$project$NativePreviewProposalIngress$positive),
				A2($elm$json$Json$Decode$field, 'alreadyDelivered', $elm$json$Json$Decode$bool),
				A2($elm$json$Json$Decode$field, 'wire', $elm$json$Json$Decode$string)));
		var packet = A2(
			$author$project$NativePreviewProposalIngress$strict,
			_List_fromArray(
				['previewProtocol', 'kind', 'binding', 'receiverEpoch', 'controlOrdinal', 'entries']),
			A6(
				$elm$json$Json$Decode$map5,
				$author$project$NativePreviewProposalIngress$Packet,
				A2($elm$json$Json$Decode$field, 'previewProtocol', $elm$json$Json$Decode$int),
				A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
				$author$project$NativePreviewRealm$domainDecoder,
				A2($elm$json$Json$Decode$field, 'controlOrdinal', $author$project$NativePreviewProposalIngress$positive),
				A2(
					$elm$json$Json$Decode$field,
					'entries',
					$elm$json$Json$Decode$list($author$project$NativePreviewProposalIngress$intentDecoder))));
		return A2(
			$elm$core$Maybe$andThen,
			function (fact) {
				return ((fact.aL !== 3) || ((fact.bX !== 'preview-control-ticket') || ((!A2($author$project$NativePreviewRealm$same, fact.aT, grant.aT)) || ($author$project$NativePreviewProposalIngress$bytes(fact.bF) > 4096)))) ? $elm$core$Maybe$Nothing : A2(
					$elm$core$Maybe$andThen,
					function (decoded) {
						var _v1 = decoded.bV;
						if (_v1.b && (!_v1.b.b)) {
							var intent = _v1.a;
							return ((decoded.aL === 3) && ((decoded.bX === 'preview-commands') && (A2($author$project$NativePreviewRealm$same, decoded.aT, grant.aT) && (_Utils_eq(decoded.b0, fact.b0) && A2(
								$elm$core$List$any,
								$author$project$NativePreviewProposalIngress$sameIntent(intent),
								rows))))) ? $elm$core$Maybe$Just(
								A2(
									$author$project$NativePreviewProposalIngress$Model,
									grant,
									A2(
										$elm$core$List$filter,
										function (row) {
											return !A2($author$project$NativePreviewProposalIngress$sameIntent, intent, row);
										},
										rows))) : $elm$core$Maybe$Nothing;
						} else {
							return $elm$core$Maybe$Nothing;
						}
					},
					$elm$core$Result$toMaybe(
						A2($elm$json$Json$Decode$decodeString, packet, fact.bF)));
			},
			$elm$core$Result$toMaybe(
				A2($elm$json$Json$Decode$decodeValue, ticket, raw)));
	});
var $author$project$RetainedPreviewPresenter$issued = F2(
	function (raw, prior) {
		var policy = prior.a;
		var grant = prior.b;
		var ingress = prior.c;
		var deferred = prior.d;
		return A2(
			$elm$core$Maybe$withDefault,
			prior,
			A2(
				$elm$core$Maybe$map,
				function (next) {
					return A4(
						$author$project$RetainedPreviewPresenter$Model,
						policy,
						grant,
						$elm$core$Maybe$Just(next),
						deferred);
				},
				A2(
					$elm$core$Maybe$andThen,
					$author$project$NativePreviewProposalIngress$issued(raw),
					ingress)));
	});
var $elm$json$Json$Encode$list = F2(
	function (func, entries) {
		return _Json_wrap(
			A3(
				$elm$core$List$foldl,
				_Json_addEntry(func),
				_Json_emptyArray(0),
				entries));
	});
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
var $author$project$NativePreviewProposalIngress$Proposal = F4(
	function (protocol, kind, domain, rows) {
		return {aT: domain, bX: kind, aL: protocol, bi: rows};
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
var $author$project$NativePreviewRealm$bindingValue = function (domain) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'lifetime',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(domain.aV))),
				_Utils_Tuple2(
				'session',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(domain.bk))),
				_Utils_Tuple2(
				'frontend',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(domain.a9)))
			]));
};
var $author$project$NativePreviewRealm$commands = F2(
	function (domain, entries) {
		return $elm$json$Json$Encode$object(
			_List_fromArray(
				[
					_Utils_Tuple2(
					'previewProtocol',
					$elm$json$Json$Encode$int(3)),
					_Utils_Tuple2(
					'kind',
					$elm$json$Json$Encode$string('preview-proposals')),
					_Utils_Tuple2(
					'binding',
					$author$project$NativePreviewRealm$bindingValue(domain)),
					_Utils_Tuple2(
					'receiverEpoch',
					$elm$json$Json$Encode$string(
						$author$project$UInt64$string(domain.ca))),
					_Utils_Tuple2('entries', entries)
				]));
	});
var $author$project$NativePreviewProposalIngress$encode = function (intent) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'identity',
				$elm$json$Json$Encode$string(intent.aG)),
				_Utils_Tuple2(
				'commands',
				A2(
					$elm$json$Json$Encode$list,
					$elm$core$Basics$identity,
					_List_fromArray(
						[intent.a5])))
			]));
};
var $author$project$NativePreviewProposalIngress$unique = A2(
	$elm$core$List$foldl,
	F2(
		function (intent, rows) {
			return A2(
				$elm$core$List$any,
				$author$project$NativePreviewProposalIngress$sameIntent(intent),
				rows) ? rows : _Utils_ap(
				rows,
				_List_fromArray(
					[intent]));
		}),
	_List_Nil);
var $author$project$NativePreviewProposalIngress$decode = F2(
	function (grant, raw) {
		var decoder = A2(
			$author$project$NativePreviewProposalIngress$strict,
			_List_fromArray(
				['previewProtocol', 'kind', 'binding', 'receiverEpoch', 'entries']),
			A5(
				$elm$json$Json$Decode$map4,
				$author$project$NativePreviewProposalIngress$Proposal,
				A2($elm$json$Json$Decode$field, 'previewProtocol', $elm$json$Json$Decode$int),
				A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
				$author$project$NativePreviewRealm$domainDecoder,
				A2(
					$elm$json$Json$Decode$field,
					'entries',
					$elm$json$Json$Decode$list($author$project$NativePreviewProposalIngress$intentDecoder))));
		return A2(
			$elm$core$Maybe$andThen,
			function (proposal) {
				return ((proposal.aL === 3) && ((proposal.bX === 'preview-proposals') && (A2($author$project$NativePreviewRealm$same, proposal.aT, grant.aT) && (($elm$core$List$length(proposal.bi) <= 1065) && A2(
					$elm$core$List$all,
					function (row) {
						return $author$project$NativePreviewProposalIngress$bytes(
							A2(
								$elm$json$Json$Encode$encode,
								0,
								A2(
									$author$project$NativePreviewRealm$commands,
									grant.aT,
									A2(
										$elm$json$Json$Encode$list,
										$author$project$NativePreviewProposalIngress$encode,
										_List_fromArray(
											[row]))))) <= 4096;
					},
					proposal.bi))))) ? $elm$core$Maybe$Just(
					$author$project$NativePreviewProposalIngress$unique(proposal.bi)) : $elm$core$Maybe$Nothing;
			},
			$elm$core$Result$toMaybe(
				A2($elm$json$Json$Decode$decodeValue, decoder, raw)));
	});
var $author$project$RetainedPreviewPresenter$emptyOutput = function (grant) {
	return A2(
		$elm$core$Maybe$withDefault,
		A2($elm$json$Json$Encode$list, $elm$core$Basics$identity, _List_Nil),
		A2(
			$elm$core$Maybe$map,
			function (g) {
				return A2(
					$author$project$NativePreviewRealm$commands,
					g.aT,
					A2($elm$json$Json$Encode$list, $elm$core$Basics$identity, _List_Nil));
			},
			grant));
};
var $author$project$NativePreviewProposalIngress$proposals = function (_v0) {
	var grant = _v0.a;
	var rows = _v0.b;
	return A2(
		$author$project$NativePreviewRealm$commands,
		grant.aT,
		A2($elm$json$Json$Encode$list, $author$project$NativePreviewProposalIngress$encode, rows));
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
var $author$project$NativePreviewProposalIngress$split = F2(
	function (offered, _v0) {
		var grant = _v0.a;
		var rows = _v0.b;
		var fresh = A2(
			$elm$core$List$filter,
			function (intent) {
				return !A2(
					$elm$core$List$any,
					$author$project$NativePreviewProposalIngress$sameIntent(intent),
					rows);
			},
			$author$project$NativePreviewProposalIngress$unique(offered));
		var available = A2(
			$elm$core$Basics$max,
			0,
			grant.bH - $elm$core$List$length(rows));
		return _Utils_Tuple2(
			A2(
				$author$project$NativePreviewProposalIngress$Model,
				grant,
				_Utils_ap(
					rows,
					A2($elm$core$List$take, available, fresh))),
			A2($elm$core$List$drop, available, fresh));
	});
var $author$project$RetainedPreviewPresenter$commit = F2(
	function (prior, _v0) {
		var grant = prior.b;
		var ingress = prior.c;
		var deferred = prior.d;
		var candidate = _v0.a;
		var output = _v0.b;
		if (!$elm$core$List$isEmpty(deferred)) {
			return _Utils_Tuple2(
				prior,
				$author$project$RetainedPreviewPresenter$emptyOutput(grant));
		} else {
			var _v1 = _Utils_Tuple2(grant, ingress);
			if ((!_v1.a.$) && (!_v1.b.$)) {
				var g = _v1.a.a;
				var queue = _v1.b.a;
				var _v2 = A2($author$project$NativePreviewProposalIngress$decode, g, output);
				if (_v2.$ === 1) {
					return _Utils_Tuple2(
						prior,
						$author$project$RetainedPreviewPresenter$emptyOutput(grant));
				} else {
					var intents = _v2.a;
					var _v3 = A2($author$project$NativePreviewProposalIngress$split, intents, queue);
					var retained = _v3.a;
					var waiting = _v3.b;
					return _Utils_Tuple2(
						A4(
							$author$project$RetainedPreviewPresenter$Model,
							candidate,
							grant,
							$elm$core$Maybe$Just(retained),
							waiting),
						$author$project$NativePreviewProposalIngress$proposals(retained));
				}
			} else {
				return _Utils_Tuple2(
					A4($author$project$RetainedPreviewPresenter$Model, candidate, grant, ingress, deferred),
					output);
			}
		}
	});
var $author$project$NativePreviewSource$PickerFamily = {$: 3};
var $author$project$PreviewLifecycle$Receipt = F2(
	function (a, b) {
		return {$: 14, a: a, b: b};
	});
var $author$project$PreviewLifecycle$Attach = F2(
	function (a, b) {
		return {$: 7, a: a, b: b};
	});
var $author$project$PreviewLifecycle$Cancelled = function (a) {
	return {$: 9, a: a};
};
var $author$project$PreviewLifecycle$Clock = F3(
	function (a, b, c) {
		return {$: 8, a: a, b: b, c: c};
	});
var $author$project$PreviewLifecycle$Close = {$: 1};
var $author$project$PreviewLifecycle$Exhausted = function (a) {
	return {$: 12, a: a};
};
var $author$project$PreviewLifecycle$Expired = function (a) {
	return {$: 11, a: a};
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
	return {$: 13, a: a};
};
var $author$project$PreviewLifecycle$Released = function (a) {
	return {$: 10, a: a};
};
var $author$project$PreviewLifecycle$Request = function (a) {
	return {$: 2, a: a};
};
var $author$project$PreviewLifecycle$SourceDenied = F2(
	function (a, b) {
		return {$: 6, a: a, b: b};
	});
var $author$project$PreviewLifecycle$Binding = F3(
	function (lifetime, session, frontend) {
		return {a9: frontend, aV: lifetime, bk: session};
	});
var $author$project$PreviewIdentity$Identity = $elm$core$Basics$identity;
var $author$project$PreviewIdentity$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (counter) {
		return _Utils_eq(counter, $author$project$UInt64$zero) ? $elm$json$Json$Decode$fail('Positive native identity') : $elm$json$Json$Decode$succeed(counter);
	},
	$author$project$UInt64$decoder);
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
var $author$project$PreviewLifecycle$Job = F6(
	function (binding, context, request, origin, clock, deadline) {
		return {g: binding, U: clock, b: context, O: deadline, aX: origin, a_: request};
	});
var $author$project$PreviewLifecycle$Context = F7(
	function (lifetime, incarnation, output, privacy, rendering, scene, content) {
		return {cv: content, aH: incarnation, aV: lifetime, aJ: output, aK: privacy, aM: rendering, S: scene};
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
var $author$project$PreviewLifecycle$NativeScope = F9(
	function (binding, context, observation, clock, now, present, sourceLive, locked, gpuReady) {
		return {g: binding, U: clock, b: context, ap: gpuReady, E: locked, af: now, bc: observation, av: present, az: sourceLive};
	});
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
var $author$project$PreviewLifecycle$ClientContent = 0;
var $author$project$PreviewLifecycle$ComposedFamily = 1;
var $author$project$PreviewLifecycle$LeaseHandle = $elm$core$Basics$identity;
var $author$project$PreviewLifecycle$Packet = F7(
	function (job, handle, owned, signaled, fidelity, coverage, expires) {
		return {a6: coverage, aU: expires, aF: fidelity, X: handle, e: job, be: owned, bl: signaled};
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
var $elm$core$Set$isEmpty = function (_v0) {
	var dict = _v0;
	return $elm$core$Dict$isEmpty(dict);
};
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
		return {g: binding, U: clock, b: context, O: deadline, aX: origin};
	});
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
			case 'source-denied':
				return A2(
					$author$project$PreviewLifecycle$strict,
					_List_fromArray(
						['kind', 'job', 'reason']),
					A3(
						$elm$json$Json$Decode$map2,
						$author$project$PreviewLifecycle$SourceDenied,
						A2($elm$json$Json$Decode$field, 'job', $author$project$PreviewLifecycle$jobDecoder),
						A2(
							$elm$json$Json$Decode$field,
							'reason',
							A2(
								$elm$json$Json$Decode$andThen,
								function (reason) {
									return A2(
										$elm$core$List$member,
										reason,
										_List_fromArray(
											['locked', 'source-unavailable', 'output-unavailable', 'layout-unsupported'])) ? $elm$json$Json$Decode$succeed(reason) : $elm$json$Json$Decode$fail('Typed native source denial');
								},
								$elm$json$Json$Decode$string))));
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
		case 9:
			var job = event.a;
			return $elm$core$Maybe$Just(job);
		case 10:
			var frame = event.a;
			return $elm$core$Maybe$Just(frame.e);
		case 13:
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
var $author$project$PreviewLifecycle$Model = $elm$core$Basics$identity;
var $author$project$PreviewLifecycle$Accepted = $elm$core$Basics$identity;
var $author$project$PreviewLifecycle$Acquire = function (a) {
	return {$: 0, a: a};
};
var $author$project$PreviewLifecycle$Capturing = function (a) {
	return {$: 1, a: a};
};
var $author$project$PreviewLifecycle$Connected = 0;
var $author$project$PreviewLifecycle$Idle = {$: 0};
var $author$project$PreviewLifecycle$NeedsReconciliation = 2;
var $author$project$PreviewLifecycle$SourceSuspended = 1;
var $author$project$PreviewLifecycle$acceptedPacket = function (st) {
	return A2(
		$elm$core$Maybe$map,
		function (_v0) {
			var packet = _v0;
			return packet;
		},
		st.T);
};
var $author$project$PreviewLifecycle$Cancel = function (a) {
	return {$: 1, a: a};
};
var $author$project$PreviewLifecycle$emit = F2(
	function (command, work) {
		return _Utils_update(
			work,
			{
				am: _Utils_ap(
					work.am,
					_List_fromArray(
						[command]))
			});
	});
var $author$project$PreviewLifecycle$mapState = F2(
	function (f, work) {
		return _Utils_update(
			work,
			{
				i: f(work.i)
			});
	});
var $author$project$PreviewLifecycle$cancelCurrent = function (work) {
	var _v0 = work.i.h;
	if (_v0.$ === 1) {
		var job = _v0.a;
		var cleared = A2(
			$author$project$PreviewLifecycle$mapState,
			function (st) {
				return _Utils_update(
					st,
					{h: $author$project$PreviewLifecycle$Idle});
			},
			work);
		return A2($elm$core$List$member, job, work.i.A) ? cleared : A2(
			$author$project$PreviewLifecycle$emit,
			$author$project$PreviewLifecycle$Cancel(job),
			A2(
				$author$project$PreviewLifecycle$mapState,
				function (st) {
					return _Utils_update(
						st,
						{
							A: A2($elm$core$List$cons, job, st.A)
						});
				},
				cleared));
	} else {
		return work;
	}
};
var $author$project$PreviewLifecycle$candidate = function (st) {
	var _v0 = st.h;
	if (_v0.$ === 2) {
		var frame = _v0.a;
		return $elm$core$Maybe$Just(frame);
	} else {
		return $elm$core$Maybe$Nothing;
	}
};
var $author$project$PreviewIdentity$compare = F2(
	function (_v0, _v1) {
		var a = _v0;
		var b = _v1;
		return A2($author$project$UInt64$compare, a, b);
	});
var $author$project$PreviewLifecycle$notAfter = F2(
	function (a, b) {
		return A2($author$project$PreviewIdentity$compare, a, b) !== 2;
	});
var $author$project$PreviewLifecycle$Release = function (a) {
	return {$: 2, a: a};
};
var $author$project$PreviewLifecycle$sameLease = F2(
	function (a, b) {
		return _Utils_eq(a.e, b.e) && _Utils_eq(a.X, b.X);
	});
var $author$project$PreviewLifecycle$retirePacket = F2(
	function (frame, work) {
		return A2(
			$elm$core$List$any,
			$author$project$PreviewLifecycle$sameLease(frame),
			work.i.w) ? work : A2(
			$author$project$PreviewLifecycle$emit,
			$author$project$PreviewLifecycle$Release(frame),
			A2(
				$author$project$PreviewLifecycle$mapState,
				function (st) {
					return _Utils_update(
						st,
						{
							w: A2($elm$core$List$cons, frame, st.w)
						});
				},
				work));
	});
var $author$project$PreviewLifecycle$retireAccepted = function (work) {
	var _v0 = $author$project$PreviewLifecycle$acceptedPacket(work.i);
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
						{T: $elm$core$Maybe$Nothing});
				},
				work));
	} else {
		return work;
	}
};
var $author$project$PreviewLifecycle$retireCandidate = function (work) {
	var _v0 = $author$project$PreviewLifecycle$candidate(work.i);
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
						{h: $author$project$PreviewLifecycle$Idle});
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
							{af: now})
					});
			},
			work);
		var jobTimed = function () {
			var _v2 = timed.i.h;
			if (_v2.$ === 1) {
				var job = _v2.a;
				return A2($author$project$PreviewLifecycle$notAfter, job.O, now) ? $author$project$PreviewLifecycle$cancelCurrent(timed) : timed;
			} else {
				return timed;
			}
		}();
		var candidateTimed = function () {
			var _v1 = $author$project$PreviewLifecycle$candidate(jobTimed.i);
			if (!_v1.$) {
				var frame = _v1.a;
				return (A2($author$project$PreviewLifecycle$notAfter, frame.e.O, now) || A2($author$project$PreviewLifecycle$notAfter, frame.aU, now)) ? $author$project$PreviewLifecycle$retireCandidate(jobTimed) : jobTimed;
			} else {
				return jobTimed;
			}
		}();
		var _v0 = $author$project$PreviewLifecycle$acceptedPacket(candidateTimed.i);
		if (!_v0.$) {
			var frame = _v0.a;
			return A2($author$project$PreviewLifecycle$notAfter, frame.aU, now) ? $author$project$PreviewLifecycle$retireAccepted(candidateTimed) : candidateTimed;
		} else {
			return candidateTimed;
		}
	});
var $author$project$PreviewLifecycle$before = F2(
	function (a, b) {
		return !A2($author$project$PreviewIdentity$compare, a, b);
	});
var $author$project$PreviewLifecycle$generationMatches = F2(
	function (a, b) {
		return _Utils_eq(a.aV, b.aV) && (_Utils_eq(a.aH, b.aH) && (_Utils_eq(a.aJ, b.aJ) && (_Utils_eq(a.aK, b.aK) && _Utils_eq(a.aM, b.aM))));
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
var $author$project$PreviewLifecycle$authorized = F2(
	function (st, frame) {
		return (!st.B) && (st.a.av && ((!st.a.E) && (st.a.ap && (frame.be && (_Utils_eq(frame.e.g, st.a.g) && (_Utils_eq(frame.e.U, st.a.U) && (A2($author$project$PreviewLifecycle$generationMatches, st.a.b, frame.e.b) && (A2($author$project$PreviewLifecycle$notAfter, frame.e.b.S, st.a.b.S) && (A2($author$project$PreviewLifecycle$notAfter, frame.e.b.cv, st.a.b.cv) && (A2($author$project$PreviewLifecycle$before, st.a.af, frame.aU) && (A2($elm$core$Set$member, 'client', frame.a6) && ((!frame.aF) || _Utils_eq(
			frame.a6,
			$elm$core$Set$fromList(
				_List_fromArray(
					['client', 'decoration', 'modal', 'popup'])))))))))))))));
	});
var $author$project$PreviewLifecycle$finishKnown = F2(
	function (job, work) {
		var st = work.i;
		var captureMatches = function () {
			var _v0 = st.h;
			switch (_v0.$) {
				case 1:
					var current = _v0.a;
					return _Utils_eq(current, job);
				case 2:
					var current = _v0.a;
					return _Utils_eq(current.e, job);
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
					return _Utils_eq(f.e, job);
				},
				$author$project$PreviewLifecycle$acceptedPacket(st))) || (A2($elm$core$List$member, job, st.A) || A2(
			$elm$core$List$any,
			function (f) {
				return _Utils_eq(f.e, job);
			},
			st.w)));
		return stillHeld ? work : A2(
			$author$project$PreviewLifecycle$mapState,
			function (state) {
				return _Utils_update(
					state,
					{
						D: A2(
							$elm$core$List$filter,
							$elm$core$Basics$neq(job),
							state.D)
					});
			},
			work);
	});
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
var $author$project$PreviewLifecycle$Candidate = $elm$core$Basics$identity;
var $author$project$PreviewLifecycle$WaitingFence = function (a) {
	return {$: 2, a: a};
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
var $author$project$PreviewLifecycle$heldHandle = F2(
	function (st, handle) {
		return A2(
			$elm$core$List$any,
			function (packet) {
				return _Utils_eq(packet.X, handle);
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
				st.w));
	});
var $author$project$PreviewLifecycle$offer = F2(
	function (frame, work) {
		var st = work.i;
		var matches = function () {
			var _v1 = st.h;
			if (_v1.$ === 1) {
				var job = _v1.a;
				return st.H && (_Utils_eq(job, frame.e) && (A2($author$project$PreviewLifecycle$authorized, st, frame) && (A2($author$project$PreviewLifecycle$before, st.a.af, frame.e.O) && (!A2($author$project$PreviewLifecycle$heldHandle, st, frame.X)))));
			} else {
				return false;
			}
		}();
		if (matches) {
			return frame.bl ? A2(
				$author$project$PreviewLifecycle$mapState,
				function (state) {
					return _Utils_update(
						state,
						{
							T: $elm$core$Maybe$Just(frame),
							h: $author$project$PreviewLifecycle$Idle
						});
				},
				$author$project$PreviewLifecycle$retireAccepted(work)) : A2(
				$author$project$PreviewLifecycle$mapState,
				function (state) {
					return _Utils_update(
						state,
						{
							h: $author$project$PreviewLifecycle$WaitingFence(frame)
						});
				},
				work);
		} else {
			if (A2($elm$core$List$member, frame.e, st.D) && (frame.be && (!A2($author$project$PreviewLifecycle$heldHandle, st, frame.X)))) {
				var cleanup = A2($author$project$PreviewLifecycle$retirePacket, frame, work);
				var _v0 = cleanup.i.h;
				if (_v0.$ === 1) {
					var job = _v0.a;
					return _Utils_eq(job, frame.e) ? $author$project$PreviewLifecycle$cancelCurrent(cleanup) : cleanup;
				} else {
					return cleanup;
				}
			} else {
				return work;
			}
		}
	});
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
		$author$project$PreviewLifecycle$Reconcile(work.i.a.g),
		A2(
			$author$project$PreviewLifecycle$mapState,
			function (st) {
				return _Utils_update(
					st,
					{B: 2});
			},
			$author$project$PreviewLifecycle$revoke(work)));
};
var $author$project$PreviewLifecycle$scopeCoherent = F2(
	function (previous, incoming) {
		return A2($author$project$PreviewLifecycle$notAfter, previous.b.aJ, incoming.b.aJ) && (A2($author$project$PreviewLifecycle$notAfter, previous.b.aK, incoming.b.aK) && (A2($author$project$PreviewLifecycle$notAfter, previous.b.aM, incoming.b.aM) && ((!_Utils_eq(incoming.b.aH, previous.b.aH)) || (A2($author$project$PreviewLifecycle$notAfter, previous.b.S, incoming.b.S) && (A2($author$project$PreviewLifecycle$notAfter, previous.b.cv, incoming.b.cv) && (_Utils_eq(incoming.az, previous.az) || A2($author$project$PreviewLifecycle$before, previous.b.S, incoming.b.S)))))));
	});
var $author$project$PreviewLifecycle$scopeValid = F2(
	function (previous, incoming) {
		return _Utils_eq(incoming.g, previous.g) && (_Utils_eq(incoming.U, previous.U) && (_Utils_eq(incoming.b.aV, incoming.g.aV) && (A2($author$project$PreviewLifecycle$notAfter, previous.af, incoming.af) && A2($author$project$PreviewLifecycle$before, previous.bc, incoming.bc))));
	});
var $author$project$PreviewIdentity$zeroRequest = $author$project$UInt64$zero;
var $author$project$PreviewLifecycle$updatePlain = F2(
	function (event, _v0) {
		var initial = _v0;
		var base = {am: _List_Nil, i: initial};
		var _final = function () {
			switch (event.$) {
				case 0:
					return A2(
						$author$project$PreviewLifecycle$mapState,
						function (st) {
							return _Utils_update(
								st,
								{H: true});
						},
						base);
				case 1:
					return A2(
						$author$project$PreviewLifecycle$mapState,
						function (st) {
							return _Utils_update(
								st,
								{H: false});
						},
						$author$project$PreviewLifecycle$retireCandidate(
							$author$project$PreviewLifecycle$cancelCurrent(base)));
				case 2:
					var trigger = event.a;
					if ((!initial.B) && (initial.H && (initial.a.av && (initial.a.az && ((!initial.a.E) && (initial.a.ap && (_Utils_eq(initial.h, $author$project$PreviewLifecycle$Idle) && ($elm$core$List$isEmpty(initial.A) && ($elm$core$List$isEmpty(initial.w) && (_Utils_eq(trigger.g, initial.a.g) && (_Utils_eq(trigger.b, initial.a.b) && (_Utils_eq(trigger.U, initial.a.U) && A2($author$project$PreviewLifecycle$before, initial.a.af, trigger.O))))))))))))) {
						var _v2 = initial.aI;
						if (!_v2.$) {
							var request = _v2.a;
							var job = {g: initial.a.g, U: initial.a.U, b: initial.a.b, O: trigger.O, aX: trigger.aX, a_: request};
							return A2(
								$author$project$PreviewLifecycle$emit,
								$author$project$PreviewLifecycle$Acquire(job),
								A2(
									$author$project$PreviewLifecycle$mapState,
									function (st) {
										return _Utils_update(
											st,
											{
												h: $author$project$PreviewLifecycle$Capturing(job),
												D: A2($elm$core$List$cons, job, st.D),
												aI: $author$project$PreviewIdentity$nextRequest(request)
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
						return (A2($author$project$PreviewLifecycle$sameLease, frame, incoming) && (initial.H && (A2($author$project$PreviewLifecycle$authorized, initial, frame) && A2($author$project$PreviewLifecycle$before, initial.a.af, frame.e.O)))) ? A2(
							$author$project$PreviewLifecycle$mapState,
							function (st) {
								return _Utils_update(
									st,
									{
										T: $elm$core$Maybe$Just(
											_Utils_update(
												frame,
												{bl: true})),
										h: $author$project$PreviewLifecycle$Idle
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
							var changed = ((!A2($author$project$PreviewLifecycle$generationMatches, initial.a.b, incoming.b)) || ((!incoming.av) || (incoming.E || (!incoming.ap)))) ? $author$project$PreviewLifecycle$revoke(base) : base;
							return A2(
								$author$project$PreviewLifecycle$advanceClock,
								incoming.af,
								A2(
									$author$project$PreviewLifecycle$mapState,
									function (st) {
										return _Utils_update(
											st,
											{
												B: ((st.B === 1) && (incoming.av && ((!incoming.E) && incoming.ap))) ? 0 : st.B,
												P: incoming.E,
												a: incoming
											});
									},
									changed));
						}
					}
				case 6:
					var job = event.a;
					var reason = event.b;
					var current = function () {
						var _v4 = initial.h;
						switch (_v4.$) {
							case 1:
								var active = _v4.a;
								return _Utils_eq(active, job);
							case 2:
								var frame = _v4.a;
								return _Utils_eq(frame.e, job);
							default:
								return false;
						}
					}();
					var accepted = _Utils_eq(initial.h, $author$project$PreviewLifecycle$Idle) && A2(
						$elm$core$Maybe$withDefault,
						false,
						A2(
							$elm$core$Maybe$map,
							function (frame) {
								return _Utils_eq(frame.e, job);
							},
							$author$project$PreviewLifecycle$acceptedPacket(initial)));
					return (_Utils_eq(job.g, initial.a.g) && (A2($elm$core$List$member, job, initial.D) && (current || accepted))) ? A2(
						$author$project$PreviewLifecycle$mapState,
						function (st) {
							return _Utils_update(
								st,
								{
									B: (st.B === 2) ? 2 : 1,
									P: st.P || (reason === 'locked')
								});
						},
						$author$project$PreviewLifecycle$revoke(base)) : base;
				case 7:
					var previous = event.a;
					var incoming = event.b;
					return (_Utils_eq(previous, initial.a.g) && ((!_Utils_eq(incoming.g, previous)) && _Utils_eq(incoming.b.aV, incoming.g.aV))) ? A2(
						$author$project$PreviewLifecycle$mapState,
						function (st) {
							return _Utils_update(
								st,
								{
									B: 0,
									P: incoming.E,
									aI: $author$project$PreviewIdentity$nextRequest($author$project$PreviewIdentity$zeroRequest),
									a: incoming
								});
						},
						$author$project$PreviewLifecycle$revoke(base)) : base;
				case 8:
					var binding = event.a;
					var clock = event.b;
					var now = event.c;
					return (_Utils_eq(binding, initial.a.g) && (_Utils_eq(clock, initial.a.U) && A2($author$project$PreviewLifecycle$before, initial.a.af, now))) ? A2($author$project$PreviewLifecycle$advanceClock, now, base) : base;
				case 9:
					var job = event.a;
					return A2($elm$core$List$member, job, initial.A) ? A2(
						$author$project$PreviewLifecycle$finishKnown,
						job,
						A2(
							$author$project$PreviewLifecycle$mapState,
							function (st) {
								return _Utils_update(
									st,
									{
										A: A2(
											$elm$core$List$filter,
											$elm$core$Basics$neq(job),
											st.A),
										w: A2(
											$elm$core$List$filter,
											function (f) {
												return !_Utils_eq(f.e, job);
											},
											st.w)
									});
							},
							base)) : base;
				case 10:
					var frame = event.a;
					return A2(
						$elm$core$List$any,
						$author$project$PreviewLifecycle$sameLease(frame),
						initial.w) ? A2(
						$author$project$PreviewLifecycle$finishKnown,
						frame.e,
						A2(
							$author$project$PreviewLifecycle$mapState,
							function (st) {
								return _Utils_update(
									st,
									{
										w: A2(
											$elm$core$List$filter,
											A2(
												$elm$core$Basics$composeR,
												$author$project$PreviewLifecycle$sameLease(frame),
												$elm$core$Basics$not),
											st.w)
									});
							},
							base)) : base;
				case 11:
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
				case 12:
					var binding = event.a;
					return _Utils_eq(binding, initial.a.g) ? $author$project$PreviewLifecycle$reconcile(base) : base;
				case 14:
					return base;
				default:
					var job = event.a;
					var _v5 = initial.h;
					if (_v5.$ === 1) {
						var current = _v5.a;
						return _Utils_eq(current, job) ? A2(
							$author$project$PreviewLifecycle$finishKnown,
							job,
							A2(
								$author$project$PreviewLifecycle$mapState,
								function (st) {
									return _Utils_update(
										st,
										{h: $author$project$PreviewLifecycle$Idle});
								},
								base)) : base;
					} else {
						return base;
					}
			}
		}();
		return _Utils_Tuple2(_final.i, _final.am);
	});
var $author$project$PreviewLifecycle$update = F2(
	function (event, model) {
		if (event.$ === 14) {
			var sequence = event.a;
			var terminal = event.b;
			var _v1 = $author$project$PreviewLifecycle$terminalJob(terminal);
			if (!_v1.$) {
				var job = _v1.a;
				var _v2 = model;
				var initial = _v2;
				var correlated = A2($elm$core$List$member, job, initial.D) || _Utils_eq(
					initial.ba,
					$elm$core$Maybe$Just(
						_Utils_Tuple2(job, sequence)));
				if (!correlated) {
					return _Utils_Tuple2(model, _List_Nil);
				} else {
					var _v3 = A2($author$project$PreviewLifecycle$updatePlain, terminal, model);
					var next = _v3.a;
					var commands = _v3.b;
					var _v4 = next;
					var state = _v4;
					return A2($elm$core$List$member, job, state.D) ? _Utils_Tuple2(next, commands) : _Utils_Tuple2(
						_Utils_update(
							state,
							{
								ba: $elm$core$Maybe$Just(
									_Utils_Tuple2(job, sequence))
							}),
						_Utils_ap(
							commands,
							_List_fromArray(
								[
									A2($author$project$PreviewLifecycle$Acknowledge, job, sequence)
								])));
				}
			} else {
				return A2($author$project$PreviewLifecycle$updatePlain, terminal, model);
			}
		} else {
			return A2($author$project$PreviewLifecycle$updatePlain, event, model);
		}
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
var $author$project$PreviewPresenter$closeEntry = function (entry) {
	var _v0 = entry.d;
	if (_v0.$ === 1) {
		return _Utils_Tuple2(
			_Utils_update(
				entry,
				{m: $elm$core$Maybe$Nothing, k: $elm$core$Maybe$Nothing}),
			_List_Nil);
	} else {
		var lifecycle = _v0.a;
		var _v1 = A2(
			$elm$core$Result$withDefault,
			_Utils_Tuple2(lifecycle, _List_Nil),
			A2(
				$elm$core$Result$map,
				function (event) {
					return A2($author$project$PreviewLifecycle$update, event, lifecycle);
				},
				A2(
					$elm$json$Json$Decode$decodeValue,
					$author$project$PreviewLifecycle$eventDecoder,
					$elm$json$Json$Encode$object(
						_List_fromArray(
							[
								_Utils_Tuple2(
								'kind',
								$elm$json$Json$Encode$string('close'))
							])))));
		var closed = _v1.a;
		var commands = _v1.b;
		return _Utils_Tuple2(
			_Utils_update(
				entry,
				{
					m: $elm$core$Maybe$Nothing,
					d: $elm$core$Maybe$Just(closed),
					k: $elm$core$Maybe$Nothing
				}),
			commands);
	}
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
				$author$project$PreviewIdentity$encode(binding.aV)),
				_Utils_Tuple2(
				'session',
				$author$project$PreviewIdentity$encode(binding.bk)),
				_Utils_Tuple2(
				'frontend',
				$author$project$PreviewIdentity$encode(binding.a9))
			]));
};
var $author$project$PreviewLifecycle$encodeContext = function (context) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'lifetime',
				$author$project$PreviewIdentity$encode(context.aV)),
				_Utils_Tuple2(
				'incarnation',
				$author$project$PreviewIdentity$encode(context.aH)),
				_Utils_Tuple2(
				'output',
				$author$project$PreviewIdentity$encode(context.aJ)),
				_Utils_Tuple2(
				'privacy',
				$author$project$PreviewIdentity$encode(context.aK)),
				_Utils_Tuple2(
				'rendering',
				$author$project$PreviewIdentity$encode(context.aM)),
				_Utils_Tuple2(
				'scene',
				$author$project$PreviewIdentity$encode(context.S)),
				_Utils_Tuple2(
				'content',
				$author$project$PreviewIdentity$encode(context.cv))
			]));
};
var $author$project$PreviewLifecycle$encodeJob = function (job) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'binding',
				$author$project$PreviewLifecycle$encodeBinding(job.g)),
				_Utils_Tuple2(
				'context',
				$author$project$PreviewLifecycle$encodeContext(job.b)),
				_Utils_Tuple2(
				'request',
				$author$project$PreviewIdentity$encode(job.a_)),
				_Utils_Tuple2(
				'origin',
				$author$project$PreviewIdentity$encode(job.aX)),
				_Utils_Tuple2(
				'clock',
				$author$project$PreviewIdentity$encode(job.U)),
				_Utils_Tuple2(
				'deadline',
				$author$project$PreviewIdentity$encode(job.O))
			]));
};
var $elm$json$Json$Encode$bool = _Json_wrap;
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
				$author$project$PreviewLifecycle$encodeJob(packet.e)),
				_Utils_Tuple2(
				'handle',
				$elm$json$Json$Encode$string(
					$author$project$PreviewLifecycle$handleString(packet.X))),
				_Utils_Tuple2(
				'owned',
				$elm$json$Json$Encode$bool(packet.be)),
				_Utils_Tuple2(
				'signaled',
				$elm$json$Json$Encode$bool(packet.bl)),
				_Utils_Tuple2(
				'fidelity',
				$elm$json$Json$Encode$string(
					(!packet.aF) ? 'client' : 'family')),
				_Utils_Tuple2(
				'coverage',
				A2(
					$elm$json$Json$Encode$list,
					$elm$json$Json$Encode$string,
					$elm$core$Set$toList(packet.a6))),
				_Utils_Tuple2(
				'expires',
				$author$project$PreviewIdentity$encode(packet.aU))
			]));
};
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
var $author$project$PreviewPresenter$encode = function (outputs) {
	return A2(
		$elm$json$Json$Encode$list,
		function (out) {
			return $elm$json$Json$Encode$object(
				_List_fromArray(
					[
						_Utils_Tuple2(
						'identity',
						$elm$json$Json$Encode$string(out.aG)),
						_Utils_Tuple2(
						'commands',
						$author$project$PreviewLifecycle$encodeCommands(out.V))
					]));
		},
		A2(
			$elm$core$List$filter,
			function (out) {
				return !$elm$core$List$isEmpty(out.V);
			},
			outputs));
};
var $author$project$PreviewPresenter$same = F2(
	function (stamp, snapshot) {
		return _Utils_eq(
			stamp.bf,
			$author$project$SurfaceRenderer$publication(snapshot)) && (_Utils_eq(
			stamp.bs,
			$author$project$SurfaceRenderer$lease(snapshot)) && ($author$project$SurfaceRenderer$mode(snapshot) === 'picker'));
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
var $author$project$PreviewPresenter$wrap = F2(
	function (scoped, entries) {
		var row = A3(
			$elm$json$Json$Decode$map2,
			$elm$core$Tuple$pair,
			A2($elm$json$Json$Decode$field, 'identity', $elm$json$Json$Decode$string),
			A2(
				$elm$json$Json$Decode$field,
				'commands',
				$elm$json$Json$Decode$list($elm$json$Json$Decode$value)));
		var canonical = A2(
			$elm$core$Result$withDefault,
			entries,
			A2(
				$elm$core$Result$map,
				function (rows) {
					return A2(
						$elm$json$Json$Encode$list,
						function (value) {
							return value;
						},
						A2(
							$elm$core$List$concatMap,
							function (_v0) {
								var identity = _v0.a;
								var commands = _v0.b;
								return A2(
									$elm$core$List$map,
									function (command) {
										return $elm$json$Json$Encode$object(
											_List_fromArray(
												[
													_Utils_Tuple2(
													'identity',
													$elm$json$Json$Encode$string(
														_Utils_eq(
															A2(
																$elm$json$Json$Decode$decodeValue,
																A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
																command),
															$elm$core$Result$Ok('reconcile')) ? A2(
															$elm$core$Maybe$withDefault,
															identity,
															A2(
																$elm$core$Maybe$map,
																function (grant) {
																	return 'binding:' + $author$project$NativePreviewRealm$owner(grant.aT);
																},
																scoped.r)) : identity)),
													_Utils_Tuple2(
													'commands',
													A2(
														$elm$json$Json$Encode$list,
														function (value) {
															return value;
														},
														_List_fromArray(
															[command])))
												]));
									},
									commands);
							},
							rows));
				},
				A2(
					$elm$json$Json$Decode$decodeValue,
					$elm$json$Json$Decode$list(row),
					entries)));
		return A2(
			$elm$core$Maybe$withDefault,
			entries,
			A2(
				$elm$core$Maybe$map,
				function (grant) {
					return A2($author$project$NativePreviewRealm$commands, grant.aT, canonical);
				},
				scoped.r));
	});
var $author$project$PreviewPresenter$present = F2(
	function (snapshot, _v0) {
		var entries = _v0.a;
		var catalog = _v0.b;
		var ledger = _v0.c;
		var scoped = _v0.d;
		var advance = F3(
			function (identity, entry, _v3) {
				var next = _v3.a;
				var outputs = _v3.b;
				var current = A2(
					$elm$core$Maybe$withDefault,
					false,
					A2(
						$elm$core$Maybe$map,
						function (stamp) {
							return A2(
								$elm$core$Maybe$withDefault,
								false,
								A2(
									$elm$core$Maybe$map,
									function (shown) {
										return A3($author$project$SurfaceRenderer$enabled, true, identity, shown) && (A2($author$project$PreviewPresenter$same, stamp, shown) || (_Utils_eq(
											entry.aP,
											$elm$core$Maybe$Just($author$project$NativePreviewSource$PickerFamily)) && (($author$project$SurfaceRenderer$mode(shown) === 'picker') && (_Utils_eq(
											stamp.bs,
											$author$project$SurfaceRenderer$lease(shown)) && (A2(
											$author$project$UInt64$compare,
											$author$project$SurfaceRenderer$publication(shown),
											stamp.bf) === 2)))));
									},
									snapshot));
						},
						entry.k));
				if (current || _Utils_eq(entry.k, $elm$core$Maybe$Nothing)) {
					return _Utils_Tuple2(
						A3($elm$core$Dict$insert, identity, entry, next),
						outputs);
				} else {
					var _v2 = $author$project$PreviewPresenter$closeEntry(entry);
					var closed = _v2.a;
					var commands = _v2.b;
					return _Utils_Tuple2(
						((!scoped.u) && (_Utils_eq(closed.d, $elm$core$Maybe$Nothing) && (_Utils_eq(closed.t, $elm$core$Maybe$Nothing) && _Utils_eq(closed.v, $elm$core$Maybe$Nothing)))) ? A2($elm$core$Dict$remove, identity, next) : A3($elm$core$Dict$insert, identity, closed, next),
						_Utils_ap(
							outputs,
							_List_fromArray(
								[
									{V: commands, aG: identity}
								])));
				}
			});
		var _v1 = A3(
			$elm$core$Dict$foldl,
			advance,
			_Utils_Tuple2($elm$core$Dict$empty, _List_Nil),
			entries);
		var collected = _v1.a;
		var emissions = _v1.b;
		return _Utils_Tuple2(
			A4($author$project$PreviewPresenter$Model, collected, catalog, ledger, scoped),
			A2(
				$author$project$PreviewPresenter$wrap,
				scoped,
				$author$project$PreviewPresenter$encode(emissions)));
	});
var $author$project$RetainedPreviewPresenter$present = F2(
	function (snapshot, prior) {
		var policy = prior.a;
		return A2(
			$author$project$RetainedPreviewPresenter$commit,
			prior,
			A2($author$project$PreviewPresenter$present, snapshot, policy));
	});
var $author$project$Popup$previewCommands = _Platform_outgoingPort('previewCommands', $elm$core$Basics$identity);
var $author$project$PreviewLifecycle$retire = function (_v0) {
	var initial = _v0;
	var _final = A2(
		$author$project$PreviewLifecycle$mapState,
		function (st) {
			return _Utils_update(
				st,
				{H: false});
		},
		$author$project$PreviewLifecycle$revoke(
			{am: _List_Nil, i: initial}));
	return _Utils_Tuple2(_final.i, _final.am);
};
var $author$project$PreviewPresenter$detachEntry = function (entry) {
	var _v0 = entry.d;
	if (_v0.$ === 1) {
		return _Utils_Tuple2(
			_Utils_update(
				entry,
				{m: $elm$core$Maybe$Nothing, k: $elm$core$Maybe$Nothing}),
			_List_Nil);
	} else {
		var lifecycle = _v0.a;
		var _v1 = $author$project$PreviewLifecycle$retire(lifecycle);
		var next = _v1.a;
		var emitted = _v1.b;
		return _Utils_Tuple2(
			_Utils_update(
				entry,
				{
					m: $elm$core$Maybe$Nothing,
					d: $elm$core$Maybe$Just(next),
					k: $elm$core$Maybe$Nothing
				}),
			emitted);
	}
};
var $author$project$PreviewPresenter$quarantineOwned = function (prior) {
	var entries = prior.a;
	var catalog = prior.b;
	var ledger = prior.c;
	var scoped = prior.d;
	if (scoped.u) {
		return _Utils_Tuple2(
			prior,
			$author$project$PreviewPresenter$encode(_List_Nil));
	} else {
		var step = F3(
			function (identity, entry, _v2) {
				var next = _v2.a;
				var emitted = _v2.b;
				var _v1 = $author$project$PreviewPresenter$detachEntry(entry);
				var closed = _v1.a;
				var commands = _v1.b;
				return _Utils_Tuple2(
					A3($elm$core$Dict$insert, identity, closed, next),
					_Utils_ap(
						emitted,
						_List_fromArray(
							[
								{V: commands, aG: identity}
							])));
			});
		var _v0 = A3(
			$elm$core$Dict$foldl,
			step,
			_Utils_Tuple2($elm$core$Dict$empty, _List_Nil),
			entries);
		var retained = _v0.a;
		var cleanup = _v0.b;
		return _Utils_Tuple2(
			A4(
				$author$project$PreviewPresenter$Model,
				retained,
				catalog,
				ledger,
				_Utils_update(
					scoped,
					{u: true})),
			$author$project$PreviewPresenter$encode(cleanup));
	}
};
var $author$project$PreviewPresenter$quarantineRealm = F2(
	function (domain, prior) {
		var scoped = prior.d;
		if (scoped.N || (scoped.u || (!A2(
			$elm$core$Maybe$withDefault,
			false,
			A2(
				$elm$core$Maybe$map,
				function (grant) {
					return A2($author$project$NativePreviewRealm$same, grant.aT, domain);
				},
				scoped.r))))) {
			return _Utils_Tuple2(
				prior,
				A2(
					$author$project$PreviewPresenter$wrap,
					scoped,
					$author$project$PreviewPresenter$encode(_List_Nil)));
		} else {
			var original = $elm$json$Json$Encode$object(
				_List_fromArray(
					[
						_Utils_Tuple2(
						'identity',
						$elm$json$Json$Encode$string(
							'binding:' + $author$project$NativePreviewRealm$owner(domain))),
						_Utils_Tuple2(
						'commands',
						A2(
							$elm$json$Json$Encode$list,
							$elm$core$Basics$identity,
							_List_fromArray(
								[
									$elm$json$Json$Encode$object(
									_List_fromArray(
										[
											_Utils_Tuple2(
											'kind',
											$elm$json$Json$Encode$string('reconcile')),
											_Utils_Tuple2(
											'binding',
											$author$project$NativePreviewRealm$bindingValue(domain))
										]))
								])))
					]));
			var _v0 = $author$project$PreviewPresenter$quarantineOwned(prior);
			var next = _v0.a;
			var cleanup = _v0.b;
			var retained = A2(
				$elm$core$Result$withDefault,
				_List_Nil,
				A2(
					$elm$json$Json$Decode$decodeValue,
					$elm$json$Json$Decode$list($elm$json$Json$Decode$value),
					cleanup));
			return _Utils_Tuple2(
				next,
				A2(
					$author$project$PreviewPresenter$wrap,
					scoped,
					A2(
						$elm$json$Json$Encode$list,
						$elm$core$Basics$identity,
						A2($elm$core$List$cons, original, retained))));
		}
	});
var $author$project$RetainedPreviewPresenter$quarantineRealm = F2(
	function (domain, prior) {
		var policy = prior.a;
		var grant = prior.b;
		var ingress = prior.c;
		var deferred = prior.d;
		if ($elm$core$List$isEmpty(deferred)) {
			return A2(
				$author$project$RetainedPreviewPresenter$commit,
				prior,
				A2($author$project$PreviewPresenter$quarantineRealm, domain, policy));
		} else {
			var _v0 = _Utils_Tuple2(grant, ingress);
			if ((!_v0.a.$) && (!_v0.b.$)) {
				var g = _v0.a.a;
				var queue = _v0.b.a;
				if (!A2($author$project$NativePreviewRealm$same, g.aT, domain)) {
					return _Utils_Tuple2(
						prior,
						$author$project$RetainedPreviewPresenter$emptyOutput(grant));
				} else {
					var _v1 = A2($author$project$PreviewPresenter$quarantineRealm, domain, policy);
					var candidate = _v1.a;
					var output = _v1.b;
					var _v2 = A2($author$project$NativePreviewProposalIngress$decode, g, output);
					if ((!_v2.$) && _v2.a.b) {
						var _v3 = _v2.a;
						var intents = A2(
							$elm$core$Maybe$withDefault,
							_List_Nil,
							A2($author$project$NativePreviewProposalIngress$decode, g, output));
						var _v4 = A2(
							$author$project$NativePreviewProposalIngress$split,
							_Utils_ap(deferred, intents),
							queue);
						var retained = _v4.a;
						var waiting = _v4.b;
						return _Utils_Tuple2(
							A4(
								$author$project$RetainedPreviewPresenter$Model,
								candidate,
								grant,
								$elm$core$Maybe$Just(retained),
								waiting),
							$author$project$NativePreviewProposalIngress$proposals(retained));
					} else {
						return _Utils_Tuple2(
							prior,
							$author$project$RetainedPreviewPresenter$emptyOutput(grant));
					}
				}
			} else {
				return _Utils_Tuple2(
					prior,
					$author$project$RetainedPreviewPresenter$emptyOutput(grant));
			}
		}
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
var $author$project$SurfaceRenderer$queryValue = function (current) {
	var snapshot = current;
	return A2(
		$elm$core$Maybe$map,
		function ($) {
			return $.bY;
		},
		$elm$core$List$head(
			A2(
				$elm$core$List$filter,
				function (item) {
					return _Utils_eq(
						item.aG,
						$author$project$SurfaceRenderer$fieldIdentity(current));
				},
				snapshot.n)));
};
var $elm$json$Json$Decode$null = _Json_decodeNull;
var $elm$json$Json$Decode$nullable = function (decoder) {
	return $elm$json$Json$Decode$oneOf(
		_List_fromArray(
			[
				$elm$json$Json$Decode$null($elm$core$Maybe$Nothing),
				A2($elm$json$Json$Decode$map, $elm$core$Maybe$Just, decoder)
			]));
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
var $author$project$PreviewLifecycle$encodeScope = function (scope) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'binding',
				$author$project$PreviewLifecycle$encodeBinding(scope.g)),
				_Utils_Tuple2(
				'context',
				$author$project$PreviewLifecycle$encodeContext(scope.b)),
				_Utils_Tuple2(
				'observation',
				$author$project$PreviewIdentity$encode(scope.bc)),
				_Utils_Tuple2(
				'clock',
				$author$project$PreviewIdentity$encode(scope.U)),
				_Utils_Tuple2(
				'now',
				$author$project$PreviewIdentity$encode(scope.af)),
				_Utils_Tuple2(
				'present',
				$elm$json$Json$Encode$bool(scope.av)),
				_Utils_Tuple2(
				'sourceLive',
				$elm$json$Json$Encode$bool(scope.az)),
				_Utils_Tuple2(
				'locked',
				$elm$json$Json$Encode$bool(scope.E)),
				_Utils_Tuple2(
				'gpuReady',
				$elm$json$Json$Encode$bool(scope.ap))
			]));
};
var $elm$json$Json$Encode$null = _Json_encodeNull;
var $author$project$PreviewLifecycle$Historical = function (a) {
	return {$: 1, a: a};
};
var $author$project$PreviewLifecycle$Live = function (a) {
	return {$: 0, a: a};
};
var $author$project$PreviewLifecycle$Loading = {$: 2};
var $author$project$PreviewLifecycle$Unavailable = {$: 3};
var $author$project$PreviewLifecycle$loadingStatus = function (st) {
	return (st.H && (!_Utils_eq(st.h, $author$project$PreviewLifecycle$Idle))) ? $author$project$PreviewLifecycle$Loading : $author$project$PreviewLifecycle$Unavailable;
};
var $author$project$PreviewLifecycle$status = function (st) {
	var _v0 = st.T;
	if (!_v0.$) {
		var lease = _v0.a;
		var frame = lease;
		return (st.H && A2($author$project$PreviewLifecycle$authorized, st, frame)) ? ((st.a.az && (_Utils_eq(frame.e.b.S, st.a.b.S) && _Utils_eq(frame.e.b.cv, st.a.b.cv))) ? $author$project$PreviewLifecycle$Live(lease) : $author$project$PreviewLifecycle$Historical(lease)) : $author$project$PreviewLifecycle$loadingStatus(st);
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
		var _v1 = st.h;
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
				$elm$json$Json$Encode$bool(st.H)),
				_Utils_Tuple2(
				'ready',
				$elm$json$Json$Encode$bool(!st.B)),
				_Utils_Tuple2(
				'nextRequest',
				A2(maybe, $author$project$PreviewIdentity$encode, st.aI)),
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
				A2($elm$json$Json$Encode$list, $author$project$PreviewLifecycle$encodeJob, st.D)),
				_Utils_Tuple2(
				'cancelling',
				A2($elm$json$Json$Encode$list, $author$project$PreviewLifecycle$encodeJob, st.A)),
				_Utils_Tuple2(
				'retiring',
				A2($elm$json$Json$Encode$list, $author$project$PreviewLifecycle$encodePacket, st.w)),
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
							return $.X;
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
var $author$project$PreviewPresenter$floorMatches = F2(
	function (entry, seed) {
		var _v0 = entry.d;
		if (_v0.$ === 1) {
			return _Utils_eq(seed.cJ, $author$project$UInt64$zero);
		} else {
			var lifecycle = _v0.a;
			return A2(
				$elm$core$Result$withDefault,
				false,
				A2(
					$elm$core$Result$map,
					function (next) {
						return _Utils_eq(
							next,
							$author$project$UInt64$next(seed.cJ));
					},
					A2(
						$elm$json$Json$Decode$decodeValue,
						A2(
							$elm$json$Json$Decode$field,
							'nextRequest',
							$elm$json$Json$Decode$nullable($author$project$UInt64$decoder)),
						$author$project$PreviewLifecycle$observe(lifecycle))));
		}
	});
var $author$project$NativePreviewDetachment$ready = function (seed) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'kind',
				$elm$json$Json$Encode$string('detach-ready')),
				_Utils_Tuple2(
				'binding',
				$author$project$NativePreviewRealm$bindingValue(seed.aT)),
				_Utils_Tuple2(
				'receiverEpoch',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(seed.aT.ca))),
				_Utils_Tuple2(
				'subject',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(seed.aA))),
				_Utils_Tuple2(
				'entry',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(seed.bN))),
				_Utils_Tuple2(
				'entryIssuedThrough',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(seed.a8))),
				_Utils_Tuple2(
				'requestFloor',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(seed.cJ)))
			]));
};
var $author$project$NativeActorRetirement$bindingValue = function (value) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'lifetime',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(value.aV))),
				_Utils_Tuple2(
				'session',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(value.bk))),
				_Utils_Tuple2(
				'frontend',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(value.a9)))
			]));
};
var $author$project$NativeActorRetirement$readyCommand = function (value) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'kind',
				$elm$json$Json$Encode$string('retire-ready')),
				_Utils_Tuple2(
				'binding',
				$author$project$NativeActorRetirement$bindingValue(value)),
				_Utils_Tuple2(
				'subject',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(value.aA))),
				_Utils_Tuple2(
				'observationRequest',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(value.a_))),
				_Utils_Tuple2(
				'observationSequence',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(value.ay)))
			]));
};
var $author$project$NativePreviewDetachment$acknowledgment = function (delivery) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'kind',
				$elm$json$Json$Encode$string('detach-delivery-ack')),
				_Utils_Tuple2(
				'binding',
				$author$project$NativePreviewRealm$bindingValue(delivery.bj.aT)),
				_Utils_Tuple2(
				'receiverEpoch',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(delivery.bj.aT.ca))),
				_Utils_Tuple2(
				'deliveryOrdinal',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(delivery.b0)))
			]));
};
var $author$project$NativeActorRetirement$owner = function (value) {
	return A2(
		$elm$core$String$join,
		':',
		A2(
			$elm$core$List$map,
			$author$project$UInt64$string,
			_List_fromArray(
				[value.aV, value.bk, value.a9])));
};
var $author$project$NativeActorRetirement$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (!_Utils_eq(value, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Positive native retirement identity');
	},
	$author$project$UInt64$decoder);
var $author$project$NativeActorRetirement$admittedAfter = F3(
	function (ledger, binding, raw) {
		var _v0 = ledger.aN;
		if (_v0.$ === 1) {
			return true;
		} else {
			var _final = _v0.a;
			var _v1 = A2(
				$elm$json$Json$Decode$decodeValue,
				A3(
					$elm$json$Json$Decode$map2,
					$elm$core$Tuple$pair,
					A2($elm$json$Json$Decode$field, 'clock', $author$project$NativeActorRetirement$positive),
					A2($elm$json$Json$Decode$field, 'now', $author$project$NativeActorRetirement$positive)),
				raw);
			if (!_v1.$) {
				var _v2 = _v1.a;
				var clock = _v2.a;
				var now = _v2.b;
				return _Utils_eq(
					binding,
					$author$project$NativeActorRetirement$owner(_final.j)) && (_Utils_eq(clock, _final.j.U) && (A2($author$project$UInt64$compare, now, _final.j.af) === 2));
			} else {
				return false;
			}
		}
	});
var $author$project$PreviewPresenter$advanceFloor = F2(
	function (old, incoming) {
		var _v0 = _Utils_Tuple2(old, incoming);
		if (!_v0.b.$) {
			if (!_v0.a.$) {
				var previous = _v0.a.a;
				var next = _v0.b.a;
				return $elm$core$Maybe$Just(
					(A2($author$project$UInt64$compare, next, previous) === 2) ? next : previous);
			} else {
				var next = _v0.b.a;
				return $elm$core$Maybe$Just(next);
			}
		} else {
			return old;
		}
	});
var $elm$json$Json$Decode$at = F2(
	function (fields, decoder) {
		return A3($elm$core$List$foldr, $elm$json$Json$Decode$field, decoder, fields);
	});
var $author$project$PreviewPresenter$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (!_Utils_eq(value, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Positive preview presentation identity');
	},
	$author$project$UInt64$decoder);
var $author$project$PreviewPresenter$strict = F2(
	function (fields, decoder) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? decoder : $elm$json$Json$Decode$fail('Preview presenter fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$PreviewPresenter$binding = A2(
	$author$project$PreviewPresenter$strict,
	_List_fromArray(
		['lifetime', 'session', 'frontend']),
	A4(
		$elm$json$Json$Decode$map3,
		F3(
			function (a, b, c) {
				return A2(
					$elm$core$String$join,
					':',
					A2(
						$elm$core$List$map,
						$author$project$UInt64$string,
						_List_fromArray(
							[a, b, c])));
			}),
		A2($elm$json$Json$Decode$field, 'lifetime', $author$project$PreviewPresenter$positive),
		A2($elm$json$Json$Decode$field, 'session', $author$project$PreviewPresenter$positive),
		A2($elm$json$Json$Decode$field, 'frontend', $author$project$PreviewPresenter$positive)));
var $author$project$NativeActorRetirement$chronology = F2(
	function (incoming, previous) {
		var _v0 = A2($author$project$UInt64$compare, incoming.af, previous.af);
		if (_v0 === 1) {
			return A2($author$project$UInt64$compare, incoming.ay, previous.ay);
		} else {
			var order = _v0;
			return order;
		}
	});
var $author$project$NativeActorRetirement$coherentFrontier = F2(
	function (ledger, fact) {
		var _v0 = ledger.aN;
		if (_v0.$ === 1) {
			return true;
		} else {
			var previous = _v0.a;
			var subjects = A2($author$project$UInt64$compare, fact.j.ar, previous.j.ar);
			var order = A2($author$project$NativeActorRetirement$chronology, fact.j, previous.j);
			var entries = A2($author$project$UInt64$compare, fact.a8, previous.a8);
			return _Utils_eq(
				$author$project$NativeActorRetirement$owner(fact.j),
				$author$project$NativeActorRetirement$owner(previous.j)) && (_Utils_eq(fact.j.U, previous.j.U) && ((!order) ? ((entries !== 2) && (subjects !== 2)) : ((!(!entries)) && (!(!subjects)))));
		}
	});
var $author$project$NativeActorRetirement$fresh = F2(
	function (previous, incoming) {
		return A2(
			$elm$core$Maybe$withDefault,
			true,
			A2(
				$elm$core$Maybe$map,
				function (old) {
					return _Utils_eq(
						$author$project$NativeActorRetirement$owner(incoming),
						$author$project$NativeActorRetirement$owner(old)) && (_Utils_eq(incoming.U, old.U) && ((A2($author$project$UInt64$compare, incoming.a_, old.a_) === 2) && ((A2($author$project$UInt64$compare, incoming.ay, old.ay) === 2) && ((!(!A2($author$project$UInt64$compare, incoming.af, old.af))) && (!(!A2($author$project$UInt64$compare, incoming.ar, old.ar)))))));
				},
				previous));
	});
var $author$project$NativeActorRetirement$remember = F2(
	function (ledger, observation) {
		return A2($author$project$NativeActorRetirement$fresh, ledger.bd, observation) ? _Utils_update(
			ledger,
			{
				bd: $elm$core$Maybe$Just(observation)
			}) : ledger;
	});
var $author$project$NativeActorRetirement$confirm = F2(
	function (ledger, fact) {
		var updated = A2($author$project$NativeActorRetirement$remember, ledger, fact.j);
		var newest = A2(
			$elm$core$Maybe$withDefault,
			true,
			A2(
				$elm$core$Maybe$map,
				function (previous) {
					return !(!A2($author$project$NativeActorRetirement$chronology, fact.j, previous.j));
				},
				ledger.aN));
		return newest ? _Utils_update(
			updated,
			{
				aN: $elm$core$Maybe$Just(fact)
			}) : updated;
	});
var $author$project$NativeActorRetirement$deliveryAcknowledgment = function (delivery) {
	return $elm$json$Json$Encode$object(
		_List_fromArray(
			[
				_Utils_Tuple2(
				'kind',
				$elm$json$Json$Encode$string('retire-delivery-ack')),
				_Utils_Tuple2(
				'binding',
				$author$project$NativeActorRetirement$bindingValue(delivery.bP.j)),
				_Utils_Tuple2(
				'deliveryOrdinal',
				$elm$json$Json$Encode$string(
					$author$project$UInt64$string(delivery.b0)))
			]));
};
var $author$project$PreviewPresenter$eventOwns = F2(
	function (identity, wire) {
		var _v0 = A2(
			$elm$json$Json$Decode$decodeValue,
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			wire);
		_v0$2:
		while (true) {
			if (!_v0.$) {
				switch (_v0.a) {
					case 'observe':
						return A2(
							$elm$core$Result$withDefault,
							false,
							A2(
								$elm$core$Result$map,
								function (incarnation) {
									return _Utils_eq(
										identity,
										'family:' + $author$project$UInt64$string(incarnation));
								},
								A2(
									$elm$json$Json$Decode$decodeValue,
									A2(
										$elm$json$Json$Decode$at,
										_List_fromArray(
											['scope', 'context', 'incarnation']),
										$author$project$PreviewPresenter$positive),
									wire)));
					case 'attach':
						return A2(
							$elm$core$Result$withDefault,
							false,
							A2(
								$elm$core$Result$map,
								function (incarnation) {
									return _Utils_eq(
										identity,
										'family:' + $author$project$UInt64$string(incarnation));
								},
								A2(
									$elm$json$Json$Decode$decodeValue,
									A2(
										$elm$json$Json$Decode$at,
										_List_fromArray(
											['scope', 'context', 'incarnation']),
										$author$project$PreviewPresenter$positive),
									wire)));
					default:
						break _v0$2;
				}
			} else {
				break _v0$2;
			}
		}
		return true;
	});
var $author$project$PreviewPresenter$familyFrameOwns = F2(
	function (sourceKind, wire) {
		if (!function () {
			_v0$3:
			while (true) {
				if (!sourceKind.$) {
					switch (sourceKind.a.$) {
						case 2:
							var _v1 = sourceKind.a;
							return true;
						case 3:
							var _v2 = sourceKind.a;
							return true;
						case 4:
							return true;
						default:
							break _v0$3;
					}
				} else {
					break _v0$3;
				}
			}
			return false;
		}()) {
			return true;
		} else {
			var shape = A3(
				$elm$json$Json$Decode$map2,
				F2(
					function (fidelity, coverage) {
						return (fidelity === 'family') && _Utils_eq(
							$elm$core$List$sort(coverage),
							_List_fromArray(
								['client', 'decoration', 'modal', 'popup']));
					}),
				A2($elm$json$Json$Decode$field, 'fidelity', $elm$json$Json$Decode$string),
				A2(
					$elm$json$Json$Decode$field,
					'coverage',
					$elm$json$Json$Decode$list($elm$json$Json$Decode$string)));
			var admit = function (path) {
				return A2(
					$elm$core$Result$withDefault,
					false,
					A2(
						$elm$json$Json$Decode$decodeValue,
						A2($elm$json$Json$Decode$at, path, shape),
						wire));
			};
			var _v3 = A2(
				$elm$json$Json$Decode$decodeValue,
				A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
				wire);
			_v3$4:
			while (true) {
				if (!_v3.$) {
					switch (_v3.a) {
						case 'offer':
							return admit(
								_List_fromArray(
									['frame']));
						case 'fence':
							return admit(
								_List_fromArray(
									['frame']));
						case 'expired':
							return admit(
								_List_fromArray(
									['frame']));
						case 'receipt':
							var _v4 = A2(
								$elm$json$Json$Decode$decodeValue,
								A2(
									$elm$json$Json$Decode$at,
									_List_fromArray(
										['event', 'kind']),
									$elm$json$Json$Decode$string),
								wire);
							if ((!_v4.$) && (_v4.a === 'released')) {
								return admit(
									_List_fromArray(
										['event', 'frame']));
							} else {
								return true;
							}
						default:
							break _v3$4;
					}
				} else {
					break _v3$4;
				}
			}
			return true;
		}
	});
var $author$project$PreviewLifecycle$idle = function (_v0) {
	var st = _v0;
	return (!st.B) && (st.a.av && (st.a.az && ((!st.a.E) && (st.a.ap && ((!st.P) && (_Utils_eq(st.h, $author$project$PreviewLifecycle$Idle) && (_Utils_eq(st.T, $elm$core$Maybe$Nothing) && ($elm$core$List$isEmpty(st.D) && ($elm$core$List$isEmpty(st.A) && $elm$core$List$isEmpty(st.w))))))))));
};
var $author$project$PreviewLifecycle$init = function (_v0) {
	var scope = _v0;
	return {
		T: $elm$core$Maybe$Nothing,
		A: _List_Nil,
		h: $author$project$PreviewLifecycle$Idle,
		B: 0,
		H: false,
		D: _List_Nil,
		ba: $elm$core$Maybe$Nothing,
		P: scope.E,
		aI: $author$project$PreviewIdentity$nextRequest($author$project$PreviewIdentity$zeroRequest),
		w: _List_Nil,
		a: scope
	};
};
var $author$project$PreviewPresenter$Catalog = F3(
	function (a, b, c) {
		return {$: 3, a: a, b: b, c: c};
	});
var $author$project$PreviewPresenter$DetachSeed = function (a) {
	return {$: 9, a: a};
};
var $author$project$PreviewPresenter$Detached = function (a) {
	return {$: 10, a: a};
};
var $author$project$PreviewPresenter$Event = F3(
	function (a, b, c) {
		return {$: 2, a: a, b: b, c: c};
	});
var $author$project$PreviewPresenter$Feedback = F2(
	function (a, b) {
		return {$: 4, a: a, b: b};
	});
var $author$project$PreviewPresenter$Metadata = F8(
	function (a, b, c, d, e, f, g, h) {
		return {$: 1, a: a, b: b, c: c, d: d, e: e, f: f, g: g, h: h};
	});
var $author$project$PreviewPresenter$Retired = function (a) {
	return {$: 6, a: a};
};
var $author$project$PreviewPresenter$Retirement = function (a) {
	return {$: 5, a: a};
};
var $author$project$PreviewPresenter$RetirementChannel = function (a) {
	return {$: 7, a: a};
};
var $author$project$PreviewPresenter$RetirementDelivery = function (a) {
	return {$: 8, a: a};
};
var $author$project$PreviewPresenter$Seed = function (a) {
	return function (b) {
		return function (c) {
			return function (d) {
				return function (e) {
					return function (f) {
						return function (g) {
							return function (h) {
								return function (i) {
									return function (j) {
										return {$: 0, a: a, b: b, c: c, d: d, e: e, f: f, g: g, h: h, i: i, j: j};
									};
								};
							};
						};
					};
				};
			};
		};
	};
};
var $author$project$PreviewPresenter$Stamp = F2(
	function (publication, lease) {
		return {bs: lease, bf: publication};
	});
var $author$project$NativeActorRetirement$Fact = F4(
	function (_native, entry, entryIssuedThrough, requestFloor) {
		return {bN: entry, a8: entryIssuedThrough, j: _native, cJ: requestFloor};
	});
var $author$project$NativeActorRetirement$strict = F2(
	function (fields, decoder) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? decoder : $elm$json$Json$Decode$fail('Exact native actor retirement fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$NativeActorRetirement$nativeDecoder = A3(
	$elm$json$Json$Decode$map2,
	F2(
		function (_v0, construct) {
			var lifetime = _v0.a;
			var session = _v0.b;
			var frontend = _v0.c;
			return A3(construct, lifetime, session, frontend);
		}),
	A2(
		$elm$json$Json$Decode$field,
		'binding',
		A2(
			$author$project$NativeActorRetirement$strict,
			_List_fromArray(
				['lifetime', 'session', 'frontend']),
			A4(
				$elm$json$Json$Decode$map3,
				F3(
					function (a, b, c) {
						return _Utils_Tuple3(a, b, c);
					}),
				A2($elm$json$Json$Decode$field, 'lifetime', $author$project$NativeActorRetirement$positive),
				A2($elm$json$Json$Decode$field, 'session', $author$project$NativeActorRetirement$positive),
				A2($elm$json$Json$Decode$field, 'frontend', $author$project$NativeActorRetirement$positive)))),
	A7(
		$elm$json$Json$Decode$map6,
		F6(
			function (subject, request, sequence, clock, now, issuedThrough) {
				return F3(
					function (lifetime, session, frontend) {
						return {U: clock, a9: frontend, ar: issuedThrough, aV: lifetime, af: now, a_: request, ay: sequence, bk: session, aA: subject};
					});
			}),
		A2($elm$json$Json$Decode$field, 'subject', $author$project$NativeActorRetirement$positive),
		A2($elm$json$Json$Decode$field, 'request', $author$project$NativeActorRetirement$positive),
		A2($elm$json$Json$Decode$field, 'sequence', $author$project$NativeActorRetirement$positive),
		A2($elm$json$Json$Decode$field, 'clock', $author$project$NativeActorRetirement$positive),
		A2($elm$json$Json$Decode$field, 'now', $author$project$NativeActorRetirement$positive),
		A2($elm$json$Json$Decode$field, 'issuedThrough', $author$project$UInt64$decoder)));
var $author$project$NativeActorRetirement$validate = function (value) {
	return _Utils_eq(value.U, value.aV) && (A2($author$project$UInt64$compare, value.aA, value.ar) !== 2);
};
var $author$project$NativeActorRetirement$actorDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (_v0) {
		var fact = _v0.a;
		var _v1 = _v0.b;
		var identity = _v1.a;
		var kind = _v1.b;
		return ((kind === 'native-actor-retired') && ($author$project$NativeActorRetirement$validate(fact.j) && (_Utils_eq(
			identity,
			'family:' + $author$project$UInt64$string(fact.j.aA)) && (A2($author$project$UInt64$compare, fact.bN, fact.a8) !== 2)))) ? $elm$json$Json$Decode$succeed(fact) : $elm$json$Json$Decode$fail('Exact native aggregate retirement fact');
	},
	A2(
		$author$project$NativeActorRetirement$strict,
		_List_fromArray(
			['kind', 'identity', 'binding', 'subject', 'entry', 'entryIssuedThrough', 'requestFloor', 'request', 'sequence', 'clock', 'now', 'issuedThrough']),
		A7(
			$elm$json$Json$Decode$map6,
			F6(
				function (_native, entry, frontier, floor, identity, kind) {
					return _Utils_Tuple2(
						A4($author$project$NativeActorRetirement$Fact, _native, entry, frontier, floor),
						_Utils_Tuple2(identity, kind));
				}),
			$author$project$NativeActorRetirement$nativeDecoder,
			A2($elm$json$Json$Decode$field, 'entry', $author$project$NativeActorRetirement$positive),
			A2($elm$json$Json$Decode$field, 'entryIssuedThrough', $author$project$NativeActorRetirement$positive),
			A2($elm$json$Json$Decode$field, 'requestFloor', $author$project$UInt64$decoder),
			A2($elm$json$Json$Decode$field, 'identity', $elm$json$Json$Decode$string),
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string))));
var $author$project$PreviewPresenter$bounded = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		var size = A3(
			$elm$core$String$foldl,
			F2(
				function (c, bytes) {
					return bytes + (($elm$core$Char$toCode(c) < 128) ? 1 : (($elm$core$Char$toCode(c) < 2048) ? 2 : (($elm$core$Char$toCode(c) < 65536) ? 3 : 4)));
				}),
			0,
			value);
		var control = function (c) {
			return ($elm$core$Char$toCode(c) < 32) || (($elm$core$Char$toCode(c) >= 127) && ($elm$core$Char$toCode(c) <= 159));
		};
		return ((size <= 1024) && (!A2($elm$core$String$any, control, value))) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Preview label');
	},
	$elm$json$Json$Decode$string);
var $author$project$NativeActorRetirement$channelDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (_v0) {
		var kind = _v0.a;
		var binding = _v0.b;
		return (kind === 'native-actor-retirement-channel') ? $elm$json$Json$Decode$succeed(binding) : $elm$json$Json$Decode$fail('Retained native retirement channel');
	},
	A2(
		$author$project$NativeActorRetirement$strict,
		_List_fromArray(
			['kind', 'binding']),
		A3(
			$elm$json$Json$Decode$map2,
			$elm$core$Tuple$pair,
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			A2(
				$elm$json$Json$Decode$field,
				'binding',
				A2(
					$author$project$NativeActorRetirement$strict,
					_List_fromArray(
						['lifetime', 'session', 'frontend']),
					A4(
						$elm$json$Json$Decode$map3,
						F3(
							function (a, b, c) {
								return A2(
									$elm$core$String$join,
									':',
									A2(
										$elm$core$List$map,
										$author$project$UInt64$string,
										_List_fromArray(
											[a, b, c])));
							}),
						A2($elm$json$Json$Decode$field, 'lifetime', $author$project$NativeActorRetirement$positive),
						A2($elm$json$Json$Decode$field, 'session', $author$project$NativeActorRetirement$positive),
						A2($elm$json$Json$Decode$field, 'frontend', $author$project$NativeActorRetirement$positive)))))));
var $author$project$NativePreviewSource$GeneratedBackdropFamily = function (a) {
	return {$: 4, a: a};
};
var $author$project$NativePreviewSource$Observation = $elm$core$Basics$identity;
var $author$project$NativePreviewSource$StyleCroppedFamily = {$: 2};
var $author$project$NativeFamilyPreviewSource$GeneratedOpaque = function (a) {
	return {$: 2, a: a};
};
var $author$project$NativeFamilyPreviewSource$PickerTransparent = {$: 1};
var $author$project$NativeFamilyPreviewSource$Transparent = {$: 0};
var $author$project$NativeFamilyPreviewSource$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (!_Utils_eq(value, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Native family positive identity');
	},
	$author$project$UInt64$decoder);
var $author$project$NativeFamilyPreviewSource$strict = F2(
	function (fields, decode) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? decode : $elm$json$Json$Decode$fail('Native family fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$NativeFamilyPreviewSource$backdropDecoder = A2(
	$author$project$NativeFamilyPreviewSource$strict,
	_List_fromArray(
		['kind', 'colorARGB']),
	A2(
		$elm$json$Json$Decode$andThen,
		function (_v0) {
			var kind = _v0.a;
			var color = _v0.b;
			var value = $author$project$UInt64$string(color);
			return ((kind === 'native-opaque-generated-color') && (($elm$core$String$length(value) === 10) && ((value >= '4278190080') && (value <= '4294967295')))) ? $elm$json$Json$Decode$succeed(color) : $elm$json$Json$Decode$fail('Opaque generated native color');
		},
		A3(
			$elm$json$Json$Decode$map2,
			$elm$core$Tuple$pair,
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			A2($elm$json$Json$Decode$field, 'colorARGB', $author$project$NativeFamilyPreviewSource$positive))));
var $author$project$NativeFamilyPreviewSource$Observation = $elm$core$Basics$identity;
var $author$project$NativeFamilyPreviewSource$binding = A2(
	$author$project$NativeFamilyPreviewSource$strict,
	_List_fromArray(
		['lifetime', 'session', 'frontend']),
	A4(
		$elm$json$Json$Decode$map3,
		F3(
			function (a, b, c) {
				return _Utils_Tuple3(a, b, c);
			}),
		A2($elm$json$Json$Decode$field, 'lifetime', $author$project$NativeFamilyPreviewSource$positive),
		A2($elm$json$Json$Decode$field, 'session', $author$project$NativeFamilyPreviewSource$positive),
		A2($elm$json$Json$Decode$field, 'frontend', $author$project$NativeFamilyPreviewSource$positive)));
var $author$project$NativeFamilyPreviewSource$Crop = F5(
	function (x, y, width, height, scale) {
		return {bT: height, cd: scale, ck: width, cl: x, cm: y};
	});
var $author$project$NativeFamilyPreviewSource$boundedInt = F2(
	function (lower, upper) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (value) {
				return ((_Utils_cmp(value, lower) > -1) && (_Utils_cmp(value, upper) < 1)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Native family integer bound');
			},
			$elm$json$Json$Decode$int);
	});
var $elm$json$Json$Decode$float = _Json_decodeFloat;
var $elm$core$Basics$isInfinite = _Basics_isInfinite;
var $elm$core$Basics$isNaN = _Basics_isNaN;
var $author$project$NativeFamilyPreviewSource$finite = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return ($elm$core$Basics$isNaN(value) || $elm$core$Basics$isInfinite(value)) ? $elm$json$Json$Decode$fail('Finite native family value') : $elm$json$Json$Decode$succeed(value);
	},
	$elm$json$Json$Decode$float);
var $author$project$NativeFamilyPreviewSource$signedPixel = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		var negative = A2($elm$core$String$startsWith, '-', value);
		var limit = negative ? '2147483648' : '2147483647';
		var digits = negative ? A2($elm$core$String$dropLeft, 1, value) : value;
		return ((!$elm$core$String$isEmpty(digits)) && (A2(
			$elm$core$String$all,
			function (c) {
				return (c >= '0') && (c <= '9');
			},
			digits) && (((digits === '0') || (!A2($elm$core$String$startsWith, '0', digits))) && ((!(negative && (digits === '0'))) && (($elm$core$String$length(digits) <= 10) && (($elm$core$String$length(digits) < 10) || (_Utils_cmp(digits, limit) < 1))))))) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Canonical signed native crop origin');
	},
	$elm$json$Json$Decode$string);
var $author$project$NativeFamilyPreviewSource$cropDecoder = A2(
	$author$project$NativeFamilyPreviewSource$strict,
	_List_fromArray(
		['pixelX', 'pixelY', 'width', 'height', 'scale']),
	A6(
		$elm$json$Json$Decode$map5,
		$author$project$NativeFamilyPreviewSource$Crop,
		A2($elm$json$Json$Decode$field, 'pixelX', $author$project$NativeFamilyPreviewSource$signedPixel),
		A2($elm$json$Json$Decode$field, 'pixelY', $author$project$NativeFamilyPreviewSource$signedPixel),
		A2(
			$elm$json$Json$Decode$field,
			'width',
			A2($author$project$NativeFamilyPreviewSource$boundedInt, 1, 4096)),
		A2(
			$elm$json$Json$Decode$field,
			'height',
			A2($author$project$NativeFamilyPreviewSource$boundedInt, 1, 4096)),
		A2(
			$elm$json$Json$Decode$field,
			'scale',
			A2(
				$elm$json$Json$Decode$andThen,
				function (value) {
					return (value > 0) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Native positive scale');
				},
				$author$project$NativeFamilyPreviewSource$finite))));
var $author$project$NativeFamilyPreviewSource$Member = F6(
	function (incarnation, parent, content, order, flags, geometry) {
		return {cv: content, bQ: flags, cz: geometry, aH: incarnation, cI: order, bw: parent};
	});
var $author$project$NativeFamilyPreviewSource$fixed = F2(
	function (size, decode) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (values) {
				return _Utils_eq(
					$elm$core$List$length(values),
					size) ? $elm$json$Json$Decode$succeed(values) : $elm$json$Json$Decode$fail('Native family vector shape');
			},
			$elm$json$Json$Decode$list(decode));
	});
var $author$project$NativeFamilyPreviewSource$memberDecoder = A2(
	$author$project$NativeFamilyPreviewSource$strict,
	_List_fromArray(
		['incarnation', 'parent', 'content', 'renderOrder', 'flags', 'geometry']),
	A7(
		$elm$json$Json$Decode$map6,
		$author$project$NativeFamilyPreviewSource$Member,
		A2($elm$json$Json$Decode$field, 'incarnation', $author$project$NativeFamilyPreviewSource$positive),
		A2(
			$elm$json$Json$Decode$field,
			'parent',
			$elm$json$Json$Decode$nullable($author$project$NativeFamilyPreviewSource$positive)),
		A2($elm$json$Json$Decode$field, 'content', $author$project$NativeFamilyPreviewSource$positive),
		A2(
			$elm$json$Json$Decode$field,
			'renderOrder',
			A2($author$project$NativeFamilyPreviewSource$boundedInt, 0, 2147483647)),
		A2(
			$elm$json$Json$Decode$field,
			'flags',
			A2($author$project$NativeFamilyPreviewSource$boundedInt, 0, 511)),
		A2(
			$elm$json$Json$Decode$field,
			'geometry',
			A2($author$project$NativeFamilyPreviewSource$fixed, 8, $author$project$NativeFamilyPreviewSource$finite))));
var $elm$core$Basics$modBy = _Basics_modBy;
var $author$project$NativeFamilyPreviewSource$reachesRoot = F4(
	function (root, members, remaining, current) {
		if (remaining <= 0) {
			return false;
		} else {
			var _v0 = $elm$core$List$head(
				A2(
					$elm$core$List$filter,
					function (member) {
						return _Utils_eq(member.aH, current);
					},
					members));
			if (_v0.$ === 1) {
				return false;
			} else {
				var member = _v0.a;
				return _Utils_eq(current, root) ? _Utils_eq(member.bw, $elm$core$Maybe$Nothing) : A2(
					$elm$core$Maybe$withDefault,
					false,
					A2(
						$elm$core$Maybe$map,
						A3($author$project$NativeFamilyPreviewSource$reachesRoot, root, members, remaining - 1),
						member.bw));
			}
		}
	});
var $author$project$PreviewLifecycle$Scope = $elm$core$Basics$identity;
var $author$project$PreviewLifecycle$scopeDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (scope) {
		return _Utils_eq(scope.b.aV, scope.g.aV) ? $elm$json$Json$Decode$succeed(scope) : $elm$json$Json$Decode$fail('Scope lifetime does not match binding');
	},
	$author$project$PreviewLifecycle$nativeScopeDecoder);
var $author$project$NativeFamilyPreviewSource$Style = F4(
	function (incarnation, flags, channels, gradients) {
		return {ct: channels, bQ: flags, cA: gradients, aH: incarnation};
	});
var $author$project$NativeFamilyPreviewSource$Gradient = F2(
	function (angle, colors) {
		return {cp: angle, cu: colors};
	});
var $author$project$NativeFamilyPreviewSource$gradientDecoder = A2(
	$author$project$NativeFamilyPreviewSource$strict,
	_List_fromArray(
		['angle', 'colors']),
	A3(
		$elm$json$Json$Decode$map2,
		$author$project$NativeFamilyPreviewSource$Gradient,
		A2($elm$json$Json$Decode$field, 'angle', $author$project$NativeFamilyPreviewSource$finite),
		A2(
			$elm$json$Json$Decode$field,
			'colors',
			A2($author$project$NativeFamilyPreviewSource$boundedInt, 0, 65536))));
var $author$project$NativeFamilyPreviewSource$styleDecoder = A2(
	$author$project$NativeFamilyPreviewSource$strict,
	_List_fromArray(
		['incarnation', 'flags', 'channels', 'gradients']),
	A5(
		$elm$json$Json$Decode$map4,
		$author$project$NativeFamilyPreviewSource$Style,
		A2($elm$json$Json$Decode$field, 'incarnation', $author$project$NativeFamilyPreviewSource$positive),
		A2(
			$elm$json$Json$Decode$field,
			'flags',
			A2($author$project$NativeFamilyPreviewSource$boundedInt, 0, 4095)),
		A2(
			$elm$json$Json$Decode$field,
			'channels',
			A2($author$project$NativeFamilyPreviewSource$fixed, 18, $author$project$NativeFamilyPreviewSource$finite)),
		A2(
			$elm$json$Json$Decode$field,
			'gradients',
			A2($author$project$NativeFamilyPreviewSource$fixed, 6, $author$project$NativeFamilyPreviewSource$gradientDecoder))));
var $author$project$NativeFamilyPreviewSource$familyDecoder = function (plane_) {
	var fields = function () {
		switch (plane_.$) {
			case 0:
				return _List_Nil;
			case 1:
				return _List_Nil;
			default:
				return _List_fromArray(
					['generatedBackdrop']);
		}
	}();
	var expectedLabel = function () {
		switch (plane_.$) {
			case 0:
				return 'native-family-style-crop-channels-unqualified';
			case 1:
				return 'picker-native-family-style-crop';
			default:
				return 'native-generated-backdrop-family-crop-unqualified';
		}
	}();
	var expectedKind = function () {
		switch (plane_.$) {
			case 0:
				return 'preview-family-style-crop-scope';
			case 1:
				return 'preview-picker-family-scope';
			default:
				return 'preview-family-backdrop-crop-scope';
		}
	}();
	return A2(
		$author$project$NativeFamilyPreviewSource$strict,
		_Utils_ap(
			fields,
			_List_fromArray(
				['protocolVersion', 'kind', 'binding', 'requestId', 'scope', 'maximumTransferBytes', 'previewEligible', 'scopeKind', 'members', 'styles', 'crop'])),
		A2(
			$elm$json$Json$Decode$andThen,
			function (wire) {
				return A2(
					$elm$json$Json$Decode$andThen,
					function (_v0) {
						var members = _v0.a;
						var styles = _v0.b;
						var crop = _v0.c;
						var styleIds = A2(
							$elm$core$List$map,
							A2(
								$elm$core$Basics$composeR,
								function ($) {
									return $.aH;
								},
								$author$project$UInt64$string),
							styles);
						var maximum = $author$project$UInt64$string(wire.at);
						var withinBudget = ($elm$core$String$length(maximum) < 9) || (($elm$core$String$length(maximum) === 9) && (maximum <= '134217728'));
						var ids = A2(
							$elm$core$List$map,
							A2(
								$elm$core$Basics$composeR,
								function ($) {
									return $.aH;
								},
								$author$project$UInt64$string),
							members);
						var facts = A5(
							$elm$json$Json$Decode$map4,
							F4(
								function (own, lifetime, clock, root) {
									return {U: clock, aV: lifetime, b1: own, cc: root};
								}),
							A2($elm$json$Json$Decode$field, 'binding', $author$project$NativeFamilyPreviewSource$binding),
							A2(
								$elm$json$Json$Decode$at,
								_List_fromArray(
									['context', 'lifetime']),
								$author$project$NativeFamilyPreviewSource$positive),
							A2($elm$json$Json$Decode$field, 'clock', $author$project$NativeFamilyPreviewSource$positive),
							A2(
								$elm$json$Json$Decode$at,
								_List_fromArray(
									['context', 'incarnation']),
								$author$project$NativeFamilyPreviewSource$positive));
						var aligned = !A3(
							$elm$core$String$foldl,
							F2(
								function (digit, remainder) {
									return A2(
										$elm$core$Basics$modBy,
										4096,
										((remainder * 10) + $elm$core$Char$toCode(digit)) - 48);
								}),
							0,
							$author$project$UInt64$string(wire.at));
						var _v1 = _Utils_Tuple2(
							A2($elm$json$Json$Decode$decodeValue, $author$project$PreviewLifecycle$scopeDecoder, wire.aw),
							A2($elm$json$Json$Decode$decodeValue, facts, wire.aw));
						if ((!_v1.a.$) && (!_v1.b.$)) {
							var _native = _v1.a.a;
							var current = _v1.b.a;
							return ((wire.ci === 3) && (_Utils_eq(wire.bX, expectedKind) && (_Utils_eq(wire.bY, expectedLabel) && (_Utils_eq(
								wire.bL,
								_Utils_eq(plane_, $author$project$NativeFamilyPreviewSource$PickerTransparent)) && (_Utils_eq(wire.b2, current.b1) && (_Utils_eq(current.aV, current.U) && (aligned && (withinBudget && (($elm$core$List$length(ids) > 0) && (($elm$core$List$length(ids) <= 256) && (_Utils_eq(
								$elm$core$Set$size(
									$elm$core$Set$fromList(ids)),
								$elm$core$List$length(ids)) && (_Utils_eq(
								$elm$core$List$sort(ids),
								$elm$core$List$sort(styleIds)) && A2(
								$elm$core$List$all,
								function (member) {
									return A4(
										$author$project$NativeFamilyPreviewSource$reachesRoot,
										current.cc,
										members,
										$elm$core$List$length(members),
										member.aH);
								},
								members))))))))))))) ? $elm$json$Json$Decode$succeed(
								{aC: crop, at: wire.at, bZ: members, j: _native, aZ: plane_, aw: wire.aw, a_: wire.a_, cf: styles}) : $elm$json$Json$Decode$fail('Native family correlation');
						} else {
							return $elm$json$Json$Decode$fail('Native family scope');
						}
					},
					A4(
						$elm$json$Json$Decode$map3,
						F3(
							function (members, styles, crop) {
								return _Utils_Tuple3(members, styles, crop);
							}),
						A2(
							$elm$json$Json$Decode$field,
							'members',
							$elm$json$Json$Decode$list($author$project$NativeFamilyPreviewSource$memberDecoder)),
						A2(
							$elm$json$Json$Decode$field,
							'styles',
							$elm$json$Json$Decode$list($author$project$NativeFamilyPreviewSource$styleDecoder)),
						A2($elm$json$Json$Decode$field, 'crop', $author$project$NativeFamilyPreviewSource$cropDecoder)));
			},
			A9(
				$elm$json$Json$Decode$map8,
				F8(
					function (version, kind, owner, request, raw, maximum, eligible, label) {
						return {bL: eligible, bX: kind, bY: label, at: maximum, b2: owner, aw: raw, a_: request, ci: version};
					}),
				A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int),
				A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
				A2($elm$json$Json$Decode$field, 'binding', $author$project$NativeFamilyPreviewSource$binding),
				A2($elm$json$Json$Decode$field, 'requestId', $author$project$NativeFamilyPreviewSource$positive),
				A2($elm$json$Json$Decode$field, 'scope', $elm$json$Json$Decode$value),
				A2($elm$json$Json$Decode$field, 'maximumTransferBytes', $author$project$NativeFamilyPreviewSource$positive),
				A2($elm$json$Json$Decode$field, 'previewEligible', $elm$json$Json$Decode$bool),
				A2($elm$json$Json$Decode$field, 'scopeKind', $elm$json$Json$Decode$string))));
};
var $author$project$NativeFamilyPreviewSource$decoder = A2(
	$elm$json$Json$Decode$andThen,
	function (kind) {
		return (kind === 'preview-family-style-crop-scope') ? $author$project$NativeFamilyPreviewSource$familyDecoder($author$project$NativeFamilyPreviewSource$Transparent) : ((kind === 'preview-picker-family-scope') ? $author$project$NativeFamilyPreviewSource$familyDecoder($author$project$NativeFamilyPreviewSource$PickerTransparent) : ((kind === 'preview-family-backdrop-crop-scope') ? A2(
			$elm$json$Json$Decode$andThen,
			A2($elm$core$Basics$composeR, $author$project$NativeFamilyPreviewSource$GeneratedOpaque, $author$project$NativeFamilyPreviewSource$familyDecoder),
			A2($elm$json$Json$Decode$field, 'generatedBackdrop', $author$project$NativeFamilyPreviewSource$backdropDecoder)) : $elm$json$Json$Decode$fail('Explicit native family source kind')));
	},
	A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string));
var $author$project$NativePreviewSource$ClientMain = {$: 1};
var $author$project$NativePreviewSource$MonitorPlane = {$: 0};
var $author$project$NativePreviewSource$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (n) {
		return (!_Utils_eq(n, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(n) : $elm$json$Json$Decode$fail('Positive native source identity');
	},
	$author$project$UInt64$decoder);
var $author$project$NativePreviewSource$strict = F2(
	function (fields, decoder_) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? decoder_ : $elm$json$Json$Decode$fail('Native source fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$NativePreviewSource$binding = A2(
	$author$project$NativePreviewSource$strict,
	_List_fromArray(
		['lifetime', 'session', 'frontend']),
	A4(
		$elm$json$Json$Decode$map3,
		F3(
			function (a, b, c) {
				return _Utils_Tuple3(a, b, c);
			}),
		A2($elm$json$Json$Decode$field, 'lifetime', $author$project$NativePreviewSource$positive),
		A2($elm$json$Json$Decode$field, 'session', $author$project$NativePreviewSource$positive),
		A2($elm$json$Json$Decode$field, 'frontend', $author$project$NativePreviewSource$positive)));
var $author$project$NativePreviewSource$legacyDecoder = A2(
	$author$project$NativePreviewSource$strict,
	_List_fromArray(
		['protocolVersion', 'kind', 'binding', 'requestId', 'scope', 'maximumTransferBytes', 'previewEligible', 'scopeKind']),
	A2(
		$elm$json$Json$Decode$andThen,
		function (wire) {
			var source_ = function () {
				var _v2 = _Utils_Tuple2(wire.bX, wire.bY);
				_v2$2:
				while (true) {
					switch (_v2.a) {
						case 'preview-capture-probe-scope':
							if (_v2.b === 'root-surface-commit-monitor-plane-unqualified') {
								return $elm$core$Maybe$Just($author$project$NativePreviewSource$MonitorPlane);
							} else {
								break _v2$2;
							}
						case 'preview-client-scope':
							if (_v2.b === 'isolated-root-client-unqualified') {
								return $elm$core$Maybe$Just($author$project$NativePreviewSource$ClientMain);
							} else {
								break _v2$2;
							}
						default:
							break _v2$2;
					}
				}
				return $elm$core$Maybe$Nothing;
			}();
			var facts = A4(
				$elm$json$Json$Decode$map3,
				F3(
					function (own, lifetime, clock) {
						return _Utils_Tuple3(own, lifetime, clock);
					}),
				A2($elm$json$Json$Decode$field, 'binding', $author$project$NativePreviewSource$binding),
				A2(
					$elm$json$Json$Decode$at,
					_List_fromArray(
						['context', 'lifetime']),
					$author$project$NativePreviewSource$positive),
				A2($elm$json$Json$Decode$field, 'clock', $author$project$NativePreviewSource$positive));
			var _v0 = _Utils_Tuple3(
				source_,
				A2($elm$json$Json$Decode$decodeValue, $author$project$PreviewLifecycle$scopeDecoder, wire.aw),
				A2($elm$json$Json$Decode$decodeValue, facts, wire.aw));
			if (((!_v0.a.$) && (!_v0.b.$)) && (!_v0.c.$)) {
				var admitted = _v0.a.a;
				var _native = _v0.b.a;
				var _v1 = _v0.c.a;
				var own = _v1.a;
				var lifetime = _v1.b;
				var clock = _v1.c;
				return ((wire.ci === 3) && ((!wire.bL) && (_Utils_eq(wire.b2, own) && (_Utils_eq(lifetime, clock) && (!A3(
					$elm$core$String$foldl,
					F2(
						function (digit, remainder) {
							return A2(
								$elm$core$Basics$modBy,
								4096,
								((remainder * 10) + $elm$core$Char$toCode(digit)) - 48);
						}),
					0,
					$author$project$UInt64$string(wire.at))))))) ? $elm$json$Json$Decode$succeed(
					{bt: wire.at, j: _native, aw: wire.aw, a_: wire.a_, aP: admitted}) : $elm$json$Json$Decode$fail('Native source grant/clock/eligibility');
			} else {
				return $elm$json$Json$Decode$fail('Typed native source kind/scope');
			}
		},
		A9(
			$elm$json$Json$Decode$map8,
			F8(
				function (version, kind, owner, request, raw, maximum, eligible, label) {
					return {bL: eligible, bX: kind, bY: label, at: maximum, b2: owner, aw: raw, a_: request, ci: version};
				}),
			A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int),
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			A2($elm$json$Json$Decode$field, 'binding', $author$project$NativePreviewSource$binding),
			A2($elm$json$Json$Decode$field, 'requestId', $author$project$NativePreviewSource$positive),
			A2($elm$json$Json$Decode$field, 'scope', $elm$json$Json$Decode$value),
			A2($elm$json$Json$Decode$field, 'maximumTransferBytes', $author$project$NativePreviewSource$positive),
			A2($elm$json$Json$Decode$field, 'previewEligible', $elm$json$Json$Decode$bool),
			A2($elm$json$Json$Decode$field, 'scopeKind', $elm$json$Json$Decode$string))));
var $author$project$NativeFamilyPreviewSource$maximumTransfer = function (_v0) {
	var value = _v0;
	return value.at;
};
var $author$project$NativeFamilyPreviewSource$plane = function (_v0) {
	var value = _v0;
	return value.aZ;
};
var $author$project$NativeFamilyPreviewSource$rawScope = function (_v0) {
	var value = _v0;
	return value.aw;
};
var $author$project$NativeFamilyPreviewSource$requestIdentity = function (_v0) {
	var value = _v0;
	return value.a_;
};
var $author$project$NativeFamilyPreviewSource$scope = function (_v0) {
	var value = _v0;
	return value.j;
};
var $author$project$NativePreviewSource$decoder = A2(
	$elm$json$Json$Decode$andThen,
	function (kind) {
		return ((kind === 'preview-family-style-crop-scope') || ((kind === 'preview-family-backdrop-crop-scope') || (kind === 'preview-picker-family-scope'))) ? A2(
			$elm$json$Json$Decode$map,
			function (family) {
				return {
					bt: $author$project$NativeFamilyPreviewSource$maximumTransfer(family),
					j: $author$project$NativeFamilyPreviewSource$scope(family),
					aw: $author$project$NativeFamilyPreviewSource$rawScope(family),
					a_: $author$project$NativeFamilyPreviewSource$requestIdentity(family),
					aP: function () {
						var _v0 = $author$project$NativeFamilyPreviewSource$plane(family);
						switch (_v0.$) {
							case 0:
								return $author$project$NativePreviewSource$StyleCroppedFamily;
							case 1:
								return $author$project$NativePreviewSource$PickerFamily;
							default:
								var color = _v0.a;
								return $author$project$NativePreviewSource$GeneratedBackdropFamily(color);
						}
					}()
				};
			},
			$author$project$NativeFamilyPreviewSource$decoder) : $author$project$NativePreviewSource$legacyDecoder;
	},
	A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string));
var $author$project$NativeActorRetirement$Delivery = F2(
	function (ordinal, fact) {
		return {bP: fact, b0: ordinal};
	});
var $author$project$NativeActorRetirement$deliveryDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (_v0) {
		var kind = _v0.a;
		var delivery = _v0.b;
		return (kind === 'native-actor-retirement-delivery') ? $elm$json$Json$Decode$succeed(delivery) : $elm$json$Json$Decode$fail('Retained native retirement delivery');
	},
	A2(
		$author$project$NativeActorRetirement$strict,
		_List_fromArray(
			['kind', 'deliveryOrdinal', 'fact']),
		A4(
			$elm$json$Json$Decode$map3,
			F3(
				function (kind, ordinal, fact) {
					return _Utils_Tuple2(
						kind,
						A2($author$project$NativeActorRetirement$Delivery, ordinal, fact));
				}),
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			A2($elm$json$Json$Decode$field, 'deliveryOrdinal', $author$project$NativeActorRetirement$positive),
			A2($elm$json$Json$Decode$field, 'fact', $author$project$NativeActorRetirement$actorDecoder))));
var $author$project$NativePreviewDetachment$Delivery = F2(
	function (ordinal, seed) {
		return {b0: ordinal, bj: seed};
	});
var $author$project$NativePreviewDetachment$Seed = F5(
	function (domain, subject, entry, entryIssuedThrough, requestFloor) {
		return {aT: domain, bN: entry, a8: entryIssuedThrough, cJ: requestFloor, aA: subject};
	});
var $author$project$NativePreviewDetachment$coherent = function (seed) {
	return A2($author$project$UInt64$compare, seed.bN, seed.a8) !== 2;
};
var $author$project$NativePreviewDetachment$positive = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		return (!_Utils_eq(value, $author$project$UInt64$zero)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Positive scoped detachment identity');
	},
	$author$project$UInt64$decoder);
var $author$project$NativePreviewDetachment$strict = F2(
	function (fields, decoder) {
		return A2(
			$elm$json$Json$Decode$andThen,
			function (pairs) {
				return _Utils_eq(
					$elm$core$List$sort(
						A2($elm$core$List$map, $elm$core$Tuple$first, pairs)),
					$elm$core$List$sort(fields)) ? decoder : $elm$json$Json$Decode$fail('Exact scoped preview detachment fields');
			},
			$elm$json$Json$Decode$keyValuePairs($elm$json$Json$Decode$value));
	});
var $author$project$NativePreviewDetachment$eventDecoder = function (domain) {
	return A2(
		$elm$json$Json$Decode$andThen,
		function (_v0) {
			var kind = _v0.a;
			var identity = _v0.b;
			var seed = _v0.c;
			return ((kind === 'native-preview-actor-detached') && (_Utils_eq(
				identity,
				'family:' + $author$project$UInt64$string(seed.aA)) && $author$project$NativePreviewDetachment$coherent(seed))) ? $elm$json$Json$Decode$succeed(seed) : $elm$json$Json$Decode$fail('Distinct native preview membership completion');
		},
		A2(
			$author$project$NativePreviewDetachment$strict,
			_List_fromArray(
				['kind', 'identity', 'subject', 'entry', 'entryIssuedThrough', 'requestFloor']),
			A7(
				$elm$json$Json$Decode$map6,
				F6(
					function (kind, identity, subject, entry, frontier, floor) {
						return _Utils_Tuple3(
							kind,
							identity,
							A5($author$project$NativePreviewDetachment$Seed, domain, subject, entry, frontier, floor));
					}),
				A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
				A2($elm$json$Json$Decode$field, 'identity', $elm$json$Json$Decode$string),
				A2($elm$json$Json$Decode$field, 'subject', $author$project$NativePreviewDetachment$positive),
				A2($elm$json$Json$Decode$field, 'entry', $author$project$NativePreviewDetachment$positive),
				A2($elm$json$Json$Decode$field, 'entryIssuedThrough', $author$project$NativePreviewDetachment$positive),
				A2($elm$json$Json$Decode$field, 'requestFloor', $author$project$UInt64$decoder))));
};
var $author$project$NativePreviewDetachment$deliveryDecoder = A2(
	$author$project$NativePreviewDetachment$strict,
	_List_fromArray(
		['detachProtocol', 'kind', 'binding', 'receiverEpoch', 'deliveryOrdinal', 'event']),
	A2(
		$elm$json$Json$Decode$andThen,
		function (_v0) {
			var protocol = _v0.a;
			var kind = _v0.b;
			var _v1 = _v0.c;
			var domain = _v1.a;
			var ordinal = _v1.b;
			return ((protocol === 1) && (kind === 'native-preview-binding-detach-delivery')) ? A2(
				$elm$json$Json$Decode$map,
				$author$project$NativePreviewDetachment$Delivery(ordinal),
				A2(
					$elm$json$Json$Decode$field,
					'event',
					$author$project$NativePreviewDetachment$eventDecoder(domain))) : $elm$json$Json$Decode$fail('Distinct retained scoped detachment delivery');
		},
		A5(
			$elm$json$Json$Decode$map4,
			F4(
				function (protocol, kind, domain, ordinal) {
					return _Utils_Tuple3(
						protocol,
						kind,
						_Utils_Tuple2(domain, ordinal));
				}),
			A2($elm$json$Json$Decode$field, 'detachProtocol', $elm$json$Json$Decode$int),
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			$author$project$NativePreviewRealm$domainDecoder,
			A2($elm$json$Json$Decode$field, 'deliveryOrdinal', $author$project$NativePreviewDetachment$positive))));
var $author$project$PreviewLifecycle$IconHandle = $elm$core$Basics$identity;
var $author$project$PreviewLifecycle$iconDecoder = A2($elm$json$Json$Decode$map, $elm$core$Basics$identity, $author$project$PreviewLifecycle$opaqueDecoder);
var $author$project$NativeActorRetirement$observationDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (_v0) {
		var value = _v0.a;
		var state = _v0.b;
		return ((state === 'Retired') && $author$project$NativeActorRetirement$validate(value)) ? $elm$json$Json$Decode$succeed(value) : $elm$json$Json$Decode$fail('Exact permanent native retirement observation');
	},
	A2(
		$author$project$NativeActorRetirement$strict,
		_List_fromArray(
			['kind', 'binding', 'subject', 'request', 'sequence', 'clock', 'now', 'issuedThrough', 'state']),
		A3(
			$elm$json$Json$Decode$map2,
			$elm$core$Tuple$pair,
			$author$project$NativeActorRetirement$nativeDecoder,
			A2($elm$json$Json$Decode$field, 'state', $elm$json$Json$Decode$string))));
var $author$project$PreviewPresenter$Capacity = 0;
var $author$project$PreviewPresenter$Conflict = 3;
var $author$project$PreviewPresenter$Exhausted = 4;
var $author$project$PreviewPresenter$Expired = 2;
var $author$project$PreviewPresenter$Waiting = 1;
var $author$project$PreviewPresenter$outcomeDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (value) {
		switch (value) {
			case 'capacity':
				return $elm$json$Json$Decode$succeed(0);
			case 'waiting':
				return $elm$json$Json$Decode$succeed(1);
			case 'expired':
				return $elm$json$Json$Decode$succeed(2);
			case 'conflict':
				return $elm$json$Json$Decode$succeed(3);
			case 'exhausted':
				return $elm$json$Json$Decode$succeed(4);
			default:
				return $elm$json$Json$Decode$fail('Typed local preview outcome');
		}
	},
	$elm$json$Json$Decode$string);
var $author$project$NativePreviewSource$scope = function (_v0) {
	var value = _v0;
	return value.j;
};
var $author$project$NativePreviewDetachment$seedDecoder = A2(
	$elm$json$Json$Decode$andThen,
	function (_v0) {
		var protocol = _v0.a;
		var kind = _v0.b;
		var _v1 = _v0.c;
		var identity = _v1.a;
		var seed = _v1.b;
		return ((protocol === 1) && ((kind === 'native-preview-detach-seed') && (_Utils_eq(
			identity,
			'family:' + $author$project$UInt64$string(seed.aA)) && $author$project$NativePreviewDetachment$coherent(seed)))) ? $elm$json$Json$Decode$succeed(seed) : $elm$json$Json$Decode$fail('Exact native scoped detachment seed');
	},
	A2(
		$author$project$NativePreviewDetachment$strict,
		_List_fromArray(
			['detachProtocol', 'kind', 'identity', 'binding', 'receiverEpoch', 'subject', 'entry', 'entryIssuedThrough', 'requestFloor']),
		A9(
			$elm$json$Json$Decode$map8,
			F8(
				function (protocol, kind, identity, domain, subject, entry, frontier, floor) {
					return _Utils_Tuple3(
						protocol,
						kind,
						_Utils_Tuple2(
							identity,
							A5($author$project$NativePreviewDetachment$Seed, domain, subject, entry, frontier, floor)));
				}),
			A2($elm$json$Json$Decode$field, 'detachProtocol', $elm$json$Json$Decode$int),
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			A2($elm$json$Json$Decode$field, 'identity', $elm$json$Json$Decode$string),
			$author$project$NativePreviewRealm$domainDecoder,
			A2($elm$json$Json$Decode$field, 'subject', $author$project$NativePreviewDetachment$positive),
			A2($elm$json$Json$Decode$field, 'entry', $author$project$NativePreviewDetachment$positive),
			A2($elm$json$Json$Decode$field, 'entryIssuedThrough', $author$project$NativePreviewDetachment$positive),
			A2($elm$json$Json$Decode$field, 'requestFloor', $author$project$UInt64$decoder))));
var $author$project$NativePreviewSource$source = function (_v0) {
	var value = _v0;
	return value.aP;
};
var $author$project$PreviewPresenter$Window = F4(
	function (subject, title, application, minimized) {
		return {p: application, Z: minimized, aA: subject, bD: title};
	});
var $author$project$PreviewPresenter$windows = A2(
	$elm$json$Json$Decode$andThen,
	function (rows) {
		return (($elm$core$List$length(rows) <= 256) && _Utils_eq(
			$elm$core$Set$size(
				$elm$core$Set$fromList(
					A2(
						$elm$core$List$map,
						A2(
							$elm$core$Basics$composeR,
							function ($) {
								return $.aA;
							},
							$author$project$UInt64$string),
						rows))),
			$elm$core$List$length(rows))) ? $elm$json$Json$Decode$succeed(rows) : $elm$json$Json$Decode$fail('Unique bounded catalog');
	},
	$elm$json$Json$Decode$list(
		A2(
			$author$project$PreviewPresenter$strict,
			_List_fromArray(
				['incarnation', 'application', 'label', 'minimized']),
			A5(
				$elm$json$Json$Decode$map4,
				$author$project$PreviewPresenter$Window,
				A2($elm$json$Json$Decode$field, 'incarnation', $author$project$PreviewPresenter$positive),
				A2($elm$json$Json$Decode$field, 'label', $author$project$PreviewPresenter$bounded),
				A2($elm$json$Json$Decode$field, 'application', $author$project$PreviewPresenter$bounded),
				A2($elm$json$Json$Decode$field, 'minimized', $elm$json$Json$Decode$bool)))));
var $author$project$PreviewPresenter$input = A2(
	$elm$json$Json$Decode$andThen,
	function (kind) {
		switch (kind) {
			case 'native-preview-detach-seed':
				return A2($elm$json$Json$Decode$map, $author$project$PreviewPresenter$DetachSeed, $author$project$NativePreviewDetachment$seedDecoder);
			case 'native-preview-binding-detach-delivery':
				return A2($elm$json$Json$Decode$map, $author$project$PreviewPresenter$Detached, $author$project$NativePreviewDetachment$deliveryDecoder);
			case 'native-incarnation-retirement':
				return A2($elm$json$Json$Decode$map, $author$project$PreviewPresenter$Retirement, $author$project$NativeActorRetirement$observationDecoder);
			case 'native-actor-retired':
				return A2($elm$json$Json$Decode$map, $author$project$PreviewPresenter$Retired, $author$project$NativeActorRetirement$actorDecoder);
			case 'native-actor-retirement-channel':
				return A2($elm$json$Json$Decode$map, $author$project$PreviewPresenter$RetirementChannel, $author$project$NativeActorRetirement$channelDecoder);
			case 'native-actor-retirement-delivery':
				return A2($elm$json$Json$Decode$map, $author$project$PreviewPresenter$RetirementDelivery, $author$project$NativeActorRetirement$deliveryDecoder);
			case 'demand-feedback':
				return A2(
					$author$project$PreviewPresenter$strict,
					_List_fromArray(
						['kind', 'identity', 'binding', 'subject', 'clock', 'publication', 'lease', 'sequence', 'deadline', 'outcome']),
					A4(
						$elm$json$Json$Decode$map3,
						F3(
							function (identity, stamp, value) {
								return A2(
									$author$project$PreviewPresenter$Feedback,
									identity,
									_Utils_update(
										value,
										{k: stamp}));
							}),
						A2($elm$json$Json$Decode$field, 'identity', $author$project$PreviewPresenter$bounded),
						A3(
							$elm$json$Json$Decode$map2,
							$author$project$PreviewPresenter$Stamp,
							A2($elm$json$Json$Decode$field, 'publication', $author$project$PreviewPresenter$positive),
							A2($elm$json$Json$Decode$field, 'lease', $author$project$PreviewPresenter$positive)),
						A7(
							$elm$json$Json$Decode$map6,
							F6(
								function (owner, subject, clock, sequence, deadline, outcome) {
									return {
										U: clock,
										O: deadline,
										aY: outcome,
										b2: owner,
										ay: sequence,
										k: {bs: $author$project$UInt64$zero, bf: $author$project$UInt64$zero},
										aA: subject
									};
								}),
							A2($elm$json$Json$Decode$field, 'binding', $author$project$PreviewPresenter$binding),
							A2($elm$json$Json$Decode$field, 'subject', $author$project$PreviewPresenter$positive),
							A2($elm$json$Json$Decode$field, 'clock', $author$project$PreviewPresenter$positive),
							A2($elm$json$Json$Decode$field, 'sequence', $author$project$PreviewPresenter$positive),
							A2($elm$json$Json$Decode$field, 'deadline', $author$project$PreviewPresenter$positive),
							A2($elm$json$Json$Decode$field, 'outcome', $author$project$PreviewPresenter$outcomeDecoder))));
			case 'catalog':
				return A2(
					$author$project$PreviewPresenter$strict,
					_List_fromArray(
						['protocolVersion', 'kind', 'publication', 'lease', 'binding', 'requestId', 'sequence', 'revision', 'windows']),
					A2(
						$elm$json$Json$Decode$andThen,
						function (_v1) {
							var protocol = _v1.a;
							var result = _v1.b;
							return (protocol === 3) ? $elm$json$Json$Decode$succeed(result) : $elm$json$Json$Decode$fail('Native catalog protocol');
						},
						A9(
							$elm$json$Json$Decode$map8,
							F8(
								function (protocol, publication, lease, owner, request, sequence, revision, rows) {
									return _Utils_Tuple2(
										protocol,
										A3(
											$author$project$PreviewPresenter$Catalog,
											{bs: lease, bf: publication},
											{g: owner, a_: request, bh: revision, ay: sequence},
											rows));
								}),
							A2($elm$json$Json$Decode$field, 'protocolVersion', $elm$json$Json$Decode$int),
							A2($elm$json$Json$Decode$field, 'publication', $author$project$PreviewPresenter$positive),
							A2($elm$json$Json$Decode$field, 'lease', $author$project$PreviewPresenter$positive),
							A2($elm$json$Json$Decode$field, 'binding', $author$project$PreviewPresenter$binding),
							A2($elm$json$Json$Decode$field, 'requestId', $author$project$PreviewPresenter$positive),
							A2($elm$json$Json$Decode$field, 'sequence', $author$project$PreviewPresenter$positive),
							A2($elm$json$Json$Decode$field, 'revision', $author$project$PreviewPresenter$positive),
							A2($elm$json$Json$Decode$field, 'windows', $author$project$PreviewPresenter$windows))));
			case 'seed':
				return A2(
					$author$project$PreviewPresenter$strict,
					_List_fromArray(
						['kind', 'publication', 'lease', 'identity', 'scope', 'title', 'application']),
					A2(
						$elm$json$Json$Decode$andThen,
						function (seed) {
							var _v2 = _Utils_Tuple2(
								A2($elm$json$Json$Decode$decodeValue, $author$project$PreviewLifecycle$scopeDecoder, seed.aw),
								A2(
									$elm$json$Json$Decode$decodeValue,
									A2(
										$elm$json$Json$Decode$at,
										_List_fromArray(
											['context', 'incarnation']),
										$author$project$PreviewPresenter$positive),
									seed.aw));
							if ((!_v2.a.$) && (!_v2.b.$)) {
								var scope = _v2.a.a;
								var incarnation = _v2.b.a;
								return _Utils_eq(
									seed.aG,
									'family:' + $author$project$UInt64$string(incarnation)) ? $elm$json$Json$Decode$succeed(
									$author$project$PreviewPresenter$Seed(
										{bs: seed.bs, bf: seed.bf})(seed.aG)(scope)(seed.aw)(seed.bD)(seed.p)(seed.b2)($elm$core$Maybe$Nothing)(false)($elm$core$Maybe$Nothing)) : $elm$json$Json$Decode$fail('Preview control incarnation mismatch');
							} else {
								return $elm$json$Json$Decode$fail('Native preview scope');
							}
						},
						A8(
							$elm$json$Json$Decode$map7,
							F7(
								function (publication, lease, identity, raw, title, application, owner) {
									return {p: application, aG: identity, bs: lease, b2: owner, bf: publication, aw: raw, bD: title};
								}),
							A2($elm$json$Json$Decode$field, 'publication', $author$project$PreviewPresenter$positive),
							A2($elm$json$Json$Decode$field, 'lease', $author$project$PreviewPresenter$positive),
							A2($elm$json$Json$Decode$field, 'identity', $author$project$PreviewPresenter$bounded),
							A2($elm$json$Json$Decode$field, 'scope', $elm$json$Json$Decode$value),
							A2($elm$json$Json$Decode$field, 'title', $author$project$PreviewPresenter$bounded),
							A2($elm$json$Json$Decode$field, 'application', $author$project$PreviewPresenter$bounded),
							A2(
								$elm$json$Json$Decode$at,
								_List_fromArray(
									['scope', 'binding']),
								$author$project$PreviewPresenter$binding))));
			default:
				var sourceSeedKind = kind;
				if (A2(
					$elm$core$List$member,
					sourceSeedKind,
					_List_fromArray(
						['source-seed', 'demand-seed']))) {
					return A2(
						$author$project$PreviewPresenter$strict,
						_List_fromArray(
							['kind', 'publication', 'lease', 'identity', 'source', 'title', 'application']),
						A2(
							$elm$json$Json$Decode$andThen,
							function (seed) {
								var _v3 = _Utils_Tuple2(
									A2($elm$json$Json$Decode$decodeValue, $author$project$NativePreviewSource$decoder, seed.aw),
									A2(
										$elm$json$Json$Decode$decodeValue,
										A4(
											$elm$json$Json$Decode$map3,
											F3(
												function (_native, incarnation, owner) {
													return _Utils_Tuple3(_native, incarnation, owner);
												}),
											A2($elm$json$Json$Decode$field, 'scope', $elm$json$Json$Decode$value),
											A2(
												$elm$json$Json$Decode$at,
												_List_fromArray(
													['scope', 'context', 'incarnation']),
												$author$project$PreviewPresenter$positive),
											A2(
												$elm$json$Json$Decode$at,
												_List_fromArray(
													['scope', 'binding']),
												$author$project$PreviewPresenter$binding)),
										seed.aw));
								if ((!_v3.a.$) && (!_v3.b.$)) {
									var observation = _v3.a.a;
									var _v4 = _v3.b.a;
									var _native = _v4.a;
									var incarnation = _v4.b;
									var owner = _v4.c;
									return _Utils_eq(
										seed.aG,
										'family:' + $author$project$UInt64$string(incarnation)) ? $elm$json$Json$Decode$succeed(
										$author$project$PreviewPresenter$Seed(
											{bs: seed.bs, bf: seed.bf})(seed.aG)(
											$author$project$NativePreviewSource$scope(observation))(_native)(seed.bD)(seed.p)(owner)(
											$elm$core$Maybe$Just(
												$author$project$NativePreviewSource$source(observation)))(sourceSeedKind === 'demand-seed')(
											$elm$core$Result$toMaybe(
												A2(
													$elm$json$Json$Decode$decodeValue,
													A2($elm$json$Json$Decode$field, 'requestId', $author$project$PreviewPresenter$positive),
													seed.aw)))) : $elm$json$Json$Decode$fail('Typed source control incarnation mismatch');
								} else {
									return $elm$json$Json$Decode$fail('Typed native preview source');
								}
							},
							A7(
								$elm$json$Json$Decode$map6,
								F6(
									function (publication, lease, identity, raw, title, application) {
										return {p: application, aG: identity, bs: lease, bf: publication, aw: raw, bD: title};
									}),
								A2($elm$json$Json$Decode$field, 'publication', $author$project$PreviewPresenter$positive),
								A2($elm$json$Json$Decode$field, 'lease', $author$project$PreviewPresenter$positive),
								A2($elm$json$Json$Decode$field, 'identity', $author$project$PreviewPresenter$bounded),
								A2($elm$json$Json$Decode$field, 'source', $elm$json$Json$Decode$value),
								A2($elm$json$Json$Decode$field, 'title', $author$project$PreviewPresenter$bounded),
								A2($elm$json$Json$Decode$field, 'application', $author$project$PreviewPresenter$bounded))));
				} else {
					switch (sourceSeedKind) {
						case 'metadata':
							return A2(
								$author$project$PreviewPresenter$strict,
								_List_fromArray(
									['kind', 'identity', 'binding', 'subject', 'revision', 'title', 'application', 'icon', 'iconKind']),
								A9(
									$elm$json$Json$Decode$map8,
									$author$project$PreviewPresenter$Metadata,
									A2($elm$json$Json$Decode$field, 'identity', $author$project$PreviewPresenter$bounded),
									A2($elm$json$Json$Decode$field, 'binding', $author$project$PreviewPresenter$binding),
									A2($elm$json$Json$Decode$field, 'subject', $author$project$PreviewPresenter$positive),
									A2($elm$json$Json$Decode$field, 'revision', $author$project$PreviewPresenter$positive),
									A2($elm$json$Json$Decode$field, 'title', $author$project$PreviewPresenter$bounded),
									A2($elm$json$Json$Decode$field, 'application', $author$project$PreviewPresenter$bounded),
									A2(
										$elm$json$Json$Decode$field,
										'icon',
										$elm$json$Json$Decode$nullable($author$project$PreviewLifecycle$iconDecoder)),
									A2(
										$elm$json$Json$Decode$field,
										'iconKind',
										A2(
											$elm$json$Json$Decode$andThen,
											function (resolution) {
												return A2(
													$elm$core$List$member,
													resolution,
													_List_fromArray(
														['application', 'generic', 'unavailable'])) ? $elm$json$Json$Decode$succeed(resolution) : $elm$json$Json$Decode$fail('Native icon resolution');
											},
											$elm$json$Json$Decode$string))));
						case 'event':
							return A2(
								$author$project$PreviewPresenter$strict,
								_List_fromArray(
									['kind', 'identity', 'event']),
								A4(
									$elm$json$Json$Decode$map3,
									$author$project$PreviewPresenter$Event,
									A2($elm$json$Json$Decode$field, 'identity', $author$project$PreviewPresenter$bounded),
									A2($elm$json$Json$Decode$field, 'event', $author$project$PreviewLifecycle$eventDecoder),
									A2($elm$json$Json$Decode$field, 'event', $elm$json$Json$Decode$value)));
						default:
							return $elm$json$Json$Decode$fail('Preview presenter kind');
					}
				}
		}
	},
	A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string));
var $author$project$PreviewPresenter$eventRealmOwned = F2(
	function (domain, wire) {
		var owns = function (path) {
			return _Utils_eq(
				A2(
					$elm$json$Json$Decode$decodeValue,
					A2($elm$json$Json$Decode$at, path, $author$project$PreviewPresenter$binding),
					wire),
				$elm$core$Result$Ok(
					$author$project$NativePreviewRealm$owner(domain)));
		};
		var _v0 = A2(
			$elm$json$Json$Decode$decodeValue,
			A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
			wire);
		if (!_v0.$) {
			switch (_v0.a) {
				case 'open':
					return true;
				case 'close':
					return true;
				case 'request':
					return owns(
						_List_fromArray(
							['trigger', 'binding']));
				case 'observe':
					return owns(
						_List_fromArray(
							['scope', 'binding']));
				case 'attach':
					return owns(
						_List_fromArray(
							['previous'])) && owns(
						_List_fromArray(
							['scope', 'binding']));
				case 'clock':
					return owns(
						_List_fromArray(
							['binding']));
				case 'exhausted':
					return owns(
						_List_fromArray(
							['binding']));
				case 'source-denied':
					return owns(
						_List_fromArray(
							['job', 'binding']));
				case 'refused':
					return owns(
						_List_fromArray(
							['job', 'binding']));
				case 'cancelled':
					return owns(
						_List_fromArray(
							['job', 'binding']));
				case 'receipt':
					return A2(
						$elm$core$Result$withDefault,
						false,
						A2(
							$elm$core$Result$map,
							$author$project$PreviewPresenter$eventRealmOwned(domain),
							A2(
								$elm$json$Json$Decode$decodeValue,
								A2($elm$json$Json$Decode$field, 'event', $elm$json$Json$Decode$value),
								wire)));
				default:
					var kind = _v0.a;
					return A2(
						$elm$core$List$member,
						kind,
						_List_fromArray(
							['offer', 'fence', 'expired', 'released'])) && owns(
						_List_fromArray(
							['frame', 'job', 'binding']));
			}
		} else {
			return false;
		}
	});
var $author$project$PreviewPresenter$inputRealmOwned = F2(
	function (scoped, decoded) {
		var _v0 = scoped.r;
		if (_v0.$ === 1) {
			return true;
		} else {
			var grant = _v0.a;
			var own = function (owner) {
				return _Utils_eq(
					owner,
					$author$project$NativePreviewRealm$owner(grant.aT));
			};
			switch (decoded.$) {
				case 0:
					var owner = decoded.g;
					return own(owner);
				case 3:
					var current = decoded.b;
					return own(current.g);
				case 1:
					var owner = decoded.b;
					return own(owner);
				case 4:
					var local = decoded.b;
					return own(local.b2);
				case 2:
					var wire = decoded.c;
					return A2($author$project$PreviewPresenter$eventRealmOwned, grant.aT, wire);
				case 5:
					var observation = decoded.a;
					return own(
						$author$project$NativeActorRetirement$owner(observation));
				case 6:
					var fact = decoded.a;
					return own(
						$author$project$NativeActorRetirement$owner(fact.j));
				case 7:
					var owner = decoded.a;
					return own(owner);
				case 8:
					var delivery = decoded.a;
					return own(
						$author$project$NativeActorRetirement$owner(delivery.bP.j));
				case 9:
					var seed = decoded.a;
					return A2($author$project$NativePreviewRealm$same, grant.aT, seed.aT);
				default:
					var delivery = decoded.a;
					return A2($author$project$NativePreviewRealm$same, grant.aT, delivery.bj.aT);
			}
		}
	});
var $author$project$PreviewPresenter$retireEntry = function (entry) {
	var _v0 = entry.d;
	if (_v0.$ === 1) {
		return _Utils_Tuple2(
			_Utils_update(
				entry,
				{m: $elm$core$Maybe$Nothing, k: $elm$core$Maybe$Nothing}),
			_List_Nil);
	} else {
		var lifecycle = _v0.a;
		var _v1 = $author$project$PreviewLifecycle$retire(lifecycle);
		var retiring = _v1.a;
		var commands = _v1.b;
		return _Utils_Tuple2(
			_Utils_update(
				entry,
				{
					m: $elm$core$Maybe$Nothing,
					d: $elm$core$Maybe$Just(retiring),
					k: $elm$core$Maybe$Nothing
				}),
			commands);
	}
};
var $author$project$PreviewPresenter$sameSourcePlane = F2(
	function (old, current) {
		var _v0 = _Utils_Tuple2(old, current);
		if ((((!_v0.a.$) && (_v0.a.a.$ === 4)) && (!_v0.b.$)) && (_v0.b.a.$ === 4)) {
			return true;
		} else {
			return _Utils_eq(old, current);
		}
	});
var $author$project$NativeActorRetirement$scopeBefore = F2(
	function (observation, raw) {
		var _v0 = A2(
			$elm$json$Json$Decode$decodeValue,
			A3(
				$elm$json$Json$Decode$map2,
				$elm$core$Tuple$pair,
				A2($elm$json$Json$Decode$field, 'clock', $author$project$NativeActorRetirement$positive),
				A2($elm$json$Json$Decode$field, 'now', $author$project$NativeActorRetirement$positive)),
			raw);
		if (!_v0.$) {
			var _v1 = _v0.a;
			var clock = _v1.a;
			var now = _v1.b;
			return _Utils_eq(clock, observation.U) && (!(!A2($author$project$UInt64$compare, observation.af, now)));
		} else {
			return false;
		}
	});
var $author$project$PreviewLifecycle$settled = function (_v0) {
	var st = _v0;
	return (!st.H) && (_Utils_eq(st.h, $author$project$PreviewLifecycle$Idle) && (_Utils_eq(st.T, $elm$core$Maybe$Nothing) && ($elm$core$List$isEmpty(st.D) && ($elm$core$List$isEmpty(st.A) && $elm$core$List$isEmpty(st.w)))));
};
var $author$project$NativeActorRetirement$settles = F2(
	function (pending, fact) {
		return _Utils_eq(fact.j.aA, pending.aA) && A2(
			$author$project$NativeActorRetirement$fresh,
			$elm$core$Maybe$Just(pending),
			fact.j);
	});
var $elm$core$Dict$update = F3(
	function (targetKey, alter, dictionary) {
		var _v0 = alter(
			A2($elm$core$Dict$get, targetKey, dictionary));
		if (!_v0.$) {
			var value = _v0.a;
			return A3($elm$core$Dict$insert, targetKey, value, dictionary);
		} else {
			return A2($elm$core$Dict$remove, targetKey, dictionary);
		}
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
var $author$project$PreviewPresenter$receiveInput = F3(
	function (snapshot, raw, prior) {
		var entries = prior.a;
		var previousCatalog = prior.b;
		var ledger = prior.c;
		var scoped = prior.d;
		var _v0 = A2(
			$elm$core$Result$andThen,
			function (decoded) {
				return A2($author$project$PreviewPresenter$inputRealmOwned, scoped, decoded) ? $elm$core$Result$Ok(decoded) : $elm$core$Result$Err(
					A2($elm$json$Json$Decode$Failure, 'Original native realm owns the inner event', raw));
			},
			A2($elm$json$Json$Decode$decodeValue, $author$project$PreviewPresenter$input, raw));
		if (_v0.$ === 1) {
			return _Utils_Tuple2(
				prior,
				$author$project$PreviewPresenter$encode(_List_Nil));
		} else {
			switch (_v0.a.$) {
				case 9:
					var seed = _v0.a.a;
					var own = A2(
						$elm$core$Maybe$withDefault,
						false,
						A2(
							$elm$core$Maybe$map,
							function (grant) {
								return A2($author$project$NativePreviewRealm$same, grant.aT, seed.aT);
							},
							scoped.r));
					var identity = 'family:' + $author$project$UInt64$string(seed.aA);
					if ((!own) || scoped.N) {
						return _Utils_Tuple2(
							prior,
							$author$project$PreviewPresenter$encode(_List_Nil));
					} else {
						var _v1 = A2($elm$core$Dict$get, identity, entries);
						if (_v1.$ === 1) {
							return _Utils_Tuple2(
								prior,
								$author$project$PreviewPresenter$encode(_List_Nil));
						} else {
							var entry = _v1.a;
							if ((!_Utils_eq(
								entry.g,
								$author$project$NativePreviewRealm$owner(seed.aT))) || ((!_Utils_eq(entry.t, $elm$core$Maybe$Nothing)) || ((!A2($author$project$PreviewPresenter$floorMatches, entry, seed)) || ((!_Utils_eq(entry.v, $elm$core$Maybe$Nothing)) && (!_Utils_eq(
								entry.v,
								$elm$core$Maybe$Just(seed))))))) {
								return _Utils_Tuple2(
									prior,
									$author$project$PreviewPresenter$encode(_List_Nil));
							} else {
								var _v2 = $author$project$PreviewPresenter$quarantineOwned(prior);
								var _v3 = _v2.a;
								var retained = _v3.a;
								var catalog = _v3.b;
								var held = _v3.c;
								var nextScoped = _v3.d;
								var cleanup = _v2.b;
								var updated = A3(
									$elm$core$Dict$update,
									identity,
									$elm$core$Maybe$map(
										function (row) {
											return _Utils_update(
												row,
												{
													v: $elm$core$Maybe$Just(seed)
												});
										}),
									retained);
								return _Utils_Tuple2(
									A4($author$project$PreviewPresenter$Model, updated, catalog, held, nextScoped),
									cleanup);
							}
						}
					}
				case 10:
					var delivery = _v0.a.a;
					var seed = delivery.bj;
					var own = A2(
						$elm$core$Maybe$withDefault,
						false,
						A2(
							$elm$core$Maybe$map,
							function (grant) {
								return A2($author$project$NativePreviewRealm$same, grant.aT, seed.aT);
							},
							scoped.r));
					var identity = 'family:' + $author$project$UInt64$string(seed.aA);
					var ack = A2(
						$elm$json$Json$Encode$list,
						function (value) {
							return value;
						},
						_List_fromArray(
							[
								$elm$json$Json$Encode$object(
								_List_fromArray(
									[
										_Utils_Tuple2(
										'identity',
										$elm$json$Json$Encode$string(identity)),
										_Utils_Tuple2(
										'commands',
										A2(
											$elm$json$Json$Encode$list,
											function (value) {
												return value;
											},
											_List_fromArray(
												[
													$author$project$NativePreviewDetachment$acknowledgment(delivery)
												])))
									]))
							]));
					if ((!own) || scoped.N) {
						return _Utils_Tuple2(
							prior,
							$author$project$PreviewPresenter$encode(_List_Nil));
					} else {
						if (A2($author$project$UInt64$compare, delivery.b0, scoped.b7) !== 2) {
							return _Utils_eq(
								A2($elm$core$Dict$get, identity, scoped.W),
								$elm$core$Maybe$Just(
									_Utils_Tuple2(delivery.b0, seed))) ? _Utils_Tuple2(prior, ack) : _Utils_Tuple2(
								prior,
								$author$project$PreviewPresenter$encode(_List_Nil));
						} else {
							if (!_Utils_eq(
								$author$project$UInt64$next(scoped.b7),
								$elm$core$Maybe$Just(delivery.b0))) {
								return _Utils_Tuple2(
									prior,
									$author$project$PreviewPresenter$encode(_List_Nil));
							} else {
								var _v4 = A2($elm$core$Dict$get, identity, entries);
								if (_v4.$ === 1) {
									return _Utils_Tuple2(
										prior,
										$author$project$PreviewPresenter$encode(_List_Nil));
								} else {
									var entry = _v4.a;
									return ((!_Utils_eq(entry.t, $elm$core$Maybe$Nothing)) || ((!entry.aD) || ((!_Utils_eq(
										entry.v,
										$elm$core$Maybe$Just(seed))) || ((!A2($author$project$PreviewPresenter$floorMatches, entry, seed)) || ((!A2(
										$elm$core$Maybe$withDefault,
										true,
										A2($elm$core$Maybe$map, $author$project$PreviewLifecycle$settled, entry.d))) || ($elm$core$Dict$size(scoped.W) >= 256)))))) ? _Utils_Tuple2(
										prior,
										$author$project$PreviewPresenter$encode(_List_Nil)) : _Utils_Tuple2(
										A4(
											$author$project$PreviewPresenter$Model,
											A2($elm$core$Dict$remove, identity, entries),
											previousCatalog,
											ledger,
											_Utils_update(
												scoped,
												{
													W: A3(
														$elm$core$Dict$insert,
														identity,
														_Utils_Tuple2(delivery.b0, seed),
														scoped.W),
													b7: delivery.b0
												})),
										ack);
								}
							}
						}
					}
				case 7:
					var owner = _v0.a.a;
					var known = ((!$elm$core$Dict$isEmpty(entries)) || A2(
						$elm$core$Maybe$withDefault,
						false,
						A2(
							$elm$core$Maybe$map,
							function (catalog) {
								return _Utils_eq(catalog.g, owner);
							},
							previousCatalog))) && A2(
						$elm$core$List$all,
						function (entry) {
							return _Utils_eq(entry.g, owner);
						},
						$elm$core$Dict$values(entries));
					return _Utils_eq(
						ledger.bJ,
						$elm$core$Maybe$Just(owner)) ? _Utils_Tuple2(
						prior,
						$author$project$PreviewPresenter$encode(_List_Nil)) : (((!_Utils_eq(ledger.bJ, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(ledger.bd, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(ledger.aN, $elm$core$Maybe$Nothing)) || (!known)))) ? _Utils_Tuple2(
						prior,
						$author$project$PreviewPresenter$encode(_List_Nil)) : _Utils_Tuple2(
						A4(
							$author$project$PreviewPresenter$Model,
							entries,
							previousCatalog,
							_Utils_update(
								ledger,
								{
									bJ: $elm$core$Maybe$Just(owner)
								}),
							scoped),
						$author$project$PreviewPresenter$encode(_List_Nil)));
				case 8:
					var delivery = _v0.a.a;
					var fact = delivery.bP;
					var identity = 'family:' + $author$project$UInt64$string(fact.j.aA);
					var acknowledge = A2(
						$elm$json$Json$Encode$list,
						function (value) {
							return value;
						},
						_List_fromArray(
							[
								$elm$json$Json$Encode$object(
								_List_fromArray(
									[
										_Utils_Tuple2(
										'identity',
										$elm$json$Json$Encode$string(identity)),
										_Utils_Tuple2(
										'commands',
										A2(
											$elm$json$Json$Encode$list,
											function (value) {
												return value;
											},
											_List_fromArray(
												[
													$author$project$NativeActorRetirement$deliveryAcknowledgment(delivery)
												])))
									]))
							]));
					if (!_Utils_eq(
						ledger.bJ,
						$elm$core$Maybe$Just(
							$author$project$NativeActorRetirement$owner(fact.j)))) {
						return _Utils_Tuple2(
							prior,
							$author$project$PreviewPresenter$encode(_List_Nil));
					} else {
						if (A2($author$project$UInt64$compare, delivery.b0, ledger.b7) !== 2) {
							return _Utils_Tuple2(prior, acknowledge);
						} else {
							if (!_Utils_eq(
								$author$project$UInt64$next(ledger.b7),
								$elm$core$Maybe$Just(delivery.b0))) {
								return _Utils_Tuple2(
									prior,
									$author$project$PreviewPresenter$encode(_List_Nil));
							} else {
								var _v5 = A2($elm$core$Dict$get, identity, entries);
								if (_v5.$ === 1) {
									return _Utils_Tuple2(
										prior,
										$author$project$PreviewPresenter$encode(_List_Nil));
								} else {
									var entry = _v5.a;
									var settled = A2(
										$elm$core$Maybe$withDefault,
										true,
										A2($elm$core$Maybe$map, $author$project$PreviewLifecycle$settled, entry.d));
									var exact = A2(
										$elm$core$Maybe$withDefault,
										false,
										A2(
											$elm$core$Maybe$map,
											function (pending) {
												return A2($author$project$NativeActorRetirement$settles, pending, fact);
											},
											entry.t));
									if ((!entry.ab) || ((!settled) || ((!exact) || (!A2($author$project$NativeActorRetirement$coherentFrontier, ledger, fact))))) {
										return _Utils_Tuple2(
											prior,
											$author$project$PreviewPresenter$encode(_List_Nil));
									} else {
										var confirmed = A2($author$project$NativeActorRetirement$confirm, ledger, fact);
										return _Utils_Tuple2(
											A4(
												$author$project$PreviewPresenter$Model,
												A2($elm$core$Dict$remove, identity, entries),
												previousCatalog,
												_Utils_update(
													confirmed,
													{b7: delivery.b0}),
												scoped),
											acknowledge);
									}
								}
							}
						}
					}
				case 5:
					var observation = _v0.a.a;
					var identity = 'family:' + $author$project$UInt64$string(observation.aA);
					var _v6 = A2($elm$core$Dict$get, identity, entries);
					if (_v6.$ === 1) {
						return _Utils_Tuple2(
							prior,
							$author$project$PreviewPresenter$encode(_List_Nil));
					} else {
						var entry = _v6.a;
						if (((!_Utils_eq(ledger.bJ, $elm$core$Maybe$Nothing)) && (!_Utils_eq(
							ledger.bJ,
							$elm$core$Maybe$Just(
								$author$project$NativeActorRetirement$owner(observation))))) || ((!_Utils_eq(
							entry.g,
							$author$project$NativeActorRetirement$owner(observation))) || ((!_Utils_eq(entry.t, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(entry.v, $elm$core$Maybe$Nothing)) || (!A2(
							$elm$core$Maybe$withDefault,
							true,
							A2(
								$elm$core$Maybe$map,
								function (lifecycle) {
									return A2(
										$elm$core$Result$withDefault,
										false,
										A2(
											$elm$core$Result$map,
											$author$project$NativeActorRetirement$scopeBefore(observation),
											A2(
												$elm$json$Json$Decode$decodeValue,
												A2($elm$json$Json$Decode$field, 'scope', $elm$json$Json$Decode$value),
												$author$project$PreviewLifecycle$observe(lifecycle))));
								},
								entry.d))))))) {
							return _Utils_Tuple2(
								prior,
								$author$project$PreviewPresenter$encode(_List_Nil));
						} else {
							var _v7 = $author$project$PreviewPresenter$retireEntry(entry);
							var closed = _v7.a;
							var commands = _v7.b;
							var pending = _Utils_update(
								closed,
								{
									ab: false,
									t: $elm$core$Maybe$Just(observation)
								});
							return _Utils_Tuple2(
								A4(
									$author$project$PreviewPresenter$Model,
									A3($elm$core$Dict$insert, identity, pending, entries),
									previousCatalog,
									A2($author$project$NativeActorRetirement$remember, ledger, observation),
									scoped),
								$author$project$PreviewPresenter$encode(
									_List_fromArray(
										[
											{V: commands, aG: identity}
										])));
						}
					}
				case 6:
					var fact = _v0.a.a;
					var identity = 'family:' + $author$project$UInt64$string(fact.j.aA);
					var _v8 = A2($elm$core$Dict$get, identity, entries);
					if (_v8.$ === 1) {
						return _Utils_Tuple2(
							prior,
							$author$project$PreviewPresenter$encode(_List_Nil));
					} else {
						var entry = _v8.a;
						var settled = A2(
							$elm$core$Maybe$withDefault,
							true,
							A2($elm$core$Maybe$map, $author$project$PreviewLifecycle$settled, entry.d));
						var frontier = A2($author$project$NativeActorRetirement$coherentFrontier, ledger, fact);
						var exact = A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (pending) {
									return A2($author$project$NativeActorRetirement$settles, pending, fact);
								},
								entry.t));
						return ((!_Utils_eq(ledger.bJ, $elm$core$Maybe$Nothing)) || ((!entry.ab) || ((!settled) || ((!exact) || (!frontier))))) ? _Utils_Tuple2(
							prior,
							$author$project$PreviewPresenter$encode(_List_Nil)) : _Utils_Tuple2(
							A4(
								$author$project$PreviewPresenter$Model,
								A2($elm$core$Dict$remove, identity, entries),
								previousCatalog,
								A2($author$project$NativeActorRetirement$confirm, ledger, fact),
								scoped),
							$author$project$PreviewPresenter$encode(_List_Nil));
					}
				case 3:
					var _v9 = _v0.a;
					var stamp = _v9.a;
					var current = _v9.b;
					var rows = _v9.c;
					var ownersMatch = A2(
						$elm$core$List$all,
						function (entry) {
							return _Utils_eq(entry.g, current.g);
						},
						$elm$core$Dict$values(entries));
					var monotonic = A2(
						$elm$core$Maybe$withDefault,
						true,
						A2(
							$elm$core$Maybe$map,
							function (previous) {
								return _Utils_eq(current.g, previous.g) && ((A2($author$project$UInt64$compare, current.a_, previous.a_) === 2) && ((A2($author$project$UInt64$compare, current.ay, previous.ay) === 2) && (!(!A2($author$project$UInt64$compare, current.bh, previous.bh)))));
							},
							previousCatalog));
					var enroll = F2(
						function (row, next) {
							var identity = 'family:' + $author$project$UInt64$string(row.aA);
							var _v13 = A2($elm$core$Dict$get, identity, next);
							if (!_v13.$) {
								var entry = _v13.a;
								return (scoped.u || (A2($elm$core$Dict$member, identity, scoped.W) || ((!_Utils_eq(entry.d, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(entry.t, $elm$core$Maybe$Nothing)) || (!_Utils_eq(entry.v, $elm$core$Maybe$Nothing)))))) ? next : A3(
									$elm$core$Dict$insert,
									identity,
									_Utils_update(
										entry,
										{
											p: row.p,
											Y: $elm$core$Maybe$Just(current.a_),
											Z: $elm$core$Maybe$Just(row.Z),
											k: $elm$core$Maybe$Just(stamp),
											bD: row.bD
										}),
									next);
							} else {
								return (scoped.u || A2($elm$core$Dict$member, identity, scoped.W)) ? next : A3(
									$elm$core$Dict$insert,
									identity,
									{
										p: row.p,
										g: current.g,
										aD: false,
										v: $elm$core$Maybe$Nothing,
										ad: $elm$core$Maybe$Nothing,
										bq: $elm$core$Maybe$Nothing,
										aq: 'unavailable',
										m: $elm$core$Maybe$Nothing,
										Y: $elm$core$Maybe$Just(current.a_),
										Z: $elm$core$Maybe$Just(row.Z),
										d: $elm$core$Maybe$Nothing,
										ab: false,
										t: $elm$core$Maybe$Nothing,
										aP: $elm$core$Maybe$Nothing,
										k: $elm$core$Maybe$Just(stamp),
										bD: row.bD
									},
									next);
							}
						});
					var allowed = A2(
						$elm$core$Maybe$withDefault,
						false,
						A2(
							$elm$core$Maybe$map,
							$author$project$PreviewPresenter$same(stamp),
							snapshot));
					var admitted = A2(
						$elm$core$List$filter,
						function (row) {
							return A2(
								$elm$core$Maybe$withDefault,
								false,
								A2(
									$elm$core$Maybe$map,
									A2(
										$author$project$SurfaceRenderer$enabled,
										true,
										'family:' + $author$project$UInt64$string(row.aA)),
									snapshot));
						},
						rows);
					var identities = $elm$core$Set$fromList(
						A2(
							$elm$core$List$map,
							A2(
								$elm$core$Basics$composeR,
								function ($) {
									return $.aA;
								},
								A2(
									$elm$core$Basics$composeR,
									$author$project$UInt64$string,
									$elm$core$Basics$append('family:'))),
							admitted));
					var prune = F3(
						function (identity, entry, _v12) {
							var next = _v12.a;
							var outputs = _v12.b;
							if (A2($elm$core$Set$member, identity, identities)) {
								return _Utils_Tuple2(
									A3($elm$core$Dict$insert, identity, entry, next),
									outputs);
							} else {
								var _v11 = $author$project$PreviewPresenter$closeEntry(entry);
								var closed = _v11.a;
								var commands = _v11.b;
								return _Utils_Tuple2(
									((!scoped.u) && (_Utils_eq(closed.d, $elm$core$Maybe$Nothing) && (_Utils_eq(closed.t, $elm$core$Maybe$Nothing) && _Utils_eq(closed.v, $elm$core$Maybe$Nothing)))) ? next : A3($elm$core$Dict$insert, identity, closed, next),
									_Utils_ap(
										outputs,
										_List_fromArray(
											[
												{V: commands, aG: identity}
											])));
							}
						});
					var _v10 = A3(
						$elm$core$Dict$foldl,
						prune,
						_Utils_Tuple2($elm$core$Dict$empty, _List_Nil),
						entries);
					var retained = _v10.a;
					var cleanup = _v10.b;
					var enrolled = A3($elm$core$List$foldl, enroll, retained, admitted);
					return ((!allowed) || ((!monotonic) || ((!ownersMatch) || (A2(
						$elm$core$Maybe$withDefault,
						false,
						A2(
							$elm$core$Maybe$map,
							function (_final) {
								return A2($author$project$UInt64$compare, current.a_, _final.j.a_) !== 2;
							},
							ledger.aN)) || ($elm$core$Dict$size(enrolled) > 2051))))) ? _Utils_Tuple2(
						prior,
						$author$project$PreviewPresenter$encode(_List_Nil)) : _Utils_Tuple2(
						A4(
							$author$project$PreviewPresenter$Model,
							enrolled,
							$elm$core$Maybe$Just(current),
							ledger,
							scoped),
						$author$project$PreviewPresenter$encode(cleanup));
				case 1:
					var _v14 = _v0.a;
					var identity = _v14.a;
					var owner = _v14.b;
					var subject = _v14.c;
					var revision = _v14.d;
					var title = _v14.e;
					var application = _v14.f;
					var icon = _v14.g;
					var iconKind = _v14.h;
					var _v15 = A2($elm$core$Dict$get, identity, entries);
					if (!_v15.$) {
						var entry = _v15.a;
						return (scoped.u || ((!_Utils_eq(
							identity,
							'family:' + $author$project$UInt64$string(subject))) || ((!_Utils_eq(entry.g, owner)) || ((!_Utils_eq(entry.t, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(entry.v, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(
							_Utils_eq(icon, $elm$core$Maybe$Nothing),
							iconKind === 'unavailable')) || A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (previous) {
									return A2($author$project$UInt64$compare, revision, previous) !== 2;
								},
								entry.Y)))))))) ? _Utils_Tuple2(
							prior,
							$author$project$PreviewPresenter$encode(_List_Nil)) : _Utils_Tuple2(
							A4(
								$author$project$PreviewPresenter$Model,
								A3(
									$elm$core$Dict$insert,
									identity,
									_Utils_update(
										entry,
										{
											p: application,
											bq: icon,
											aq: iconKind,
											Y: $elm$core$Maybe$Just(revision),
											bD: title
										}),
									entries),
								previousCatalog,
								ledger,
								scoped),
							$author$project$PreviewPresenter$encode(_List_Nil));
					} else {
						return _Utils_Tuple2(
							prior,
							$author$project$PreviewPresenter$encode(_List_Nil));
					}
				case 4:
					var _v16 = _v0.a;
					var identity = _v16.a;
					var local = _v16.b;
					var _v17 = A2($elm$core$Dict$get, identity, entries);
					if (_v17.$ === 1) {
						return _Utils_Tuple2(
							prior,
							$author$project$PreviewPresenter$encode(_List_Nil));
					} else {
						var entry = _v17.a;
						var scopeMatches = A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (lifecycle) {
									return $author$project$PreviewLifecycle$idle(lifecycle) && _Utils_eq(
										A2(
											$elm$json$Json$Decode$decodeValue,
											A2(
												$elm$json$Json$Decode$at,
												_List_fromArray(
													['scope', 'clock']),
												$author$project$PreviewPresenter$positive),
											$author$project$PreviewLifecycle$observe(lifecycle)),
										$elm$core$Result$Ok(local.U));
								},
								entry.d));
						var newer = A2(
							$elm$core$Maybe$withDefault,
							true,
							A2(
								$elm$core$Maybe$map,
								function (floor) {
									return A2($author$project$UInt64$compare, local.ay, floor) === 2;
								},
								entry.ad));
						var current = A2(
							$elm$core$Maybe$withDefault,
							false,
							A2(
								$elm$core$Maybe$map,
								function (shown) {
									return A2($author$project$PreviewPresenter$same, local.k, shown) && A3($author$project$SurfaceRenderer$enabled, true, identity, shown);
								},
								snapshot));
						return (scoped.u || ((!current) || ((!scopeMatches) || ((!newer) || ((!_Utils_eq(entry.t, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(entry.v, $elm$core$Maybe$Nothing)) || ((!_Utils_eq(entry.g, local.b2)) || (!_Utils_eq(
							identity,
							'family:' + $author$project$UInt64$string(local.aA)))))))))) ? _Utils_Tuple2(
							prior,
							$author$project$PreviewPresenter$encode(_List_Nil)) : _Utils_Tuple2(
							A4(
								$author$project$PreviewPresenter$Model,
								A3(
									$elm$core$Dict$insert,
									identity,
									_Utils_update(
										entry,
										{
											ad: $elm$core$Maybe$Just(local.ay),
											m: $elm$core$Maybe$Just(local),
											k: $elm$core$Maybe$Just(local.k)
										}),
									entries),
								previousCatalog,
								ledger,
								scoped),
							$author$project$PreviewPresenter$encode(_List_Nil));
					}
				case 2:
					var _v18 = _v0.a;
					var identity = _v18.a;
					var event = _v18.b;
					var wire = _v18.c;
					var _v19 = A2($elm$core$Dict$get, identity, entries);
					if (_v19.$ === 1) {
						return _Utils_Tuple2(
							prior,
							$author$project$PreviewPresenter$encode(_List_Nil));
					} else {
						var entry = _v19.a;
						if (entry.ab || ((!(A2($author$project$PreviewPresenter$eventOwns, identity, wire) && A2($author$project$PreviewPresenter$familyFrameOwns, entry.aP, wire))) || ((scoped.u || ((!_Utils_eq(entry.t, $elm$core$Maybe$Nothing)) || (!_Utils_eq(entry.v, $elm$core$Maybe$Nothing)))) && A2(
							$elm$core$Result$withDefault,
							true,
							A2(
								$elm$core$Result$map,
								function (kind) {
									return A2(
										$elm$core$List$member,
										kind,
										_List_fromArray(
											['open', 'request', 'attach', 'observe']));
								},
								A2(
									$elm$json$Json$Decode$decodeValue,
									A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
									wire)))))) {
							return _Utils_Tuple2(
								prior,
								$author$project$PreviewPresenter$encode(_List_Nil));
						} else {
							var _v20 = entry.d;
							if (_v20.$ === 1) {
								return _Utils_Tuple2(
									prior,
									$author$project$PreviewPresenter$encode(_List_Nil));
							} else {
								var lifecycle = _v20.a;
								var _v21 = A2($author$project$PreviewLifecycle$update, event, lifecycle);
								var next = _v21.a;
								var commands = _v21.b;
								var owner = A2(
									$elm$core$Result$withDefault,
									entry.g,
									A2(
										$elm$json$Json$Decode$decodeValue,
										A2(
											$elm$json$Json$Decode$at,
											_List_fromArray(
												['scope', 'binding']),
											$author$project$PreviewPresenter$binding),
										$author$project$PreviewLifecycle$observe(next)));
								var updated = _Utils_eq(owner, entry.g) ? _Utils_update(
									entry,
									{
										m: $author$project$PreviewLifecycle$idle(next) ? entry.m : $elm$core$Maybe$Nothing,
										d: $elm$core$Maybe$Just(next)
									}) : _Utils_update(
									entry,
									{
										p: '',
										g: owner,
										ad: $elm$core$Maybe$Nothing,
										bq: $elm$core$Maybe$Nothing,
										aq: 'unavailable',
										m: $elm$core$Maybe$Nothing,
										Y: $elm$core$Maybe$Nothing,
										d: $elm$core$Maybe$Just(next),
										bD: 'Preview unavailable'
									});
								return _Utils_Tuple2(
									A4(
										$author$project$PreviewPresenter$Model,
										A3($elm$core$Dict$insert, identity, updated, entries),
										previousCatalog,
										ledger,
										scoped),
									$author$project$PreviewPresenter$encode(
										_List_fromArray(
											[
												{V: commands, aG: identity}
											])));
							}
						}
					}
				default:
					var _v22 = _v0.a;
					var stamp = _v22.a;
					var identity = _v22.b;
					var scope = _v22.c;
					var _native = _v22.d;
					var title = _v22.e;
					var application = _v22.f;
					var owner = _v22.g;
					var sourceKind = _v22.h;
					var unissued = _v22.i;
					var sequence = _v22.j;
					var openEvent = A2(
						$elm$json$Json$Decode$decodeValue,
						$author$project$PreviewLifecycle$eventDecoder,
						$elm$json$Json$Encode$object(
							_List_fromArray(
								[
									_Utils_Tuple2(
									'kind',
									$elm$json$Json$Encode$string('open'))
								])));
					var old = A2($elm$core$Dict$get, identity, entries);
					var observeEvent = A2(
						$elm$json$Json$Decode$decodeValue,
						$author$project$PreviewLifecycle$eventDecoder,
						$elm$json$Json$Encode$object(
							_List_fromArray(
								[
									_Utils_Tuple2(
									'kind',
									$elm$json$Json$Encode$string('observe')),
									_Utils_Tuple2('scope', _native)
								])));
					var matching = A2(
						$elm$core$Maybe$withDefault,
						true,
						A2(
							$elm$core$Maybe$map,
							function (entry) {
								return (!scoped.u) && (_Utils_eq(entry.g, owner) && (_Utils_eq(entry.t, $elm$core$Maybe$Nothing) && (_Utils_eq(entry.v, $elm$core$Maybe$Nothing) && (_Utils_eq(entry.d, $elm$core$Maybe$Nothing) || (A2($author$project$PreviewPresenter$sameSourcePlane, entry.aP, sourceKind) && ((!unissued) || A2(
									$elm$core$Maybe$withDefault,
									true,
									A2($elm$core$Maybe$map, $author$project$PreviewLifecycle$idle, entry.d))))))));
							},
							old));
					var allowed = A2(
						$elm$core$Maybe$withDefault,
						false,
						A2(
							$elm$core$Maybe$map,
							function (shown) {
								return A2($author$project$PreviewPresenter$same, stamp, shown) && A3($author$project$SurfaceRenderer$enabled, true, identity, shown);
							},
							snapshot));
					if (scoped.u || ((!allowed) || ((!matching) || ((_Utils_eq(old, $elm$core$Maybe$Nothing) && (!A3($author$project$NativeActorRetirement$admittedAfter, ledger, owner, _native))) || (_Utils_eq(old, $elm$core$Maybe$Nothing) && ($elm$core$Dict$size(entries) >= 2051)))))) {
						return _Utils_Tuple2(
							prior,
							$author$project$PreviewPresenter$encode(_List_Nil));
					} else {
						var floor = A2(
							$elm$core$Maybe$andThen,
							function ($) {
								return $.ad;
							},
							old);
						var base = A2(
							$elm$core$Maybe$withDefault,
							$author$project$PreviewLifecycle$init(scope),
							A2(
								$elm$core$Maybe$andThen,
								function ($) {
									return $.d;
								},
								old));
						var _v23 = A2(
							$elm$core$Result$withDefault,
							_Utils_Tuple2(base, _List_Nil),
							A2(
								$elm$core$Result$map,
								function (event) {
									return A2($author$project$PreviewLifecycle$update, event, base);
								},
								observeEvent));
						var observed = _v23.a;
						var first = _v23.b;
						var _v24 = unissued ? _Utils_Tuple2(observed, _List_Nil) : A2(
							$elm$core$Result$withDefault,
							_Utils_Tuple2(observed, _List_Nil),
							A2(
								$elm$core$Result$map,
								function (event) {
									return A2($author$project$PreviewLifecycle$update, event, observed);
								},
								openEvent));
						var opened = _v24.a;
						var second = _v24.b;
						var entry = {
							p: A2(
								$elm$core$Maybe$withDefault,
								application,
								A2(
									$elm$core$Maybe$map,
									function ($) {
										return $.p;
									},
									old)),
							g: owner,
							aD: false,
							v: $elm$core$Maybe$Nothing,
							ad: unissued ? floor : A2($author$project$PreviewPresenter$advanceFloor, floor, sequence),
							bq: A2(
								$elm$core$Maybe$andThen,
								function ($) {
									return $.bq;
								},
								old),
							aq: A2(
								$elm$core$Maybe$withDefault,
								'unavailable',
								A2(
									$elm$core$Maybe$map,
									function ($) {
										return $.aq;
									},
									old)),
							m: unissued ? A2(
								$elm$core$Maybe$andThen,
								function ($) {
									return $.m;
								},
								old) : $elm$core$Maybe$Nothing,
							Y: A2(
								$elm$core$Maybe$andThen,
								function ($) {
									return $.Y;
								},
								old),
							Z: A2(
								$elm$core$Maybe$andThen,
								function ($) {
									return $.Z;
								},
								old),
							d: $elm$core$Maybe$Just(opened),
							ab: false,
							t: $elm$core$Maybe$Nothing,
							aP: sourceKind,
							k: $elm$core$Maybe$Just(stamp),
							bD: A2(
								$elm$core$Maybe$withDefault,
								title,
								A2(
									$elm$core$Maybe$map,
									function ($) {
										return $.bD;
									},
									old))
						};
						return _Utils_Tuple2(
							A4(
								$author$project$PreviewPresenter$Model,
								A3($elm$core$Dict$insert, identity, entry, entries),
								previousCatalog,
								ledger,
								scoped),
							$author$project$PreviewPresenter$encode(
								_List_fromArray(
									[
										{
										V: _Utils_ap(first, second),
										aG: identity
									}
									])));
					}
			}
		}
	});
var $author$project$PreviewPresenter$receiveOwned = F3(
	function (snapshot, raw, prior) {
		var settled = function (entry) {
			return A2(
				$elm$core$Maybe$withDefault,
				true,
				A2($elm$core$Maybe$map, $author$project$PreviewLifecycle$settled, entry.d));
		};
		var advance = F3(
			function (identity, entry, _v5) {
				var next = _v5.a;
				var ready = _v5.b;
				var _v3 = entry.t;
				if (!_v3.$) {
					var observation = _v3.a;
					return ((!entry.ab) && settled(entry)) ? _Utils_Tuple2(
						A3(
							$elm$core$Dict$insert,
							identity,
							_Utils_update(
								entry,
								{ab: true}),
							next),
						_Utils_ap(
							ready,
							_List_fromArray(
								[
									$elm$json$Json$Encode$object(
									_List_fromArray(
										[
											_Utils_Tuple2(
											'identity',
											$elm$json$Json$Encode$string(identity)),
											_Utils_Tuple2(
											'commands',
											A2(
												$elm$json$Json$Encode$list,
												function (command) {
													return command;
												},
												_List_fromArray(
													[
														$author$project$NativeActorRetirement$readyCommand(observation)
													])))
										]))
								]))) : _Utils_Tuple2(
						A3($elm$core$Dict$insert, identity, entry, next),
						ready);
				} else {
					var _v4 = entry.v;
					if (!_v4.$) {
						var seed = _v4.a;
						return ((!entry.aD) && (settled(entry) && A2($author$project$PreviewPresenter$floorMatches, entry, seed))) ? _Utils_Tuple2(
							A3(
								$elm$core$Dict$insert,
								identity,
								_Utils_update(
									entry,
									{aD: true}),
								next),
							_Utils_ap(
								ready,
								_List_fromArray(
									[
										$elm$json$Json$Encode$object(
										_List_fromArray(
											[
												_Utils_Tuple2(
												'identity',
												$elm$json$Json$Encode$string(identity)),
												_Utils_Tuple2(
												'commands',
												A2(
													$elm$json$Json$Encode$list,
													function (value) {
														return value;
													},
													_List_fromArray(
														[
															$author$project$NativePreviewDetachment$ready(seed)
														])))
											]))
									]))) : _Utils_Tuple2(
							A3($elm$core$Dict$insert, identity, entry, next),
							ready);
					} else {
						return _Utils_Tuple2(
							A3($elm$core$Dict$insert, identity, entry, next),
							ready);
					}
				}
			});
		var _v0 = A3($author$project$PreviewPresenter$receiveInput, snapshot, raw, prior);
		var _v1 = _v0.a;
		var entries = _v1.a;
		var catalog = _v1.b;
		var ledger = _v1.c;
		var scoped = _v1.d;
		var emitted = _v0.b;
		var cleanup = A2(
			$elm$core$Result$withDefault,
			_List_Nil,
			A2(
				$elm$json$Json$Decode$decodeValue,
				$elm$json$Json$Decode$list($elm$json$Json$Decode$value),
				emitted));
		var _v2 = A3(
			$elm$core$Dict$foldl,
			advance,
			_Utils_Tuple2($elm$core$Dict$empty, _List_Nil),
			entries);
		var retained = _v2.a;
		var barriers = _v2.b;
		return _Utils_Tuple2(
			A4($author$project$PreviewPresenter$Model, retained, catalog, ledger, scoped),
			A2(
				$elm$json$Json$Encode$list,
				$elm$core$Basics$identity,
				_Utils_ap(cleanup, barriers)));
	});
var $author$project$PreviewPresenter$receive = F3(
	function (snapshot, raw, prior) {
		var scoped = prior.d;
		return (!_Utils_eq(scoped.r, $elm$core$Maybe$Nothing)) ? _Utils_Tuple2(
			prior,
			$author$project$PreviewPresenter$encode(_List_Nil)) : A3($author$project$PreviewPresenter$receiveOwned, snapshot, raw, prior);
	});
var $author$project$RetainedPreviewPresenter$receive = F3(
	function (snapshot, raw, prior) {
		var policy = prior.a;
		return A2(
			$author$project$RetainedPreviewPresenter$commit,
			prior,
			A3($author$project$PreviewPresenter$receive, snapshot, raw, policy));
	});
var $author$project$NativePreviewRealm$unwrap = F2(
	function (current, _v0) {
		var domain = _v0.a;
		var event = _v0.b;
		return A2($author$project$NativePreviewRealm$same, current, domain) ? $elm$core$Maybe$Just(event) : $elm$core$Maybe$Nothing;
	});
var $author$project$PreviewPresenter$receiveRealm = F3(
	function (snapshot, raw, prior) {
		var scoped = prior.d;
		var _v0 = _Utils_Tuple2(
			scoped.r,
			A2($elm$json$Json$Decode$decodeValue, $author$project$NativePreviewRealm$envelopeDecoder, raw));
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var grant = _v0.a.a;
			var envelope = _v0.b.a;
			var _v1 = scoped.N ? $elm$core$Maybe$Nothing : A2($author$project$NativePreviewRealm$unwrap, grant.aT, envelope);
			if (_v1.$ === 1) {
				return _Utils_Tuple2(
					prior,
					A2(
						$author$project$PreviewPresenter$wrap,
						scoped,
						$author$project$PreviewPresenter$encode(_List_Nil)));
			} else {
				var event = _v1.a;
				var _v2 = A3($author$project$PreviewPresenter$receiveOwned, snapshot, event, prior);
				var next = _v2.a;
				var emitted = _v2.b;
				return _Utils_Tuple2(
					next,
					A2($author$project$PreviewPresenter$wrap, scoped, emitted));
			}
		} else {
			return _Utils_Tuple2(
				prior,
				A2(
					$author$project$PreviewPresenter$wrap,
					scoped,
					$author$project$PreviewPresenter$encode(_List_Nil)));
		}
	});
var $author$project$RetainedPreviewPresenter$receiveRealm = F3(
	function (snapshot, raw, prior) {
		var policy = prior.a;
		return A2(
			$author$project$RetainedPreviewPresenter$commit,
			prior,
			A3($author$project$PreviewPresenter$receiveRealm, snapshot, raw, policy));
	});
var $author$project$PreviewPresenter$retireLegacy = F2(
	function (raw, prior) {
		var entries = prior.a;
		var scoped = prior.d;
		var _v0 = A2($elm$json$Json$Decode$decodeValue, $author$project$PreviewPresenter$binding, raw);
		if (!_v0.$) {
			var owner = _v0.a;
			return (_Utils_eq(scoped.r, $elm$core$Maybe$Nothing) && A2(
				$elm$core$List$all,
				function (entry) {
					return _Utils_eq(entry.g, owner);
				},
				$elm$core$Dict$values(entries))) ? $author$project$PreviewPresenter$quarantineOwned(prior) : _Utils_Tuple2(
				prior,
				$author$project$PreviewPresenter$encode(_List_Nil));
		} else {
			return _Utils_Tuple2(
				prior,
				$author$project$PreviewPresenter$encode(_List_Nil));
		}
	});
var $author$project$RetainedPreviewPresenter$retireLegacy = F2(
	function (raw, prior) {
		var policy = prior.a;
		return A2(
			$author$project$RetainedPreviewPresenter$commit,
			prior,
			A2($author$project$PreviewPresenter$retireLegacy, raw, policy));
	});
var $author$project$RetainedPreviewPresenter$retry = F2(
	function (domain, prior) {
		var policy = prior.a;
		var grant = prior.b;
		var ingress = prior.c;
		var deferred = prior.d;
		var _v0 = _Utils_Tuple2(grant, ingress);
		if ((!_v0.a.$) && (!_v0.b.$)) {
			var g = _v0.a.a;
			var queue = _v0.b.a;
			if (A2($author$project$NativePreviewRealm$same, g.aT, domain)) {
				var _v1 = A2($author$project$NativePreviewProposalIngress$split, deferred, queue);
				var next = _v1.a;
				var waiting = _v1.b;
				return _Utils_Tuple2(
					A4(
						$author$project$RetainedPreviewPresenter$Model,
						policy,
						grant,
						$elm$core$Maybe$Just(next),
						waiting),
					$author$project$NativePreviewProposalIngress$proposals(next));
			} else {
				return _Utils_Tuple2(
					prior,
					$author$project$RetainedPreviewPresenter$emptyOutput(grant));
			}
		} else {
			return _Utils_Tuple2(
				prior,
				$author$project$RetainedPreviewPresenter$emptyOutput(grant));
		}
	});
var $author$project$Popup$update = F2(
	function (message, model) {
		switch (message.$) {
			case 1:
				var value = message.a;
				var sendQuery = F3(
					function (query, wire, current) {
						var unchanged = _Utils_eq(
							$elm$core$Maybe$Just(query),
							A2(
								$elm$core$Maybe$andThen,
								$author$project$SurfaceRenderer$queryValue,
								$author$project$Presentation$current(current.z)));
						var key = A2(
							$elm$core$Maybe$map,
							function (snapshot) {
								return _Utils_Tuple3(
									query,
									$author$project$SurfaceRenderer$publication(snapshot),
									$author$project$SurfaceRenderer$lease(snapshot));
							},
							$author$project$Presentation$current(current.z));
						var duplicate = (!_Utils_eq(key, $elm$core$Maybe$Nothing)) && _Utils_eq(key, current.as);
						return _Utils_Tuple2(
							_Utils_update(
								current,
								{
									as: key,
									y: unchanged ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(query)
								}),
							(unchanged || duplicate) ? $elm$core$Platform$Cmd$none : $author$project$Popup$actions(wire));
					});
				var kind = A2(
					$elm$core$Result$withDefault,
					'',
					A2(
						$elm$json$Json$Decode$decodeValue,
						A2($elm$json$Json$Decode$field, 'kind', $elm$json$Json$Decode$string),
						value));
				var before = {
					bo: A2(
						$elm$core$Maybe$withDefault,
						A2(
							$elm$core$Maybe$withDefault,
							'',
							A2(
								$elm$core$Maybe$andThen,
								$author$project$SurfaceRenderer$queryValue,
								$author$project$Presentation$current(model.z))),
						model.y),
					bp: model.y
				};
				if (A2(
					$elm$core$List$member,
					kind,
					_List_fromArray(
						['surface-query', 'surface-preedit', 'surface-composition-start', 'surface-composition-end']))) {
					var _v1 = A2($author$project$Presentation$editQuery, value, model.z);
					if (!_v1.$) {
						var _v2 = _v1.a;
						var query = _v2.a;
						var wire = _v2.b;
						if (kind === 'surface-composition-start') {
							return _Utils_Tuple2(
								_Utils_update(
									model,
									{
										L: $author$project$Popup$Preediting(
											{bo: query, bp: model.y}),
										y: $elm$core$Maybe$Just(query)
									}),
								$elm$core$Platform$Cmd$none);
						} else {
							if (kind === 'surface-composition-end') {
								var _v3 = model.L;
								if (!_v3.$) {
									return _Utils_Tuple2(model, $elm$core$Platform$Cmd$none);
								} else {
									var held = _v3.a;
									return _Utils_eq(query, held.bo) ? _Utils_Tuple2(
										_Utils_update(
											model,
											{
												L: $author$project$Popup$Idle,
												y: A2(
													$elm$core$Maybe$andThen,
													function (prior) {
														return _Utils_eq(
															A2(
																$elm$core$Maybe$andThen,
																$author$project$SurfaceRenderer$queryValue,
																$author$project$Presentation$current(model.z)),
															$elm$core$Maybe$Just(prior)) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(prior);
													},
													held.bp)
											}),
										$elm$core$Platform$Cmd$none) : A3(
										sendQuery,
										query,
										wire,
										_Utils_update(
											model,
											{L: $author$project$Popup$Idle}));
								}
							} else {
								if ((kind === 'surface-preedit') || $author$project$Popup$isComposing(model)) {
									return _Utils_Tuple2(
										_Utils_update(
											model,
											{
												L: $author$project$Popup$isComposing(model) ? model.L : $author$project$Popup$Preediting(before),
												y: $elm$core$Maybe$Just(query)
											}),
										$elm$core$Platform$Cmd$none);
								} else {
									return A3(sendQuery, query, wire, model);
								}
							}
						}
					} else {
						return _Utils_Tuple2(model, $elm$core$Platform$Cmd$none);
					}
				} else {
					if ($author$project$Popup$isComposing(model) || ((!_Utils_eq(model.y, $elm$core$Maybe$Nothing)) && A2(
						$elm$core$Result$withDefault,
						false,
						A2(
							$elm$core$Result$map,
							function (identity) {
								return A2($elm$core$String$startsWith, 'entry:', identity) || ((identity === 'files:open-path') || ((identity === 'files:home') || A2($elm$core$String$startsWith, 'files:collection:', identity)));
							},
							A2(
								$elm$json$Json$Decode$decodeValue,
								A2($elm$json$Json$Decode$field, 'id', $elm$json$Json$Decode$string),
								value))))) {
						return _Utils_Tuple2(model, $elm$core$Platform$Cmd$none);
					} else {
						return _Utils_Tuple2(
							model,
							A2(
								$elm$core$Maybe$withDefault,
								$elm$core$Platform$Cmd$none,
								A2(
									$elm$core$Maybe$map,
									$author$project$Popup$actions,
									A3($author$project$Presentation$dispatch, true, value, model.z))));
					}
				}
			case 0:
				var raw = message.a;
				var acceptedPresentation = A2($author$project$Presentation$accept, raw, model.z);
				var sameField = function () {
					var _v6 = _Utils_Tuple2(
						$author$project$Presentation$current(model.z),
						$author$project$Presentation$current(acceptedPresentation));
					if ((!_v6.a.$) && (!_v6.b.$)) {
						var old = _v6.a.a;
						var next = _v6.b.a;
						return A2(
							$elm$core$List$member,
							$author$project$SurfaceRenderer$mode(next),
							_List_fromArray(
								['applications', 'files'])) && (_Utils_eq(
							$author$project$SurfaceRenderer$mode(old),
							$author$project$SurfaceRenderer$mode(next)) && A3(
							$author$project$SurfaceRenderer$enabled,
							true,
							$author$project$SurfaceRenderer$fieldIdentity(next),
							next));
					} else {
						return false;
					}
				}();
				var composition = sameField ? model.L : $author$project$Popup$Idle;
				var composing = !_Utils_eq(composition, $author$project$Popup$Idle);
				var pending = (!sameField) ? $elm$core$Maybe$Nothing : (composing ? model.y : A2(
					$elm$core$Maybe$andThen,
					function (query) {
						var _v5 = $author$project$Presentation$current(acceptedPresentation);
						if (!_v5.$) {
							var snapshot = _v5.a;
							return (!_Utils_eq(
								$author$project$SurfaceRenderer$queryValue(snapshot),
								$elm$core$Maybe$Just(query))) ? $elm$core$Maybe$Just(query) : $elm$core$Maybe$Nothing;
						} else {
							return $elm$core$Maybe$Nothing;
						}
					},
					model.y));
				var key = A2(
					$elm$core$Maybe$andThen,
					function (query) {
						return A2(
							$elm$core$Maybe$map,
							function (snapshot) {
								return _Utils_Tuple3(
									query,
									$author$project$SurfaceRenderer$publication(snapshot),
									$author$project$SurfaceRenderer$lease(snapshot));
							},
							$author$project$Presentation$current(acceptedPresentation));
					},
					pending);
				var lastQuery = (!sameField) ? $elm$core$Maybe$Nothing : ((composing || _Utils_eq(pending, $elm$core$Maybe$Nothing)) ? model.as : key);
				var queryCommand = (composing || _Utils_eq(key, model.as)) ? $elm$core$Platform$Cmd$none : A2(
					$elm$core$Maybe$withDefault,
					$elm$core$Platform$Cmd$none,
					A2(
						$elm$core$Maybe$map,
						$author$project$Popup$actions,
						A2(
							$elm$core$Maybe$andThen,
							function (query) {
								return A2($author$project$Presentation$query, query, acceptedPresentation);
							},
							pending)));
				var _v4 = A2(
					$author$project$RetainedPreviewPresenter$present,
					$author$project$Presentation$current(acceptedPresentation),
					model.f);
				var previews = _v4.a;
				var commands = _v4.b;
				return _Utils_Tuple2(
					{L: composition, as: lastQuery, y: pending, z: acceptedPresentation, f: previews},
					$elm$core$Platform$Cmd$batch(
						_List_fromArray(
							[
								$author$project$Popup$previewCommands(commands),
								queryCommand
							])));
			case 2:
				var raw = message.a;
				var _v7 = function () {
					var _v8 = A2($elm$json$Json$Decode$decodeValue, $author$project$NativePreviewRealm$envelopeDecoder, raw);
					if (!_v8.$) {
						return A3(
							$author$project$RetainedPreviewPresenter$receiveRealm,
							$author$project$Presentation$current(model.z),
							raw,
							model.f);
					} else {
						return A3(
							$author$project$RetainedPreviewPresenter$receive,
							$author$project$Presentation$current(model.z),
							raw,
							model.f);
					}
				}();
				var previews = _v7.a;
				var commands = _v7.b;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{f: previews}),
					$author$project$Popup$previewCommands(commands));
			case 8:
				var raw = message.a;
				var _v9 = A2($author$project$RetainedPreviewPresenter$retireLegacy, raw, model.f);
				var previews = _v9.a;
				var commands = _v9.b;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{f: previews}),
					$author$project$Popup$previewCommands(commands));
			case 3:
				var raw = message.a;
				var previews = A2(
					$elm$core$Maybe$withDefault,
					model.f,
					A2(
						$elm$core$Maybe$andThen,
						function (grant) {
							return A2($author$project$RetainedPreviewPresenter$enrollRealm, grant, model.f);
						},
						$elm$core$Result$toMaybe(
							A2($elm$json$Json$Decode$decodeValue, $author$project$NativePreviewRealm$grantDecoder, raw))));
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{f: previews}),
					$elm$core$Platform$Cmd$none);
			case 4:
				var raw = message.a;
				var _v10 = A2(
					$elm$core$Result$withDefault,
					_Utils_Tuple2(
						model.f,
						A2($elm$json$Json$Encode$list, $elm$core$Basics$identity, _List_Nil)),
					A2(
						$elm$core$Result$map,
						function (domain) {
							return A2($author$project$RetainedPreviewPresenter$quarantineRealm, domain, model.f);
						},
						A2($elm$json$Json$Decode$decodeValue, $author$project$NativePreviewRealm$domainDecoder, raw)));
				var previews = _v10.a;
				var commands = _v10.b;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{f: previews}),
					$author$project$Popup$previewCommands(commands));
			case 6:
				var raw = message.a;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{
							f: A2($author$project$RetainedPreviewPresenter$issued, raw, model.f)
						}),
					$elm$core$Platform$Cmd$none);
			case 7:
				var raw = message.a;
				var _v11 = A2(
					$elm$core$Result$withDefault,
					_Utils_Tuple2(
						model.f,
						A2($elm$json$Json$Encode$list, $elm$core$Basics$identity, _List_Nil)),
					A2(
						$elm$core$Result$map,
						function (domain) {
							return A2($author$project$RetainedPreviewPresenter$retry, domain, model.f);
						},
						A2($elm$json$Json$Decode$decodeValue, $author$project$NativePreviewRealm$domainDecoder, raw)));
				var previews = _v11.a;
				var commands = _v11.b;
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{f: previews}),
					$author$project$Popup$previewCommands(commands));
			default:
				var raw = message.a;
				var previews = A2(
					$elm$core$Maybe$withDefault,
					model.f,
					A2(
						$elm$core$Maybe$andThen,
						function (domain) {
							return A2($author$project$RetainedPreviewPresenter$closeRealm, domain, model.f);
						},
						$elm$core$Result$toMaybe(
							A2($elm$json$Json$Decode$decodeValue, $author$project$NativePreviewRealm$domainDecoder, raw))));
				return _Utils_Tuple2(
					_Utils_update(
						model,
						{f: previews}),
					$elm$core$Platform$Cmd$none);
		}
	});
var $elm$html$Html$button = _VirtualDom_node('button');
var $elm$html$Html$Attributes$stringProperty = F2(
	function (key, string) {
		return A2(
			_VirtualDom_property,
			key,
			$elm$json$Json$Encode$string(string));
	});
var $elm$html$Html$Attributes$class = $elm$html$Html$Attributes$stringProperty('className');
var $author$project$PreviewVisual$Hidden = {$: 0};
var $elm$html$Html$Attributes$alt = $elm$html$Html$Attributes$stringProperty('alt');
var $author$project$PreviewVisual$Family = 1;
var $author$project$PreviewVisual$fidelityLabel = function (fidelity) {
	return (fidelity === 1) ? 'Window family' : 'Client content';
};
var $elm$html$Html$img = _VirtualDom_node('img');
var $author$project$PreviewVisual$localLabel = function (state) {
	switch (state) {
		case 0:
			return 'Waiting for preview capacity';
		case 1:
			return 'Waiting for preview';
		case 2:
			return 'Preview request expired';
		case 3:
			return 'Preview request changed';
		default:
			return 'Preview unavailable';
	}
};
var $author$project$PreviewVisual$localName = function (state) {
	switch (state) {
		case 0:
			return 'capacity';
		case 1:
			return 'waiting';
		case 2:
			return 'expired';
		case 3:
			return 'conflict';
		default:
			return 'exhausted';
	}
};
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
var $author$project$PreviewVisual$stateLabel = function (state) {
	switch (state) {
		case 0:
			return 'Live preview';
		case 1:
			return 'Historical preview';
		case 2:
			return 'Preview loading';
		default:
			return 'Preview unavailable';
	}
};
var $author$project$PreviewVisual$stateName = function (state) {
	switch (state) {
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
var $author$project$PreviewVisual$render = F3(
	function (root, caption, visual) {
		switch (visual.$) {
			case 0:
				return $elm$html$Html$text('');
			case 1:
				return A2(
					$elm$html$Html$span,
					_List_fromArray(
						[
							$elm$html$Html$Attributes$class('window-preview'),
							A2($elm$html$Html$Attributes$attribute, 'data-preview-state', 'unavailable')
						]),
					_List_fromArray(
						[
							A2(
							$elm$html$Html$span,
							_List_fromArray(
								[
									$elm$html$Html$Attributes$class('preview-title')
								]),
							_List_Nil),
							A2(
							$elm$html$Html$span,
							_List_fromArray(
								[
									$elm$html$Html$Attributes$class('preview-state')
								]),
							_List_fromArray(
								[
									$elm$html$Html$text('Preview unavailable')
								]))
						]));
			case 2:
				var state = visual.a;
				var title = visual.b;
				return A2(
					$elm$html$Html$span,
					_List_fromArray(
						[
							$elm$html$Html$Attributes$class('window-preview'),
							A2(
							$elm$html$Html$Attributes$attribute,
							'data-preview-state',
							$author$project$PreviewVisual$localName(state))
						]),
					_List_fromArray(
						[
							A2(
							$elm$html$Html$span,
							_List_fromArray(
								[
									$elm$html$Html$Attributes$class('preview-title')
								]),
							_List_fromArray(
								[
									$elm$html$Html$text(
									_Utils_eq(
										title,
										$author$project$PreviewVisual$localLabel(state)) ? '' : title)
								])),
							A2(
							$elm$html$Html$span,
							_List_fromArray(
								[
									$elm$html$Html$Attributes$class('preview-state')
								]),
							_List_fromArray(
								[
									$elm$html$Html$text(
									$author$project$PreviewVisual$localLabel(state))
								]))
						]));
			default:
				var data = visual.a;
				var fidelity = A2(
					$elm$core$Maybe$withDefault,
					'',
					A2($elm$core$Maybe$map, $author$project$PreviewVisual$fidelityLabel, data.aF));
				var contents = function () {
					var _v1 = data.bS;
					if (!_v1.$) {
						var handle = _v1.a;
						return _List_fromArray(
							[
								_Utils_Tuple2(
								'frame:' + handle,
								A2(
									$elm$html$Html$img,
									_List_fromArray(
										[
											$elm$html$Html$Attributes$class('preview-image'),
											$elm$html$Html$Attributes$src('elm-shell://preview/' + handle),
											$elm$html$Html$Attributes$alt(''),
											A2($elm$html$Html$Attributes$attribute, 'aria-hidden', 'true')
										]),
									_List_Nil))
							]);
					} else {
						return _Utils_ap(
							A2(
								$elm$core$Maybe$withDefault,
								_List_Nil,
								A2(
									$elm$core$Maybe$map,
									function (handle) {
										return _List_fromArray(
											[
												_Utils_Tuple2(
												'icon:' + handle,
												A2(
													$elm$html$Html$img,
													_List_fromArray(
														[
															$elm$html$Html$Attributes$class('preview-icon'),
															$elm$html$Html$Attributes$src('elm-shell://icon/' + handle),
															$elm$html$Html$Attributes$alt(''),
															A2($elm$html$Html$Attributes$attribute, 'aria-hidden', 'true')
														]),
													_List_Nil))
											]);
									},
									data.bq)),
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
												$elm$html$Html$text(
												A2(
													$elm$core$Maybe$withDefault,
													'',
													A2(
														$elm$core$Maybe$andThen,
														function (title) {
															return _Utils_eq(
																title,
																$author$project$PreviewVisual$stateLabel(data.i)) ? $elm$core$Maybe$Nothing : $elm$core$Maybe$Just(title);
														},
														data.bD)))
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
							$author$project$PreviewVisual$stateName(data.i))
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
													$elm$html$Html$text(
													$author$project$PreviewVisual$stateLabel(data.i))
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
		}
	});
var $author$project$PreviewVisual$inlineView = A2($author$project$PreviewVisual$render, 'span', 'span');
var $author$project$PreviewVisual$decorativeInlineView = function (visual) {
	return _Utils_eq(visual, $author$project$PreviewVisual$Hidden) ? $elm$html$Html$text('') : A2(
		$elm$html$Html$span,
		_List_fromArray(
			[
				$elm$html$Html$Attributes$class('preview-content'),
				A2($elm$html$Html$Attributes$attribute, 'aria-hidden', 'true')
			]),
		_List_fromArray(
			[
				$author$project$PreviewVisual$inlineView(visual)
			]));
};
var $author$project$PreviewVisual$Unavailable = 3;
var $elm$core$List$singleton = function (value) {
	return _List_fromArray(
		[value]);
};
var $author$project$PreviewVisual$description = function (visual) {
	switch (visual.$) {
		case 0:
			return '';
		case 1:
			return $author$project$PreviewVisual$stateLabel(3);
		case 2:
			var state = visual.a;
			return $author$project$PreviewVisual$localLabel(state);
		default:
			var data = visual.a;
			return A2(
				$elm$core$String$join,
				'; ',
				A2(
					$elm$core$List$cons,
					$author$project$PreviewVisual$stateLabel(data.i),
					A2(
						$elm$core$Maybe$withDefault,
						_List_Nil,
						A2(
							$elm$core$Maybe$map,
							A2($elm$core$Basics$composeR, $author$project$PreviewVisual$fidelityLabel, $elm$core$List$singleton),
							data.aF))));
	}
};
var $elm$html$Html$Attributes$boolProperty = F2(
	function (key, bool) {
		return A2(
			_VirtualDom_property,
			key,
			$elm$json$Json$Encode$bool(bool));
	});
var $elm$html$Html$Attributes$disabled = $elm$html$Html$Attributes$boolProperty('disabled');
var $elm$core$String$endsWith = _String_endsWith;
var $elm$html$Html$h1 = _VirtualDom_node('h1');
var $elm$html$Html$Attributes$hidden = $elm$html$Html$Attributes$boolProperty('hidden');
var $elm$html$Html$Attributes$id = $elm$html$Html$Attributes$stringProperty('id');
var $elm$html$Html$input = _VirtualDom_node('input');
var $elm$virtual_dom$VirtualDom$Normal = function (a) {
	return {$: 0, a: a};
};
var $elm$virtual_dom$VirtualDom$on = _VirtualDom_on;
var $elm$html$Html$Events$on = F2(
	function (event, decoder) {
		return A2(
			$elm$virtual_dom$VirtualDom$on,
			event,
			$elm$virtual_dom$VirtualDom$Normal(decoder));
	});
var $elm$html$Html$p = _VirtualDom_node('p');
var $elm$html$Html$Attributes$placeholder = $elm$html$Html$Attributes$stringProperty('placeholder');
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
var $elm$html$Html$Attributes$title = $elm$html$Html$Attributes$stringProperty('title');
var $elm$html$Html$Attributes$type_ = $elm$html$Html$Attributes$stringProperty('type');
var $elm$html$Html$Attributes$value = $elm$html$Html$Attributes$stringProperty('value');
var $author$project$SurfaceRenderer$viewWithPreview = F4(
	function (preview, popup, send, current) {
		var snapshot = current;
		var familyPrefix = function (rows) {
			if (rows.b) {
				var first = rows.a;
				var rest = rows.b;
				return A2($elm$core$String$startsWith, 'overview:family:', first.aG) ? A2(
					$elm$core$List$cons,
					first,
					familyPrefix(rest)) : _List_Nil;
			} else {
				return _List_Nil;
			}
		};
		var domIds = $elm$core$Set$fromList(
			A2(
				$elm$core$List$map,
				function ($) {
					return $.C;
				},
				_Utils_ap(snapshot.K, snapshot.n)));
		var prefix = function (candidate) {
			prefix:
			while (true) {
				if (A2(
					$elm$core$List$any,
					function (item) {
						return A2(
							$elm$core$Set$member,
							_Utils_ap(candidate, item.C),
							domIds);
					},
					_Utils_ap(snapshot.K, snapshot.n))) {
					var $temp$candidate = candidate + '-';
					candidate = $temp$candidate;
					continue prefix;
				} else {
					return candidate;
				}
			}
		};
		var descriptionPrefix = prefix('preview-description-');
		var control = function (item) {
			var visual = preview(item.aG);
			var switcherOption = popup && ((snapshot.c === 'switcher') && A2($elm$core$String$startsWith, 'switcher:family:', item.aG));
			var settingsToggle = popup && ((snapshot.c === 'settings') && A2(
				$elm$core$List$member,
				item.aG,
				_List_fromArray(
					['settings:effects-off', 'settings:reduced-transparency'])));
			var kind = (A2($elm$core$String$startsWith, 'bar:group:', item.aG) || A2($elm$core$String$startsWith, 'bar:pin:', item.aG)) ? 'control-group' : ((item.aG === 'bar:recovery-refresh') ? 'control-recovery' : 'control-utility');
			var descriptionId = _Utils_ap(descriptionPrefix, item.C);
			var description = $author$project$PreviewVisual$description(visual);
			var active = (!popup) && ((A2($elm$core$String$startsWith, 'bar:group:', item.aG) || A2($elm$core$String$startsWith, 'bar:pin:', item.aG)) && (A2($elm$core$String$contains, 'Active', item.q) && (!A2($elm$core$String$contains, 'Attention; ', item.q))));
			if (popup && ((snapshot.c === 'settings') && (A2($elm$core$String$startsWith, 'settings:help:text:', item.aG) || (A2($elm$core$String$startsWith, 'settings:shortcuts:', item.aG) && A2($elm$core$String$endsWith, ':state', item.aG))))) {
				return A2(
					$elm$html$Html$p,
					_List_fromArray(
						[
							$elm$html$Html$Attributes$class('notification-text'),
							$elm$html$Html$Attributes$id(item.C),
							A2(
							$elm$html$Html$Attributes$attribute,
							A2($elm$core$String$startsWith, 'settings:help:text:', item.aG) ? 'data-settings-help' : 'data-shortcut-state',
							item.aG)
						]),
					_List_fromArray(
						[
							A2(
							$elm$html$Html$span,
							_List_fromArray(
								[
									$elm$html$Html$Attributes$class('control-label')
								]),
							_List_fromArray(
								[
									$elm$html$Html$text(item.bY)
								])),
							A2(
							$elm$html$Html$span,
							_List_fromArray(
								[
									$elm$html$Html$Attributes$class('control-detail')
								]),
							_List_fromArray(
								[
									$elm$html$Html$text(item.q)
								]))
						]));
			} else {
				if (popup && ((snapshot.c === 'notifications') && (A2($elm$core$String$endsWith, ':summary', item.aG) || A2($elm$core$String$endsWith, ':body', item.aG)))) {
					return A2(
						$elm$html$Html$p,
						_List_fromArray(
							[
								$elm$html$Html$Attributes$class('notification-text'),
								$elm$html$Html$Attributes$id(item.C),
								A2($elm$html$Html$Attributes$attribute, 'data-notification-content', item.aG)
							]),
						_List_fromArray(
							[
								A2(
								$elm$html$Html$span,
								_List_fromArray(
									[
										$elm$html$Html$Attributes$class('control-label')
									]),
								_List_fromArray(
									[
										$elm$html$Html$text(item.bY)
									])),
								A2(
								$elm$html$Html$span,
								_List_fromArray(
									[
										$elm$html$Html$Attributes$class('control-detail')
									]),
								_List_fromArray(
									[
										$elm$html$Html$text(item.q)
									]))
							]));
				} else {
					if (popup && (A2(
						$elm$core$List$member,
						snapshot.c,
						_List_fromArray(
							['system', 'files', 'jump'])) && A2($elm$core$String$endsWith, ':state', item.aG))) {
						return A2(
							$elm$html$Html$p,
							_List_fromArray(
								[
									$elm$html$Html$Attributes$class('notification-text'),
									$elm$html$Html$Attributes$id(item.C),
									A2(
									$elm$html$Html$Attributes$attribute,
									(snapshot.c === 'jump') ? 'data-jump-content' : ((snapshot.c === 'files') ? 'data-files-content' : 'data-system-content'),
									item.aG)
								]),
							_List_fromArray(
								[
									A2(
									$elm$html$Html$span,
									_List_fromArray(
										[
											$elm$html$Html$Attributes$class('control-label')
										]),
									_List_fromArray(
										[
											$elm$html$Html$text(item.bY)
										]))
								]));
					} else {
						if (popup && (A2(
							$elm$core$List$member,
							snapshot.c,
							_List_fromArray(
								['applications', 'files'])) && _Utils_eq(
							item.aG,
							$author$project$SurfaceRenderer$fieldIdentity(current)))) {
							var packet = F2(
								function (inputKind, query) {
									return send(
										$elm$json$Json$Encode$object(
											_List_fromArray(
												[
													_Utils_Tuple2(
													'surfaceProtocol',
													$elm$json$Json$Encode$int(2)),
													_Utils_Tuple2(
													'kind',
													$elm$json$Json$Encode$string(inputKind)),
													_Utils_Tuple2(
													'surface',
													$elm$json$Json$Encode$string('popup')),
													_Utils_Tuple2(
													'publication',
													$elm$json$Json$Encode$string(
														$author$project$UInt64$string(snapshot.bf))),
													_Utils_Tuple2(
													'lease',
													$elm$json$Json$Encode$string(
														$author$project$UInt64$string(snapshot.bs))),
													_Utils_Tuple2(
													'id',
													$elm$json$Json$Encode$string(item.aG)),
													_Utils_Tuple2(
													'query',
													$elm$json$Json$Encode$string(query))
												])));
								});
							var edit = A3(
								$elm$json$Json$Decode$map2,
								F2(
									function (query, composing) {
										return A2(
											packet,
											composing ? 'surface-preedit' : 'surface-query',
											query);
									}),
								A2(
									$elm$json$Json$Decode$at,
									_List_fromArray(
										['target', 'value']),
									$elm$json$Json$Decode$string),
								$elm$json$Json$Decode$oneOf(
									_List_fromArray(
										[
											A2($elm$json$Json$Decode$field, 'isComposing', $elm$json$Json$Decode$bool),
											$elm$json$Json$Decode$succeed(false)
										])));
							var composition = function (inputKind) {
								return A2(
									$elm$json$Json$Decode$map,
									packet(inputKind),
									A2(
										$elm$json$Json$Decode$at,
										_List_fromArray(
											['target', 'value']),
										$elm$json$Json$Decode$string));
							};
							return A2(
								$elm$html$Html$input,
								_List_fromArray(
									[
										$elm$html$Html$Attributes$class('launcher-search'),
										$elm$html$Html$Attributes$id(item.C),
										$elm$html$Html$Attributes$type_(
										(snapshot.c === 'files') ? 'text' : 'search'),
										$elm$html$Html$Attributes$placeholder(
										(snapshot.c === 'files') ? '/path/to/folder or ~/Documents' : 'Search applications'),
										$elm$html$Html$Attributes$value(item.bY),
										A2($elm$html$Html$Attributes$attribute, 'aria-label', item.a4),
										A2($elm$html$Html$Attributes$attribute, 'data-surface-field', item.aG),
										A2($elm$html$Html$Attributes$attribute, 'autocomplete', 'off'),
										$elm$html$Html$Attributes$disabled(!item.an),
										A2($elm$html$Html$Events$on, 'input', edit),
										A2(
										$elm$html$Html$Events$on,
										'compositionstart',
										composition('surface-composition-start')),
										A2(
										$elm$html$Html$Events$on,
										'compositionend',
										composition('surface-composition-end'))
									]),
								_List_Nil);
						} else {
							return A2(
								$elm$html$Html$button,
								_Utils_ap(
									_List_fromArray(
										[
											$elm$html$Html$Attributes$class(kind),
											$elm$html$Html$Attributes$id(item.C),
											A2(
											$elm$html$Html$Attributes$attribute,
											'data-window-state',
											(kind !== 'control-group') ? 'none' : (A2($elm$core$String$contains, 'Attention; ', item.q) ? 'attention' : (A2($elm$core$String$contains, 'Active', item.q) ? 'active' : (A2($elm$core$String$contains, 'Minimized', item.q) ? 'minimized' : 'open')))),
											A2($elm$html$Html$Attributes$attribute, 'aria-label', item.a4),
											$elm$html$Html$Attributes$disabled(!item.an),
											A2($elm$html$Html$Attributes$attribute, 'data-surface-control', item.aG),
											A2(
											$elm$html$Html$Attributes$attribute,
											'role',
											switcherOption ? 'option' : ((popup && (snapshot.c === 'menu')) ? 'menuitem' : 'button')),
											A2(
											$elm$html$Html$Attributes$attribute,
											'aria-current',
											(((!popup) && ((kind === 'control-group') && (A2($elm$core$String$contains, 'Active', item.q) && (!A2($elm$core$String$contains, 'Attention; ', item.q))))) || (popup && (A2(
												$elm$core$List$member,
												snapshot.c,
												_List_fromArray(
													['menu', 'switcher', 'snap', 'settings', 'notifications', 'system', 'files', 'jump'])) && ((item.q === 'Selected') || (settingsToggle && (item.q === 'On')))))) ? 'true' : 'false')
										]),
									_Utils_ap(
										$elm$core$String$isEmpty(description) ? _List_Nil : _List_fromArray(
											[
												A2($elm$html$Html$Attributes$attribute, 'aria-describedby', descriptionId)
											]),
										_Utils_ap(
											(popup && ((snapshot.c === 'settings') && (item.aG === 'settings:help'))) ? _List_fromArray(
												[
													A2(
													$elm$html$Html$Attributes$attribute,
													'aria-expanded',
													(item.q === 'Expanded') ? 'true' : 'false')
												]) : _List_Nil,
											_Utils_ap(
												settingsToggle ? _List_fromArray(
													[
														A2(
														$elm$html$Html$Attributes$attribute,
														'aria-pressed',
														(item.q === 'On') ? 'true' : 'false')
													]) : _List_Nil,
												switcherOption ? _List_fromArray(
													[
														A2(
														$elm$html$Html$Attributes$attribute,
														'aria-selected',
														(item.q === 'Selected') ? 'true' : 'false')
													]) : (((!popup) && (kind === 'control-group')) ? _List_fromArray(
													[
														A2(
														$elm$html$Html$Attributes$attribute,
														'aria-pressed',
														active ? 'true' : 'false')
													]) : _List_Nil))))),
								_List_fromArray(
									[
										$author$project$PreviewVisual$decorativeInlineView(visual),
										A2(
										$elm$html$Html$span,
										_List_fromArray(
											[
												$elm$html$Html$Attributes$class('control-label')
											]),
										_List_fromArray(
											[
												$elm$html$Html$text(item.bY)
											])),
										A2(
										$elm$html$Html$span,
										_List_fromArray(
											[
												$elm$html$Html$Attributes$class('control-detail')
											]),
										_List_fromArray(
											[
												$elm$html$Html$text(item.q)
											])),
										$elm$core$String$isEmpty(description) ? $elm$html$Html$text('') : A2(
										$elm$html$Html$span,
										_List_fromArray(
											[
												$elm$html$Html$Attributes$class('preview-description'),
												$elm$html$Html$Attributes$id(descriptionId),
												$elm$html$Html$Attributes$hidden(true)
											]),
										_List_fromArray(
											[
												$elm$html$Html$text(description)
											]))
									]));
						}
					}
				}
			}
		};
		var overviewRows = function (rows) {
			if (!rows.b) {
				return _List_Nil;
			} else {
				var first = rows.a;
				var rest = rows.b;
				if (A2($elm$core$String$startsWith, 'overview:workspace:', first.aG)) {
					var members = familyPrefix(rest);
					return A2(
						$elm$core$List$cons,
						A2(
							$elm$html$Html$div,
							_List_fromArray(
								[
									$elm$html$Html$Attributes$class('overview-workspace'),
									A2($elm$html$Html$Attributes$attribute, 'role', 'group'),
									A2($elm$html$Html$Attributes$attribute, 'aria-labelledby', first.C)
								]),
							A2(
								$elm$core$List$map,
								control,
								A2($elm$core$List$cons, first, members))),
						overviewRows(
							A2(
								$elm$core$List$drop,
								$elm$core$List$length(members),
								rest)));
				} else {
					return A2(
						$elm$core$List$cons,
						control(first),
						overviewRows(rest));
				}
			}
		};
		return popup ? A2(
			$elm$html$Html$div,
			_List_fromArray(
				[
					A2($elm$html$Html$Attributes$attribute, 'data-motion', snapshot.bb),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-theme',
					$author$project$Settings$themeName(snapshot.G.bn)),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-text-scale',
					$elm$core$String$fromInt(snapshot.G.a0)),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-effects',
					snapshot.G.a7 ? 'off' : 'on'),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-reduced-transparency',
					snapshot.G.bg ? 'true' : 'false'),
					$elm$html$Html$Attributes$class('surface-popup'),
					A2($elm$html$Html$Attributes$attribute, 'data-mode', snapshot.c),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-publication',
					$author$project$UInt64$string(snapshot.bf)),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-lease',
					$author$project$UInt64$string(snapshot.bs))
				]),
			_List_fromArray(
				[
					A2(
					$elm$html$Html$h1,
					_List_Nil,
					_List_fromArray(
						[
							$elm$html$Html$text(
							(snapshot.c === 'applications') ? 'Applications' : ((snapshot.c === 'overview') ? 'Task View' : ((snapshot.c === 'switcher') ? 'Switch windows' : ((snapshot.c === 'snap') ? 'Snap window' : ((snapshot.c === 'jump') ? 'Application actions' : ((snapshot.c === 'files') ? 'Files' : ((snapshot.c === 'system') ? 'System' : ((snapshot.c === 'notifications') ? 'Notifications' : ((snapshot.c === 'settings') ? 'Settings' : ((snapshot.c === 'menu') ? 'Window actions' : 'Choose a window'))))))))))
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
							$elm$html$Html$text(snapshot.ai)
						])),
					(snapshot.c === 'overview') ? A2(
					$elm$html$Html$div,
					_List_fromArray(
						[
							$elm$html$Html$Attributes$class('surface-controls'),
							A2($elm$html$Html$Attributes$attribute, 'role', 'group')
						]),
					overviewRows(snapshot.n)) : ((snapshot.c === 'switcher') ? A2(
					$elm$html$Html$div,
					_List_fromArray(
						[
							$elm$html$Html$Attributes$class('surface-controls'),
							A2($elm$html$Html$Attributes$attribute, 'role', 'group'),
							A2($elm$html$Html$Attributes$attribute, 'aria-label', 'Window switcher controls')
						]),
					_List_fromArray(
						[
							A3(
							$elm$html$Html$Keyed$node,
							'div',
							_List_fromArray(
								[
									A2($elm$html$Html$Attributes$attribute, 'role', 'listbox'),
									A2($elm$html$Html$Attributes$attribute, 'aria-label', 'Switch windows'),
									A2($elm$html$Html$Attributes$attribute, 'aria-multiselectable', 'false')
								]),
							A2(
								$elm$core$List$map,
								function (item) {
									return _Utils_Tuple2(
										'control:' + item.aG,
										control(item));
								},
								A2(
									$elm$core$List$filter,
									function (item) {
										return A2($elm$core$String$startsWith, 'switcher:family:', item.aG);
									},
									snapshot.n))),
							A3(
							$elm$html$Html$Keyed$node,
							'div',
							_List_fromArray(
								[
									A2($elm$html$Html$Attributes$attribute, 'role', 'group'),
									A2($elm$html$Html$Attributes$attribute, 'aria-label', 'Window switcher actions')
								]),
							A2(
								$elm$core$List$map,
								function (item) {
									return _Utils_Tuple2(
										'control:' + item.aG,
										control(item));
								},
								A2(
									$elm$core$List$filter,
									function (item) {
										return !A2($elm$core$String$startsWith, 'switcher:family:', item.aG);
									},
									snapshot.n)))
						])) : A3(
					$elm$html$Html$Keyed$node,
					'div',
					_List_fromArray(
						[
							$elm$html$Html$Attributes$class('surface-controls'),
							A2(
							$elm$html$Html$Attributes$attribute,
							'role',
							(snapshot.c === 'menu') ? 'menu' : 'group')
						]),
					A2(
						$elm$core$List$map,
						function (item) {
							return _Utils_Tuple2(
								'control:' + item.aG,
								control(item));
						},
						snapshot.n)))
				])) : A3(
			$elm$html$Html$Keyed$node,
			'div',
			_List_fromArray(
				[
					A2($elm$html$Html$Attributes$attribute, 'data-motion', snapshot.bb),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-theme',
					$author$project$Settings$themeName(snapshot.G.bn)),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-text-scale',
					$elm$core$String$fromInt(snapshot.G.a0)),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-effects',
					snapshot.G.a7 ? 'off' : 'on'),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-reduced-transparency',
					snapshot.G.bg ? 'true' : 'false'),
					$elm$html$Html$Attributes$class('surface-bar'),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-publication',
					$author$project$UInt64$string(snapshot.bf)),
					A2(
					$elm$html$Html$Attributes$attribute,
					'data-lease',
					$author$project$UInt64$string(snapshot.bs))
				]),
			_List_fromArray(
				[
					_Utils_Tuple2(
					'actions',
					A3(
						$elm$html$Html$Keyed$node,
						'div',
						_List_fromArray(
							[
								$elm$html$Html$Attributes$class('surface-actions'),
								A2($elm$html$Html$Attributes$attribute, 'role', 'toolbar'),
								A2($elm$html$Html$Attributes$attribute, 'aria-label', 'Warlock taskbar')
							]),
						A2(
							$elm$core$List$map,
							function (item) {
								return _Utils_Tuple2(
									'control:' + item.aG,
									control(item));
							},
							snapshot.K))),
					_Utils_Tuple2(
					'status',
					A2(
						$elm$html$Html$span,
						_List_fromArray(
							[
								$elm$html$Html$Attributes$class(
								($elm$core$String$isEmpty(snapshot.ai) || (snapshot.ai === 'Ready')) ? 'surface-status surface-status-idle' : 'surface-status'),
								A2($elm$html$Html$Attributes$attribute, 'role', 'status'),
								A2($elm$html$Html$Attributes$attribute, 'aria-live', 'polite'),
								A2($elm$html$Html$Attributes$attribute, 'aria-atomic', 'true'),
								A2($elm$html$Html$Attributes$attribute, 'aria-label', snapshot.ai),
								$elm$html$Html$Attributes$title(snapshot.ai)
							]),
						_List_fromArray(
							[
								$elm$html$Html$text(snapshot.ai)
							])))
				]));
	});
var $author$project$PreviewVisual$Capacity = 0;
var $author$project$PreviewVisual$Conflict = 3;
var $author$project$PreviewVisual$Exhausted = 4;
var $author$project$PreviewVisual$Expired = 2;
var $author$project$PreviewVisual$Local = F2(
	function (a, b) {
		return {$: 2, a: a, b: b};
	});
var $author$project$PreviewVisual$Waiting = 1;
var $author$project$PreviewVisual$Fallback = {$: 1};
var $author$project$PreviewVisual$Client = 0;
var $author$project$PreviewVisual$Historical = 1;
var $author$project$PreviewVisual$Lifecycle = function (a) {
	return {$: 3, a: a};
};
var $author$project$PreviewVisual$Live = 0;
var $author$project$PreviewVisual$Loading = 2;
var $author$project$PreviewLifecycle$visual = F2(
	function (info, _v0) {
		var st = _v0;
		var current = $author$project$PreviewLifecycle$status(st);
		var shown = function () {
			switch (current.$) {
				case 0:
					return 0;
				case 1:
					return 1;
				case 2:
					return 2;
				default:
					return 3;
			}
		}();
		var _v1 = $author$project$PreviewLifecycle$drawablePacket(current);
		if (!_v1.$) {
			var packet = _v1.a;
			return $author$project$PreviewVisual$Lifecycle(
				{
					aF: $elm$core$Maybe$Just(
						(packet.aF === 1) ? 1 : 0),
					bS: $elm$core$Maybe$Just(
						$author$project$PreviewLifecycle$handleString(packet.X)),
					bq: $elm$core$Maybe$Nothing,
					i: shown,
					bD: $elm$core$Maybe$Nothing
				});
		} else {
			return $author$project$PreviewVisual$Lifecycle(
				{
					aF: $elm$core$Maybe$Nothing,
					bS: $elm$core$Maybe$Nothing,
					bq: (st.P || st.a.E) ? $elm$core$Maybe$Nothing : A2(
						$elm$core$Maybe$map,
						function (_v2) {
							var handle = _v2;
							return handle;
						},
						info.bq),
					i: shown,
					bD: $elm$core$Maybe$Just(
						(st.P || st.a.E) ? 'Preview unavailable' : info.bD)
				});
		}
	});
var $author$project$PreviewPresenter$entryVisual = function (entry) {
	return A2(
		$elm$core$Maybe$withDefault,
		$author$project$PreviewVisual$Fallback,
		A2(
			$elm$core$Maybe$map,
			$author$project$PreviewLifecycle$visual(
				{p: entry.p, bq: entry.bq, bD: entry.bD}),
			entry.d));
};
var $author$project$PreviewPresenter$visual = F3(
	function (snapshot, identity, _v0) {
		var entries = _v0.a;
		return A2(
			$elm$core$Maybe$withDefault,
			$author$project$PreviewVisual$Hidden,
			A2(
				$elm$core$Maybe$andThen,
				function (entry) {
					return A2(
						$elm$core$Maybe$andThen,
						function (stamp) {
							return (A2($author$project$PreviewPresenter$same, stamp, snapshot) && A3($author$project$SurfaceRenderer$enabled, true, identity, snapshot)) ? $elm$core$Maybe$Just(
								function () {
									var _v1 = entry.m;
									if (!_v1.$) {
										var local = _v1.a;
										return A2(
											$elm$core$Maybe$withDefault,
											false,
											A2($elm$core$Maybe$map, $author$project$PreviewLifecycle$idle, entry.d)) ? A2(
											$author$project$PreviewVisual$Local,
											function () {
												var _v2 = local.aY;
												switch (_v2) {
													case 0:
														return 0;
													case 1:
														return 1;
													case 2:
														return 2;
													case 3:
														return 3;
													default:
														return 4;
												}
											}(),
											entry.bD) : $author$project$PreviewPresenter$entryVisual(entry);
									} else {
										return $author$project$PreviewPresenter$entryVisual(entry);
									}
								}()) : $elm$core$Maybe$Nothing;
						},
						entry.k);
				},
				A2($elm$core$Dict$get, identity, entries)));
	});
var $author$project$RetainedPreviewPresenter$visual = F3(
	function (snapshot, name, _v0) {
		var policy = _v0.a;
		return A3($author$project$PreviewPresenter$visual, snapshot, name, policy);
	});
var $author$project$Popup$main = $elm$browser$Browser$element(
	{
		cD: function (_v0) {
			return _Utils_Tuple2($author$project$Popup$initial, $elm$core$Platform$Cmd$none);
		},
		cL: function (_v1) {
			return $elm$core$Platform$Sub$batch(
				_List_fromArray(
					[
						$author$project$Popup$presentation($author$project$Popup$Present),
						$author$project$Popup$requestAction($author$project$Popup$Action),
						$author$project$Popup$nativePreviews($author$project$Popup$NativePreview),
						$author$project$Popup$nativePreviewGrants($author$project$Popup$NativeGrant),
						$author$project$Popup$nativePreviewQuarantine($author$project$Popup$NativeQuarantine),
						$author$project$Popup$nativePreviewClosed($author$project$Popup$NativeClosed),
						$author$project$Popup$nativePreviewIssued($author$project$Popup$NativeIssued),
						$author$project$Popup$nativePreviewRetry($author$project$Popup$NativeRetry),
						$author$project$Popup$nativePreviewRetirement($author$project$Popup$NativeRetirement)
					]));
		},
		cM: $author$project$Popup$update,
		cN: function (model) {
			return A2(
				$elm$html$Html$div,
				_List_fromArray(
					[
						A2(
						$elm$html$Html$Attributes$attribute,
						'data-input-composing',
						$author$project$Popup$isComposing(model) ? 'true' : 'false')
					]),
				_List_fromArray(
					[
						A2(
						$elm$core$Maybe$withDefault,
						$elm$html$Html$text(''),
						A2(
							$elm$core$Maybe$map,
							function (snapshot) {
								return A4(
									$author$project$SurfaceRenderer$viewWithPreview,
									function (identity) {
										return A3($author$project$RetainedPreviewPresenter$visual, snapshot, identity, model.f);
									},
									true,
									$author$project$Popup$Action,
									A2(
										$elm$core$Maybe$withDefault,
										snapshot,
										A2(
											$elm$core$Maybe$map,
											function (query) {
												return A2($author$project$SurfaceRenderer$pendingQuery, query, snapshot);
											},
											model.y)));
							},
							$author$project$Presentation$current(model.z)))
					]));
		}
	});
_Platform_export({'Popup':{'init':$author$project$Popup$main(
	$elm$json$Json$Decode$succeed(0))(0)}});}(this));