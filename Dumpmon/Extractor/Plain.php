<?php

namespace Dumpmon\Extractor;

class Plain extends Extractor
{
    protected $emailRegex = "[a-z0-9\-\._]+@[a-z0-9\-\.]+\.[a-z]{2,4}";

    public function analyze()
    {
        $data  = '';

        $data .= $this->extractUrlWithPwd()."\n";
        $data .= $this->extractEmailPwd()."\n";
        $data .= $this->extractPwdEmails();
        $data .= $this->extractUsernamePwd()."\n";

        $this->extracted = $data;
    }

    protected function extractEmailPwd()
    {
        $this->matches = array();

        $this->data = preg_replace_callback('/^"?'.$this->emailRegex."\s?[\/|;|:|\||,|".'\t'."]\s?(.*?)[:".'\n"'."]/im", array($this, 'replaceMatches'), $this->data);

        return implode("\n", $this->matches);
    }

    /**
     * Detects lists of username:password
     */
    protected function extractUsernamePwd()
    {
        $this->matches = array();

        $this->data = preg_replace_callback('/^[a-z0-9\-]{5,15}:(.*?)$/im', array($this, 'replaceMatches'), $this->data);

        return implode("\n", $this->matches);
    }

    protected function extractUrlWithPwd()
    {
        $this->matches = array();

        $this->data = preg_replace_callback('/[ht|f]tp[s]*:\/\/\w+\:(.*)\@\w*\.\w*/', array($this, 'replaceMatches'), $this->data);

        return implode("\n", $this->matches);
    }

    protected function extractPwdEmails()
    {
        $this->matches = array();

        $this->data = preg_replace_callback("/(?:.*?:)?(.*?)[\s|\/|;|:|\||,|".'\t'."]".$this->emailRegex."\s*?$/im", array($this, 'replaceMatches'), $this->data);

        return implode("\n", $this->matches);
    }
}