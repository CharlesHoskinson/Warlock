module shader_precision_test {
 import shader_precision.* from "./shader_precision"
 action check(p:bool):bool=all{assert(p),s'=s}
 run unsupportedFragmentPrecisionCannotUploadTest=init.then(fire(Inspect({epoch:1,vertex:23,fragment:10,error:false}))).then(fire(Compile(true))).then(fire(Upload)).then(check(s.uploaded==0))
 run actualPrecisionInspectionAndCompiledShaderRequiredTest=init.then(fire(Inspect({epoch:1,vertex:23,fragment:23,error:false}))).then(fire(Compile(true))).then(fire(Upload)).then(fire(Ready)).then(check(s.ready))
 run priorContextPrecisionCannotAuthorizeNewContextTest=init.then(fire(Context)).then(fire(Inspect({epoch:1,vertex:23,fragment:23,error:false}))).then(fire(Compile(true))).then(fire(Upload)).then(check(s.uploaded==0))
 run shaderCompilationFailureCannotGrantReadinessTest=init.then(fire(Inspect({epoch:1,vertex:23,fragment:23,error:false}))).then(fire(Compile(false))).then(fire(Upload)).then(fire(Ready)).then(check(not(s.ready)))
}
