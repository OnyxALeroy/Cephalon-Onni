package com.cephalononni.service;

import com.cephalononni.exception.ApiException;
import com.cephalononni.model.Warframe;
import com.cephalononni.repository.WarframeRepository;
import com.cephalononni.web.dto.WarframeDtos.WarframeResponse;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class WarframeService {

    private final WarframeRepository warframeRepository;

    public WarframeService(WarframeRepository warframeRepository) {
        this.warframeRepository = warframeRepository;
    }

    public List<WarframeResponse> listWarframes() {
        return warframeRepository.findAll().stream().map(this::toResponse).toList();
    }

    public WarframeResponse getWarframe(String uniqueName) {
        Warframe w = warframeRepository.findByUniqueName(uniqueName)
                .orElseThrow(() -> ApiException.notFound("Warframe not found"));
        return toResponse(w);
    }

    private WarframeResponse toResponse(Warframe w) {
        return new WarframeResponse(
                w.getId(), w.getUniqueName(), w.getName(), w.getParentName(), w.getDescription(),
                w.getHealth(), w.getShield(), w.getArmor(), w.getStamina(), w.getPower(),
                w.getCodexSecret(), w.getMasteryReq(), w.getSprintSpeed(), w.getPassiveDescription(),
                w.getExalted(), w.getAbilities(), w.getProductCategory());
    }
}
