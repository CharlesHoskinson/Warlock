        } else if (operation=="preview-incarnation-retirement-state-request" && fields(object,{"protocolVersion","kind","binding","requestId","subjectIncarnation"})) {
            const auto bound=objectMember(object,"binding");
            const auto requestId=counter(object,"requestId"),subject=counter(object,"subjectIncarnation");
            if(!bound || !requestId || !subject || !fields(bound,{"lifetime","session","frontend"})) throw std::runtime_error("incarnation-retirement-schema");
            const auto native=counter(bound,"lifetime"),sessionId=counter(bound,"session"),frontend=counter(bound,"frontend");
            const auto found=sessions.find(peer);
            if(!native || !sessionId || !frontend || found==sessions.end() || found->second.start!=start || *native!=lifetime || *sessionId!=found->second.id || *frontend!=found->second.frontend || !grantRegistry->callerMatches(verifiedPeer(peer,start),{lifetime,*sessionId,*frontend})) reply=error("binding-mismatch");
            else if(incarnationRetirementSequence==std::numeric_limits<uint64_t>::max()) reply=error("incarnation-retirement-sequence-exhausted");
            else {
                // Presence in the native membership table, including minimized
                // or suspended members, prevents permanent retirement. No
                // mapped-window catalog or source-scope exception is consulted.
                const bool owned=std::any_of(members.begin(),members.end(),[&](const Member& member){return member.id==*subject;});
                const auto state=preview::retirement::observe(*subject,incarnation,owned);
                ++incarnationRetirementSequence;
                reply="{\"protocolVersion\":3,\"kind\":\"preview-incarnation-retirement-state\",\"retirementProtocol\":1,\"binding\":"+binding(found->second)+",\"requestId\":"+quote(std::to_string(*requestId))+",\"subjectIncarnation\":"+quote(std::to_string(*subject))+",\"sequence\":"+quote(std::to_string(incarnationRetirementSequence))+",\"clock\":"+quote(std::to_string(lifetime))+",\"now\":"+quote(std::to_string(preview::capture::nativeNow()))+",\"issuedThrough\":"+quote(std::to_string(incarnation))+",\"state\":"+quote(preview::retirement::name(state))+"}";
            }
