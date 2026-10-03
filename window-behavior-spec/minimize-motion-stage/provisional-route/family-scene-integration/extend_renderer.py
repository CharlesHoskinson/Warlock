from pathlib import Path
p=Path(__file__).parent/'producer/Renderer.cpp'
s=p.read_text()
s=s.replace('static Rect interpolate(','''static QJsonArray identityJson(const std::vector<Identity>& ids){QJsonArray out;for(const auto& id:ids)out.append(QJsonObject{{"stableId",qs(id.stable)},{"pid",double(id.pid)}});return out;}
static std::vector<Identity> identities(const QJsonObject& j){auto array=j["identities"].toArray();if(array.empty()||array.size()>64)throw std::invalid_argument("exact complete identity vector required");std::vector<Identity> out;std::set<std::string> seen;for(const auto& value:array){auto id=identity(value.toObject());if(!seen.insert(id.stable).second)throw std::invalid_argument("duplicate identity");out.push_back(id);}return out;}
static QJsonArray membersJson(const std::vector<MemberFrame>& members){QJsonArray out;for(const auto& m:members)out.append(QJsonObject{{"stableId",qs(m.source.identity.stable)},{"pid",double(m.source.identity.pid)},{"digest",qs(m.source.digest)},{"rectangle",rectangleJson(m.rectangle)}});return out;}
static Rect interpolate(''')
s=s.replace('GLuint shader=0,texture=0;', 'GLuint shader=0,texture=0;std::vector<GLuint> familyTextures;std::vector<Identity> familyIdentities;')
s=s.replace('    void upload(', '    GLuint upload(')
s=s.replace('if(texture)glDeleteTextures(1,&texture);glGenTextures(1,&texture);glBindTexture(GL_TEXTURE_2D,texture);', 'GLuint uploaded=0;glGenTextures(1,&uploaded);glBindTexture(GL_TEXTURE_2D,uploaded);')
s=s.replace('if(glGetError()!=GL_NO_ERROR)throw std::runtime_error("GPU snapshot upload failed");++uploadCount;', 'if(glGetError()!=GL_NO_ERROR){glDeleteTextures(1,&uploaded);throw std::runtime_error("GPU snapshot upload failed");}++uploadCount;')
s=s.replace('{{"event","uploaded"},{"digest",qs(expected)},{"pixels",QJsonArray{int(image.width),int(image.height)}},{"uploadCount",int(uploadCount)}});', '{{"event","uploaded"},{"digest",qs(expected)},{"pixels",QJsonArray{int(image.width),int(image.height)}},{"uploadCount",int(uploadCount)}});return uploaded;')
s=s.replace('{"servicePromoted",true}', '{"servicePromoted",true},{"identities",identityJson(familyIdentities)}')
s=s.replace('{"endpoint",frame.endpoint}});', '{"endpoint",frame.endpoint},{"members",membersJson(frame.members)}});')
start=s.index('        Rect rect=o.from;\n        if(active){')
end=s.index('        if(glGetError()!=GL_NO_ERROR)',start)
s=s[:start]+'''        auto members=active?ledger.sceneRectangles(o.name,p):std::vector<MemberFrame>{};
        if(active){
            if(members.size()!=familyTextures.size()){cancel("complete family textures unavailable");return;}
            glEnable(GL_BLEND);glBlendFunc(GL_ONE,GL_ONE_MINUS_SRC_ALPHA);glUseProgram(shader);glActiveTexture(GL_TEXTURE0);glUniform1i(glGetUniformLocation(shader,"atlas"),0);
            glEnableVertexAttribArray(positionLocation);glEnableVertexAttribArray(uvLocation);
            for(size_t i=0;i<members.size();++i){const auto& rect=members[i].rectangle;
                const GLfloat left=2*(rect.x-o.x)/o.width-1,right=2*(rect.x+rect.width-o.x)/o.width-1;
                const GLfloat top=1-2*(rect.y-o.y)/o.height,bottom=1-2*(rect.y+rect.height-o.y)/o.height;
                const GLfloat positions[]={left,top,right,top,left,bottom,right,bottom},uv[]={0,0,1,0,0,1,1,1};
                glBindTexture(GL_TEXTURE_2D,familyTextures[i]);glVertexAttribPointer(positionLocation,2,GL_FLOAT,GL_FALSE,0,positions);glVertexAttribPointer(uvLocation,2,GL_FLOAT,GL_FALSE,0,uv);glDrawArrays(GL_TRIANGLE_STRIP,0,4);
            }
            glDisableVertexAttribArray(positionLocation);glDisableVertexAttribArray(uvLocation);
        }
'''+s[end:]
s=s.replace('ledger.prepare(o.name,o.generation,rect,p,p==1,monotonicNs())', 'ledger.prepareFamily(o.name,o.generation,p,monotonicNs())')
s=s.replace('{"uploadCount",int(uploadCount)}});\n        }', '{"uploadCount",int(uploadCount)},{"members",membersJson(submittedScene->members)}});\n        }')
s=s.replace('ledger.retarget(routeIdentity,token)', 'ledger.retargetFamily(familyIdentities,token,j["operation"].toString().toStdString())')
s=s.replace('target=rectangle(j["target"]);durationNs=', 'durationNs=')
s=s.replace('{"rectangle",rectangleJson(f.frame.rectangle)}});}', '{"rectangle",rectangleJson(f.frame.rectangle)},{"members",membersJson(f.frame.members)}});}')
s=s.replace('{"sourceReused",true}', '{"sourceReused",true},{"identities",identityJson(familyIdentities)}')
s=s.replace('ledger.promote(routeIdentity,token)', 'ledger.promoteFamily(familyIdentities,token)')
s=s.replace('{"endpoint",f.endpoint}});}', '{"endpoint",f.endpoint},{"members",membersJson(f.members)}});}')
s=s.replace('{"records",records}});', '{"records",records},{"identities",identityJson(familyIdentities)}});')
s=s.replace('identity(j)==routeIdentity', 'identities(j)==familyIdentities')
start=s.index('        if(kind=="seed"){')
end=s.index('        if(kind=="retarget"){',start)
new='''        if(kind=="seed"){
            if(ledger.isActive())throw std::invalid_argument("active scene must be cancelled before new snapshots");
            auto token=j["token"].toString().toStdString();if(!validToken(token))throw std::invalid_argument("invalid whole scene token");
            auto op=j["operation"].toString();if(op!="minimize"&&op!="restore")throw std::invalid_argument("invalid operation");
            int duration=j["durationMs"].toInt();if(duration<1||duration>4000)throw std::invalid_argument("invalid duration");
            auto items=j["members"].toArray();if(items.empty()||items.size()>64)throw std::invalid_argument("complete ordered family sources required");
            std::vector<Source> sources;std::vector<QJsonObject> inputs;std::vector<Identity> ids;std::set<std::string> seen;uint64_t rgbaBytes=0;QJsonArray digestRecords;
            for(const auto& value:items){auto m=value.toObject();auto id=identity(m);auto hash=m["digest"].toString().toStdString();
                if(!validDigest(hash)||!seen.insert(id.stable).second)throw std::invalid_argument("invalid digest or duplicate family identity");
                auto native=rectangle(m["nativeRect"]),atlas=rectangle(m["atlasRect"]),icon=rectangle(m["iconRect"]);
                auto inset=m["insets"].toObject();double left=inset["left"].toDouble(NAN),top=inset["top"].toDouble(NAN),right=inset["right"].toDouble(NAN),bottom=inset["bottom"].toDouble(NAN);
                for(auto v:{left,top,right,bottom})if(!std::isfinite(v)||v<0)throw std::invalid_argument("invalid captured insets");
                if(std::abs(atlas.x+left-native.x)>1e-6||std::abs(atlas.y+top-native.y)>1e-6||std::abs(atlas.width-left-right-native.width)>1e-6||std::abs(atlas.height-top-bottom-native.height)>1e-6)throw std::invalid_argument("captured atlas/native geometry disagrees");
                auto pixels=m["pixels"].toArray();int pw=pixels.size()==2?pixels[0].toInt():0,ph=pixels.size()==2?pixels[1].toInt():0;double scale=m["captureScale"].toDouble();
                if(!std::isfinite(scale)||scale<=0||scale>8||pw<=0||ph<=0||pw>8192||ph>8192||std::abs(atlas.width*scale-pw)>1e-6||std::abs(atlas.height*scale-ph)>1e-6)throw std::invalid_argument("invalid captured pixel scale/extent");
                rgbaBytes+=uint64_t(pw)*ph*4;if(rgbaBytes>268435456)throw std::invalid_argument("family decoded texture memory exceeds bound");
                sources.push_back({id,hash,native,atlas,icon});ids.push_back(id);inputs.push_back(m);
                digestRecords.append(QJsonObject{{"stableId",qs(id.stable)},{"pid",double(id.pid)},{"digest",qs(hash)},{"nativeRect",rectangleJson(native)},{"atlasRect",rectangleJson(atlas)},{"iconRect",rectangleJson(icon)}});
            }
            auto hash=QCryptographicHash::hash(QJsonDocument(digestRecords).toJson(QJsonDocument::Compact),QCryptographicHash::Sha256).toHex().toStdString();
            std::map<std::string,uint64_t> generations;std::vector<Output*> selected;
            for(auto value:j["outputs"].toArray()){auto o=value.toObject();auto name=o["name"].toString().toStdString();double number=o["generation"].toDouble();if(!std::isfinite(number)||number<1||number>9007199254740991.0||std::floor(number)!=number)throw std::invalid_argument("invalid output generation number");uint64_t gen=number;
                auto match=std::find_if(outputs.begin(),outputs.end(),[&](auto& p){return p->alive&&p->configured&&p->preferredScale&&p->name==name&&p->generation==gen;});
                if(match==outputs.end()||generations.contains(name))throw std::invalid_argument("stale/duplicate output generation");selected.push_back(match->get());generations[name]=gen;
            }
            if(selected.empty())throw std::invalid_argument("no ready required outputs");
            if(!makeCurrent(*selected.front()))throw std::runtime_error("snapshot upload context unavailable");
            std::vector<GLuint> uploaded;try{for(const auto& m:inputs){auto pixels=m["pixels"].toArray();uploaded.push_back(upload(m["path"].toString().toStdString(),m["digest"].toString().toStdString(),pixels[0].toInt(),pixels[1].toInt()));}}catch(...){for(auto t:uploaded)glDeleteTextures(1,&t);throw;}
            for(auto t:familyTextures)glDeleteTextures(1,&t);familyTextures=std::move(uploaded);familyIdentities=std::move(ids);
            ledger.configure(generations);ledger.seedFamily(sources,token,hash,op.toStdString());
            routeIdentity=familyIdentities.front();digest=hash;operation=op.toStdString();durationNs=duration*1000000ULL;required=selected;
            for(auto* o:required){o->from=bounds(ledger.sceneRectangles(o->name,0));o->endpointPresented=false;}
            routeAcceptedNs=monotonicNs();endpointHeldNs=0;running=false;readySent=false;endpointSent=false;
            emitEvent({{"event","seeded"},{"token",qs(token)},{"identities",identityJson(familyIdentities)},{"nativeAuthority",false}});return;
        }
'''
s=s[:start]+new+s[end:]
s=s.replace('auto end=rectangle(j["target"]);auto operation=j["operation"].toString();if((operation!="minimize"&&operation!="restore")||end!=(operation=="minimize"?iconRect:atlasRect))', 'auto operation=j["operation"].toString();if(operation!="minimize"&&operation!="restore")')
s=s.replace('identity(j)!=routeIdentity', 'identities(j)!=familyIdentities')
s=s.replace('ledger.promote(identity(j),j["token"].toString().toStdString())', 'ledger.promoteFamily(identities(j),j["token"].toString().toStdString())')
s=s.replace('{"receivedNs",QString::number(monotonicNs())}', '{"receivedNs",QString::number(monotonicNs())},{"identities",identityJson(familyIdentities)}')
s=s.replace('{"reason",qs(reason)},{"nativeAuthority",false}', '{"reason",qs(reason)},{"identities",identityJson(familyIdentities)},{"nativeAuthority",false}')
p.write_text(s)
