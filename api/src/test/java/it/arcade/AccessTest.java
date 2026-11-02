package it.arcade;

import java.time.Instant;
import java.util.*;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.security.oauth2.jose.jws.MacAlgorithm;
import org.springframework.security.oauth2.jwt.*;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@SpringBootTest(properties={
    "spring.autoconfigure.exclude=org.springframework.boot.autoconfigure.jdbc.DataSourceAutoConfiguration",
    "arcade.jwt.secret=test-only-key-with-at-least-32-bytes-long",
    "arcade.demo.istante=2025-12-20T11:55:00+01:00"
})
@AutoConfigureMockMvc
class AccessTest {
    @Autowired MockMvc mvc;
    @Autowired PasswordEncoder passwords;
    @Autowired JwtEncoder encoder;
    @MockitoBean JdbcTemplate db;
    private String token(String role,String id,Instant expires) {
        var claims=JwtClaimsSet.builder().issuer(SecurityConfig.ISSUER).subject("test").issuedAt(Instant.now().minusSeconds(120))
            .expiresAt(expires).claim("ruolo",role);
        if(id!=null) claims.claim("idEspositore",id);
        return encoder.encode(JwtEncoderParameters.from(JwsHeader.with(MacAlgorithm.HS256).build(),claims.build())).getTokenValue();
    }
    private String token(String role,String id) { return token(role,id,Instant.now().plusSeconds(3600)); }
    @Test void anonymousAndExpiredTokensAreRejected() throws Exception {
        mvc.perform(get("/affluenza/padiglioni")).andExpect(status().isUnauthorized()).andExpect(jsonPath("$.status").value(401));
        mvc.perform(get("/affluenza/padiglioni").header("Authorization","Bearer "+token("STAFF",null,Instant.now().minusSeconds(90)))).andExpect(status().isUnauthorized());
        mvc.perform(get("/affluenza/padiglioni").header("Authorization","Bearer invalid")).andExpect(status().isUnauthorized());
        verifyNoInteractions(db);
    }
    @Test void rolesAreEnforcedBeforeQueryingDatabase() throws Exception {
        mvc.perform(get("/affluenza/padiglioni").header("Authorization","Bearer "+token("ESPOSITORE","ESP001"))).andExpect(status().isForbidden());
        mvc.perform(get("/espositore/me/visite?edizione=2025").header("Authorization","Bearer "+token("STAFF",null))).andExpect(status().isForbidden());
        verifyNoInteractions(db);
    }
    @Test void exhibitorIdentityAlwaysComesFromSignedToken() throws Exception {
        String query="SELECT edizione,codice_stand,giorno,ora,scansioni FROM arcade.v_espositore_visite_ora WHERE id_espositore = ? AND edizione = ? ORDER BY giorno,ora,codice_stand";
        when(db.query(eq(query),eq(DataController.ROW),eq("ESP001"),eq(2025))).thenReturn(List.of(Map.of("codiceStand","P1-A01","scansioni",7)));
        when(db.query(eq(query),eq(DataController.ROW),eq("ESP002"),eq(2025))).thenReturn(List.of(Map.of("codiceStand","P2-B01","scansioni",3)));
        mvc.perform(get("/espositore/me/visite?edizione=2025&idEspositore=ESP002").header("Authorization","Bearer "+token("ESPOSITORE","ESP001")))
            .andExpect(status().isOk()).andExpect(jsonPath("$[0].codiceStand").value("P1-A01"));
        mvc.perform(get("/espositore/me/visite?edizione=2025").header("Authorization","Bearer "+token("ESPOSITORE","ESP002")))
            .andExpect(status().isOk()).andExpect(jsonPath("$[0].codiceStand").value("P2-B01"));
        verify(db).query(eq(query),eq(DataController.ROW),eq("ESP001"),eq(2025));
        verify(db).query(eq(query),eq(DataController.ROW),eq("ESP002"),eq(2025));
    }
    @Test void invalidEditionAndMissingIdentityAreRejected() throws Exception {
        mvc.perform(get("/espositore/me/visite?edizione=2030").header("Authorization","Bearer "+token("ESPOSITORE","ESP001"))).andExpect(status().isBadRequest());
        mvc.perform(get("/espositore/me/visite?edizione=2025").header("Authorization","Bearer "+token("ESPOSITORE",null))).andExpect(status().isForbidden());
        verifyNoInteractions(db);
    }
    @Test void loginChecksBcryptAndIssuesVerifiableJwt() throws Exception {
        when(db.queryForList("SELECT id, password_hash, ruolo, id_espositore FROM arcade.utente WHERE username = ?","staff"))
            .thenReturn(List.of(Map.of("id",1,"password_hash",passwords.encode("correct-password"),"ruolo","STAFF")));
        mvc.perform(post("/auth/login").contentType("application/json").content("{\"username\":\"staff\",\"password\":\"wrong\"}"))
            .andExpect(status().isUnauthorized());
        mvc.perform(post("/auth/login").contentType("application/json").content("{\"username\":\"staff\",\"password\":\"correct-password\"}"))
            .andExpect(status().isOk()).andExpect(jsonPath("$.accessToken").isString()).andExpect(jsonPath("$.ruolo").value("STAFF")).andExpect(jsonPath("$.idEspositore").doesNotExist());
        mvc.perform(post("/auth/login").contentType("application/json").content("{}"))
            .andExpect(status().isBadRequest());
    }
}
