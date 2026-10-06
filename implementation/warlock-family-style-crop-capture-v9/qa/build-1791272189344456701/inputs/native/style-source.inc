std::optional<preview::RenderConfiguration> familyRenderConfiguration(){
    // Value-owned native facts, sampled on the compositor owner thread.
    // Read the exact keys/types used by this owning renderer; no GUI policy.
    preview::RenderConfiguration value;
    static auto integer0=CConfigValue<Config::INTEGER>("decoration:shadow:enabled");if(!integer0.good())return {};value.integers[0]=*integer0;
    static auto integer1=CConfigValue<Config::INTEGER>("decoration:shadow:range");if(!integer1.good())return {};value.integers[1]=*integer1;
    static auto integer2=CConfigValue<Config::INTEGER>("decoration:shadow:render_power");if(!integer2.good())return {};value.integers[2]=*integer2;
    static auto integer3=CConfigValue<Config::INTEGER>("decoration:shadow:sharp");if(!integer3.good())return {};value.integers[3]=*integer3;
    static auto integer4=CConfigValue<Config::INTEGER>("decoration:glow:enabled");if(!integer4.good())return {};value.integers[4]=*integer4;
    static auto integer5=CConfigValue<Config::INTEGER>("decoration:glow:range");if(!integer5.good())return {};value.integers[5]=*integer5;
    static auto integer6=CConfigValue<Config::INTEGER>("decoration:glow:render_power");if(!integer6.good())return {};value.integers[6]=*integer6;
    static auto integer7=CConfigValue<Config::INTEGER>("decoration:blur:enabled");if(!integer7.good())return {};value.integers[7]=*integer7;
    static auto integer8=CConfigValue<Config::INTEGER>("decoration:blur:size");if(!integer8.good())return {};value.integers[8]=*integer8;
    static auto integer9=CConfigValue<Config::INTEGER>("decoration:blur:passes");if(!integer9.good())return {};value.integers[9]=*integer9;
    static auto integer10=CConfigValue<Config::INTEGER>("decoration:blur:new_optimizations");if(!integer10.good())return {};value.integers[10]=*integer10;
    static auto integer11=CConfigValue<Config::INTEGER>("decoration:blur:xray");if(!integer11.good())return {};value.integers[11]=*integer11;
    static auto integer12=CConfigValue<Config::INTEGER>("decoration:blur:ignore_opacity");if(!integer12.good())return {};value.integers[12]=*integer12;
    static auto integer13=CConfigValue<Config::INTEGER>("decoration:blur:popups");if(!integer13.good())return {};value.integers[13]=*integer13;
    static auto integer14=CConfigValue<Config::INTEGER>("decoration:blur:input_methods");if(!integer14.good())return {};value.integers[14]=*integer14;
    static auto integer15=CConfigValue<Config::INTEGER>("render:use_shader_blur_blend");if(!integer15.good())return {};value.integers[15]=*integer15;
    static auto integer16=CConfigValue<Config::INTEGER>("render:cm_enabled");if(!integer16.good())return {};value.integers[16]=*integer16;
    static auto integer17=CConfigValue<Config::INTEGER>("render:cm_auto_hdr");if(!integer17.good())return {};value.integers[17]=*integer17;
    static auto integer18=CConfigValue<Config::INTEGER>("render:non_shader_cm");if(!integer18.good())return {};value.integers[18]=*integer18;
    static auto integer19=CConfigValue<Config::INTEGER>("render:non_shader_cm_interop");if(!integer19.good())return {};value.integers[19]=*integer19;
    static auto integer20=CConfigValue<Config::INTEGER>("render:send_content_type");if(!integer20.good())return {};value.integers[20]=*integer20;
    static auto integer21=CConfigValue<Config::INTEGER>("render:xp_mode");if(!integer21.good())return {};value.integers[21]=*integer21;
    static auto xwaylandNearest=CConfigValue<Config::INTEGER>("xwayland:use_nearest_neighbor");if(!xwaylandNearest.good())return {};value.integers[preview::XwaylandNearestNeighbor]=*xwaylandNearest;
    static auto floating0=CConfigValue<Config::FLOAT>("decoration:shadow:scale");if(!floating0.good())return {};value.floating[0]=*floating0;
    static auto floating3=CConfigValue<Config::FLOAT>("decoration:dim_around");if(!floating3.good())return {};value.floating[3]=*floating3;
    static auto floating4=CConfigValue<Config::FLOAT>("decoration:blur:brightness");if(!floating4.good())return {};value.floating[4]=*floating4;
    static auto floating5=CConfigValue<Config::FLOAT>("decoration:blur:contrast");if(!floating5.good())return {};value.floating[5]=*floating5;
    static auto floating6=CConfigValue<Config::FLOAT>("decoration:blur:vibrancy");if(!floating6.good())return {};value.floating[6]=*floating6;
    static auto floating7=CConfigValue<Config::FLOAT>("decoration:blur:vibrancy_darkness");if(!floating7.good())return {};value.floating[7]=*floating7;
    static auto floating8=CConfigValue<Config::FLOAT>("decoration:blur:noise");if(!floating8.good())return {};value.floating[8]=*floating8;
    static auto floating9=CConfigValue<Config::FLOAT>("decoration:blur:popups_ignorealpha");if(!floating9.good())return {};value.floating[9]=*floating9;
    static auto floating10=CConfigValue<Config::FLOAT>("decoration:blur:input_methods_ignorealpha");if(!floating10.good())return {};value.floating[10]=*floating10;
    static auto offset=CConfigValue<Config::VEC2>("decoration:shadow:offset");if(!offset.good())return {};
    value.floating[preview::ShadowOffsetX]=(*offset).x;value.floating[preview::ShadowOffsetY]=(*offset).y;
    static auto shader=CConfigValue<std::string>("decoration:screen_shader");if(!shader.good())return {};value.screenShader=*shader;
    return value;
}
struct FamilyStyleObservation {preview::Context context;std::vector<preview::WindowStyle> styles;};
std::optional<FamilyStyleObservation> familyStyleContext(PHLWINDOW root,uint64_t subject){
    // Invalid subjects must never allocate persistent source state.
    const auto family=familyContext(root,subject);
    if(!family){if(const auto old=familyStyles.find(subject);old!=familyStyles.end())old->second.unavailable();return {};}
    if(!familyStyles.contains(subject) && familyStyles.size()>=256)return {};
    auto& revision=familyStyles[subject];
    auto refused=[&]()->std::optional<FamilyStyleObservation>{revision.unavailable();return {};};
    const auto configuration=familyRenderConfiguration();if(!configuration)return refused();
    std::vector<preview::WindowStyle> styles;size_t blurRectangles=0;
    const auto ownerState=familySources.find(subject);if(ownerState==familySources.end())return refused();
    for(const auto& row:family->members){
        const auto member=std::find_if(members.begin(),members.end(),[&](const Member& value){return value.id==row.id;});
        const auto window=member==members.end()?PHLWINDOW{}:member->window.lock();if(!window || !window->m_workspace)return refused();
        static_assert(static_cast<size_t>(Desktop::View::WINDOW_ALPHA_LAST)==static_cast<size_t>(preview::WorkspaceAlpha));
        preview::WindowStyle style{};style.id=row.id;
        auto* rules=window->m_ruleApplicator.get();if(!rules)return refused();
        style.effectFlags=(uint64_t{rules->decorate().valueOrDefault()}<<0)
            | (uint64_t{rules->noShadow().valueOrDefault()}<<1)
            | (uint64_t{rules->noBlur().valueOrDefault()}<<2)
            | (uint64_t{rules->RGBX().valueOrDefault()}<<3)
            | (uint64_t{rules->xray().hasValue()}<<4)
            | (uint64_t{rules->xray().valueOrDefault()}<<5)
            | (uint64_t{rules->dimAround().valueOrDefault()}<<6)
            | (uint64_t{window->m_X11DoesntWantBorders}<<7)
            | (uint64_t{rules->opaque().valueOrDefault()}<<8)
            | (uint64_t{rules->nearestNeighbor().valueOrDefault()}<<9);
        const auto tree=preview::capture::rootPopupTree(window);if(!tree || tree->rows.empty())return refused();
        const auto tracker=ownerState->second.trees.find(row.id);if(tracker==ownerState->second.trees.end())return refused();
        style.rootSurfaceId=tracker->second.identity(tree->rows.front().surface);if(!style.rootSurfaceId)return refused();
        for(size_t index=0;index<tree->rows.size();++index){
            const auto& leaf=tree->rows[index];preview::SurfaceBackground effect{};
            effect.id=tracker->second.identity(leaf.surface);if(!effect.id)return refused();
            const auto nativeSurface=Desktop::View::CWLSurface::fromResource(leaf.surface);
            effect.hasEffect=nativeSurface && nativeSurface->m_hasBackgroundEffect;
            if(effect.hasEffect){
                const int count=pixman_region32_n_rects(nativeSurface->m_blurRegion.pixman());
                if(count<0 || static_cast<size_t>(count)>4096-blurRectangles)return refused();
                blurRectangles+=static_cast<size_t>(count);
                for(const auto& rectangle:nativeSurface->m_blurRegion.getRects())effect.blurRegion.push_back({rectangle.x1,rectangle.y1,rectangle.x2,rectangle.y2});
            }
            if(index==0){if(effect.hasEffect)style.effectFlags|=uint64_t{1}<<10;style.blurRegion=std::move(effect.blurRegion);}
            else style.surfaceEffects.push_back(std::move(effect));
        }
        for(size_t i=0;i<Desktop::View::WINDOW_ALPHA_LAST;++i)style.channels[i]=window->alphaValue(static_cast<Desktop::View::eWindowAlpha>(i));
        style.channels[preview::WorkspaceAlpha]=window->m_pinned?1.0:window->m_workspace->m_alpha->value();
        if(!window->m_dimPercent || !window->m_notRespondingTint)return refused();
        style.channels[preview::DimPercent]=window->m_dimPercent->value();style.channels[preview::AnrTint]=window->m_notRespondingTint->value();
        style.channels[preview::Rounding]=window->rounding();style.channels[preview::RoundingPower]=window->roundingPower();style.channels[preview::BorderSize]=window->getRealBorderSize();
        size_t channel=preview::BorderFade,flag=0;
        for(const auto& animation:{window->m_borderFadeAnimationProgress.get(),window->m_borderAngleAnimationProgress.get(),window->m_shadowFadeAnimationProgress.get(),window->m_shadowAngleAnimationProgress.get(),window->m_glowFadeAnimationProgress.get(),window->m_glowAngleAnimationProgress.get()}){
            if(!animation)return refused();
            style.channels[channel++]=animation->value();
            if(animation->isBeingAnimated())style.flags|=uint64_t{1}<<flag;
            if(animation->enabled())style.flags|=uint64_t{1}<<(flag+6);
            ++flag;
        }
        size_t index=0;
        for(const auto* gradient:{&window->m_realBorderColor,&window->m_realBorderColorPrevious,&window->m_realShadowColor,&window->m_realShadowColorPrevious,&window->m_realGlowColor,&window->m_realGlowColorPrevious}){
            auto& value=style.gradients[index++];value.angle=gradient->m_angle;
            for(const auto& color:gradient->m_colors)value.rgba.push_back({color.r,color.g,color.b,color.a});
            value.shader.assign(gradient->m_colorsOkLabA.begin(),gradient->m_colorsOkLabA.end());
        }
        styles.push_back(std::move(style));
    }
    if(!revision.observe(subject,family->context.content.value,styles,true,*configuration))return {};
    auto context=family->context;context.content={revision.value()};return FamilyStyleObservation{context,std::move(styles)};
}
std::string familyStylesJSON(const FamilyStyleObservation& observed){
    std::string output="[";bool first=true;
    for(const auto& style:observed.styles){
        if(!first)output+=',';
        first=false;
        output+="{\"incarnation\":"+quote(std::to_string(style.id))+",\"flags\":"+std::to_string(style.flags)+",\"channels\":[";
        for(size_t i=0;i<style.channels.size();++i){if(i)output+=',';output+=std::format("{:.17g}",style.channels[i]);}
        output+="],\"gradients\":[";
        for(size_t i=0;i<style.gradients.size();++i){if(i)output+=',';const auto& gradient=style.gradients[i];output+="{\"angle\":"+std::format("{:.17g}",gradient.angle)+",\"colors\":"+std::to_string(gradient.rgba.size())+"}";}
        output+="]}";
    }
    return output+"]";
}
