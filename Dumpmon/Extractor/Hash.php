<?php

namespace Dumpmon\Extractor;

class Hash extends Extractor
{
    public function analyze()
    {
        $data  = '';

        $data .= $this->extractPhpassGen()."\n";
        $data .= $this->extractMd5()."\n";
        $data .= $this->extractCrypt()."\n";

        $this->extracted = $data;
    }

    protected function extractPhpassGen()
    {
        $this->matches = array();

        $this->data = preg_replace_callback('/(\$P\$.{31})/im', array($this, 'replaceMatches'), $this->data);

        return implode("\n", $this->matches);
    }

    protected function extractMd5()
    {
        $this->matches = array();

        $this->data = preg_replace_callback('/([a-f0-9]{32})/im', array($this, 'replaceMatches'), $this->data);

        return implode("\n", $this->matches);
    }

    protected function extractCrypt()
    {
        $this->matches = array();

        $this->data = preg_replace_callback('/([a-z0-9\/\.]{13})[,\s\n]?$/im', array($this, 'replaceMatches'), $this->data);

        return implode("\n", $this->matches);
    }
}