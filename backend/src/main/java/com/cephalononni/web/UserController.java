package com.cephalononni.web;

import com.cephalononni.security.CurrentUser;
import com.cephalononni.web.dto.AuthDtos.UserPublic;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/users")
public class UserController {

    @GetMapping("/profile")
    public UserPublic getProfile(@AuthenticationPrincipal CurrentUser principal) {
        return new UserPublic(String.valueOf(principal.id()), principal.email(), principal.username(), principal.role().getWireValue());
    }
}
