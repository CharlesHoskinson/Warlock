struct FamilyStyleObservation {preview::Context context;std::vector<preview::WindowStyle> styles;};
std::optional<FamilyStyleObservation> familyStyleContext(PHLWINDOW root,uint64_t subject){
    auto& revision=familyStyles[subject];
    auto refused=[&]()->std::optional<FamilyStyleObservation>{revision.unavailable();return {};};
    const auto family=familyContext(root,subject);if(!family)return refused();
    std::vector<preview::WindowStyle> styles;
    for(const auto& row:family->members){
        const auto member=std::find_if(members.begin(),members.end(),[&](const Member& value){return value.id==row.id;});
        const auto window=member==members.end()?PHLWINDOW{}:member->window.lock();if(!window || !window->m_workspace)return refused();
        static_assert(static_cast<size_t>(Desktop::View::WINDOW_ALPHA_LAST)==static_cast<size_t>(preview::WorkspaceAlpha));
        preview::WindowStyle style{};style.id=row.id;
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
    if(!revision.observe(subject,family->context.content.value,styles))return {};
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
