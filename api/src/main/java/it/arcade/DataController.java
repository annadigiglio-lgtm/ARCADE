package it.arcade;

import java.sql.*;
import java.time.*;
import java.util.*;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.jdbc.core.RowMapper;
import org.springframework.security.core.annotation.AuthenticationPrincipal;
import org.springframework.security.oauth2.jwt.Jwt;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.server.ResponseStatusException;

@RestController
class DataController {
    private final JdbcTemplate db;
    private final OffsetDateTime demoInstant;
    DataController(JdbcTemplate db,@Value("${arcade.demo.istante}") String demoInstant) {
        this.db=db; this.demoInstant="live".equals(demoInstant) ? null : OffsetDateTime.parse(demoInstant);
    }
    // The names are constants, never supplied by a request. All values are bound parameters.
    @GetMapping("/affluenza/padiglioni") List<Map<String,Object>> presenze() { return at("presenze_al"); }
    @GetMapping("/affluenza/andamento") List<Map<String,Object>> andamento() { return at("andamento_al"); }
    @GetMapping("/affluenza/ingressi") List<Map<String,Object>> ingressi() { return at("ingressi_al"); }
    @GetMapping("/affluenza/giornata") Map<String,Object> giornata() {
        var rows=at("giornata_al");
        if(rows.isEmpty()) throw new ResponseStatusException(HttpStatus.NOT_FOUND,"Giornata non disponibile");
        return rows.getFirst();
    }
    private List<Map<String,Object>> at(String function) {
        var instant=demoInstant==null ? OffsetDateTime.now(ZoneId.of("Europe/Rome")) : demoInstant;
        return db.query("SELECT * FROM arcade."+function+"(?)",ROW,instant);
    }
    @GetMapping("/espositore/me/visite")
    List<Map<String,Object>> visite(@AuthenticationPrincipal Jwt jwt,@RequestParam int edizione) {
        checkEdition(edizione);
        return db.query("SELECT edizione,codice_stand,giorno,ora,scansioni FROM arcade.v_espositore_visite_ora WHERE id_espositore = ? AND edizione = ? ORDER BY giorno,ora,codice_stand",ROW,exhibitor(jwt),edizione);
    }
    @GetMapping("/espositore/me/riepilogo")
    Map<String,Object> riepilogo(@AuthenticationPrincipal Jwt jwt,@RequestParam int edizione) {
        checkEdition(edizione);
        var rows=db.query("SELECT * FROM arcade.v_espositore_riepilogo WHERE id_espositore = ? AND edizione = ?",ROW,exhibitor(jwt),edizione);
        if(rows.isEmpty()) throw new ResponseStatusException(HttpStatus.NOT_FOUND,"Nessun risultato per questa edizione");
        return rows.getFirst();
    }
    private static String exhibitor(Jwt jwt) {
        String id=jwt.getClaimAsString("idEspositore");
        if(id==null || id.isBlank()) throw new ResponseStatusException(HttpStatus.FORBIDDEN,"Account espositore non valido");
        return id;
    }
    private static void checkEdition(int edition) {
        if(edition<2024 || edition>2026) throw new ResponseStatusException(HttpStatus.BAD_REQUEST,"Edizione non valida");
    }
    static final RowMapper<Map<String,Object>> ROW=(rs,index) -> {
        Map<String,Object> row=new LinkedHashMap<>();
        var meta=rs.getMetaData();
        for(int i=1;i<=meta.getColumnCount();i++) {
            String name=meta.getColumnLabel(i);
            if("id_espositore".equals(name)) continue;
            StringBuilder key=new StringBuilder(); boolean upper=false;
            for(char c:name.toCharArray()) { if(c=='_') upper=true; else { key.append(upper?Character.toUpperCase(c):c); upper=false; } }
            Object value;
            if(meta.getColumnType(i)==Types.TIMESTAMP_WITH_TIMEZONE) value=rs.getObject(i,OffsetDateTime.class);
            else if(meta.getColumnType(i)==Types.DATE) value=rs.getObject(i,LocalDate.class);
            else value=rs.getObject(i);
            row.put(key.toString(),value);
        }
        return row;
    };
}
